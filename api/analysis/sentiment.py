from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

analyzer = SentimentIntensityAnalyzer()
finbert = pipeline('sentiment-analysis', model='ProsusAI/finbert')

def get_sentiment_compound_score(text):
    """Returns the compound sentiment score from VADER."""
    if not text:
        return 0
    return analyzer.polarity_scores(text)['compound']

def classify_sentiment(compound_score):
    """Classifies a compound score into a sentiment category (Positive, Negative, Neutral)."""
    if compound_score >= 0.05:
        return "Positive"
    elif compound_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def get_finbert_sentiment(posts):
    """Analyzes sentiment of Reddit posts using FinBERT."""
    if not posts or not isinstance(posts, list):
        return 0

    post_titles = [post['title'] for post in posts]
    sentiments = finbert(post_titles)

    score_map = {'positive': 1, 'neutral': 0, 'negative': -1}
    total_score = sum(score_map.get(s['label'], 0) for s in sentiments)

    return total_score / len(sentiments) if sentiments else 0
