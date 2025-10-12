import praw
import logging
from ..config import Config
from ..exceptions import RedditAPIError
from ..analysis.sentiment import get_sentiment_compound_score, classify_sentiment

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

POST_LIMIT = 25  # Number of posts to fetch from Reddit
COMMENT_LIMIT = 10  # Number of top comments per post to fetch

def get_reddit_client():
    """Creates and returns an authenticated PRAW Reddit client."""
    try:
        reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.RED_USER_AGENT or "SentimentAnalysisWebApp/0.1 by YourUsername",
        )
        if not reddit.read_only:
            raise RedditAPIError("Reddit credentials are not valid. Please check your .env file.")
        return reddit
    except Exception as e:
        logging.error(f"Error initializing PRAW: {e}")
        raise RedditAPIError("Could not connect to Reddit. Please check your API credentials and network connection.") from e

def get_reddit_sentiment(ticker_symbol):
    """
    Fetches and analyzes Reddit sentiment for a given stock ticker.
    """
    reddit = get_reddit_client()
    weighted_scores = []
    analyzed_posts = []

    try:
        subreddit = reddit.subreddit("all")
        submissions = subreddit.search(ticker_symbol, limit=POST_LIMIT)

        for post in submissions:
            title_score = get_sentiment_compound_score(post.title)
            body_score = get_sentiment_compound_score(post.selftext)

            post_weight = post.score + 1
            weighted_scores.append({'score': title_score, 'weight': post_weight})
            if post.selftext:
                weighted_scores.append({'score': body_score, 'weight': post_weight})

            post_comments = []
            post.comments.replace_more(limit=0)

            comment_list = post.comments.list()

            for comment in comment_list[:COMMENT_LIMIT]:
                comment_score = get_sentiment_compound_score(comment.body)
                comment_weight = comment.score + 1
                weighted_scores.append({'score': comment_score, 'weight': comment_weight})
                post_comments.append({
                    'body': comment.body,
                    'author': comment.author.name if comment.author else "[deleted]",
                    'score': comment.score,
                    'sentiment': classify_sentiment(comment_score)
                })

            analyzed_posts.append({
                'title': post.title,
                'url': post.url,
                'score': post.score,
                'sentiment': classify_sentiment(title_score),
                'comments': post_comments
            })

        if not weighted_scores:
            return 0, [], f"No results found for '{ticker_symbol}'."

        total_weight = sum(item['weight'] for item in weighted_scores)
        weighted_sum = sum(item['score'] * item['weight'] for item in weighted_scores)

        final_compound_score = weighted_sum / total_weight if total_weight > 0 else 0

        return final_compound_score, analyzed_posts, None

    except praw.exceptions.PrawcoreException as e:
        logging.error(f"An error occurred during Reddit search: {e}")
        raise RedditAPIError("An error occurred while fetching data from Reddit.") from e
