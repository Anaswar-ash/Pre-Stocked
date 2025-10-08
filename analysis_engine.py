import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import itertools
import os
from dotenv import load_dotenv
import logging

# --- SETUP ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# --- CONSTANTS ---
POST_LIMIT = 25  # Number of posts to fetch from Reddit
COMMENT_LIMIT = 10  # Number of top comments per post to fetch

# --- INITIALIZATION ---
# Initialize the Reddit API client (PRAW)
try:
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("RED_USER_AGENT", "SentimentAnalysisWebApp/0.1 by YourUsername"),
    )
    # Test the connection to ensure credentials are valid
    logging.info(f"Connected to Reddit as: {reddit.user.me()}")
except Exception as e:
    logging.error(f"Error initializing PRAW: {e}")
    reddit = None

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# --- STOCK DATA ---
def get_stock_data(ticker_symbol):
    """
    Fetches historical stock data and company information from Yahoo Finance.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        hist = ticker.history(period="5y")
        if hist.empty:
            logging.warning(f"No historical data found for {ticker_symbol}")
            return None, None
        # Ensure essential data points are present
        if 'longName' not in info or 'symbol' not in info:
            logging.warning(f"Incomplete company information for {ticker_symbol}")
            return None, None
        return info, hist
    except Exception as e:
        logging.error(f"Error fetching stock data for {ticker_symbol}: {e}")
        return None, None

# --- TECHNICAL ANALYSIS ---
def calculate_technical_indicators(df):
    """
    Calculates 50-day and 200-day Simple Moving Averages (SMA).
    """
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    return df

# --- FORECASTING ---
def find_best_arima_order(data):
    """
    Iterates through combinations of p, d, and q to find the best ARIMA model order based on AIC (Akaike Information Criterion).
    A lower AIC indicates a better model fit.
    """
    p = d = q = range(0, 3)  # Define the range of p, d, q values to test
    pdq = list(itertools.product(p, d, q))  # Generate all possible combinations

    best_aic = float("inf")
    best_order = None

    for order in pdq:
        try:
            model = ARIMA(data, order=order)
            model_fit = model.fit()
            if model_fit.aic < best_aic:
                best_aic = model_fit.aic
                best_order = order
        except:
            # If a model fails to fit (e.g., non-invertible), skip it
            continue

    return best_order

def forecast_stock_price(df, days_to_predict=30):
    """
    Forecasts the stock price using the best ARIMA model found.
    """
    try:
        best_order = find_best_arima_order(df['Close'])
        if best_order is None:
            logging.warning("Could not find a suitable ARIMA model. Falling back to default order (5,1,0).")
            best_order = (5, 1, 0)

        model = ARIMA(df['Close'], order=best_order)
        model_fit = model.fit()

        # Generate the forecast for the specified number of days
        forecast = model_fit.forecast(steps=days_to_predict)

        # Create the corresponding date range for the forecast
        forecast_dates = pd.to_datetime(df.index[-1]) + pd.to_timedelta(range(1, days_to_predict + 1), unit='D')

        return forecast, forecast_dates
    except Exception as e:
        logging.error(f"Error during ARIMA forecasting: {e}")
        return pd.Series(), pd.Index([])

# --- SENTIMENT ANALYSIS ---
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

def get_reddit_sentiment(ticker_symbol):
    """
    Fetches and analyzes Reddit sentiment for a given stock ticker using a weighted average.
    The sentiment is weighted by the score (upvotes) of the posts and comments.
    """
    if not reddit:
        return 0, [], "Reddit API not configured. Please check your .env file."

    weighted_scores = []
    analyzed_posts = []

    try:
        # Search for the ticker symbol across all of Reddit
        subreddit = reddit.subreddit("all")
        submissions = subreddit.search(ticker_symbol, limit=POST_LIMIT)

        for post in submissions:
            title_score = get_sentiment_compound_score(post.title)
            body_score = get_sentiment_compound_score(post.selftext)

            # Weight is upvotes + 1 (to avoid zero weight)
            post_weight = post.score + 1
            weighted_scores.append({'score': title_score, 'weight': post_weight})
            if post.selftext:
                weighted_scores.append({'score': body_score, 'weight': post_weight})

            # Analyze the top comments of the post
            post_comments = []
            post.comments.replace_more(limit=0)  # Remove "load more comments" links

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

        # Calculate the final weighted average sentiment
        total_weight = sum(item['weight'] for item in weighted_scores)
        weighted_sum = sum(item['score'] * item['weight'] for item in weighted_scores)

        final_compound_score = weighted_sum / total_weight if total_weight > 0 else 0

        return final_compound_score, analyzed_posts, None

    except Exception as e:
        logging.error(f"An error occurred during search: {e}")
        return 0, [], f"An error occurred while fetching data from Reddit: {e}"

# --- PLOTTING ---
def create_plot(df, forecast, forecast_dates, ticker_symbol):
    """
    Creates an interactive Plotly chart of the stock data and forecast.
    """
    fig = go.Figure()

    # Add traces for historical data and SMAs
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name='50-Day SMA', line=dict(color='yellow', dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], name='200-Day SMA', line=dict(color='red', dash='dash')))

    # Add trace for the forecast
    fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, name='Sentiment-Adjusted Forecast', line=dict(color='green', dash='dot')))

    # Update the layout for a clean, dark theme
    fig.update_layout(
        title=f'{ticker_symbol.upper()} Stock Price Analysis & Forecast',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        xaxis_rangeslider_visible=True
    )

    # Return the plot as an HTML string so it can be embedded in the web page
    return fig.to_html(full_html=False)
