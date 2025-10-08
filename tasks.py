from celery import Celery
from config import Config
import analysis_engine
from database import SessionLocal, AnalysisResult
import datetime

# Create a Celery application instance.
# The first argument is the name of the current module.
# The broker and backend URLs are configured from our Config class.
celery_app = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)

@celery_app.task
def run_full_analysis(ticker_symbol):
    """Celery task to run the full stock analysis and store the results in the database.

    This task is executed asynchronously by a Celery worker.
    It performs the following steps:
    1. Fetches stock data.
    2. Calculates technical indicators.
    3. Generates an ARIMA forecast.
    4. Stores the initial ARIMA plot in the database.
    5. Fetches and analyzes Reddit sentiment.
    6. Adjusts the forecast based on the sentiment.
    7. Updates the database with the final, sentiment-adjusted results.
    """
    # Create a new database session for this task.
    # It's important to create a new session for each task to ensure thread safety.
    db = SessionLocal()
    try:
        # --- ARIMA Analysis ---
        # First, run the ARIMA analysis, which is relatively fast.
        info, hist = analysis_engine.get_stock_data(ticker_symbol)
        if info is None:
            return {'error': f"Could not fetch data for {ticker_symbol.upper()}."}
        
        hist = analysis_engine.calculate_technical_indicators(hist)
        forecast, forecast_dates = analysis_engine.forecast_stock_price(hist)
        if forecast.empty:
            return {'error': f"Could not generate a forecast for {ticker_symbol.upper()}."}

        # Create the initial plot without any sentiment adjustment.
        initial_plot_html = analysis_engine.create_plot(hist, forecast, forecast_dates, ticker_symbol)

        # --- Database Update (Part 1) ---
        # Store the initial ARIMA plot in the database immediately.
        # This provides a fast initial result to the user while the slower sentiment analysis runs.
        result = db.query(AnalysisResult).filter(AnalysisResult.ticker == ticker_symbol).first()
        if not result:
            result = AnalysisResult(ticker=ticker_symbol)
            db.add(result)
        
        result.arima_plot = initial_plot_html
        result.last_updated = datetime.datetime.utcnow()
        db.commit()

        # --- Reddit Sentiment Analysis ---
        # Now, run the slower Reddit sentiment analysis.
        sentiment, posts, reddit_error = analysis_engine.get_reddit_sentiment(ticker_symbol)
        if reddit_error:
            # If Reddit analysis fails, we still have the ARIMA plot, so it's not a complete failure.
            # We can return an error message to be displayed to the user.
            return {'error': reddit_error}

        # --- Sentiment Adjustment ---
        # Adjust the forecast based on the sentiment score.
        # This is a simple linear adjustment, but it can be effective.
        if sentiment > 0.1:
            adjustment = 1 + (sentiment * 0.5)
            forecast = forecast * adjustment
        elif sentiment < -0.1:
            adjustment = 1 + (sentiment * 0.5)
            forecast = forecast * adjustment
        
        # Create the final, sentiment-adjusted plot.
        final_plot_html = analysis_engine.create_plot(hist, forecast, forecast_dates, ticker_symbol)

        # --- Database Update (Part 2) ---
        # Update the database with the final, sentiment-adjusted results.
        result.arima_plot = final_plot_html
        result.sentiment = sentiment
        result.sentiment_posts = str(posts) # Convert the list of posts to a string for database storage
        result.last_updated = datetime.datetime.utcnow()
        db.commit()

        # Return a success message.
        return {'status': 'complete', 'ticker': ticker_symbol}

    finally:
        # Ensure the database session is always closed to prevent connection leaks.
        db.close()