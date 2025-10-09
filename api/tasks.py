from celery import Celery
from .config import Config
from . import analysis_engine
from . import hybrid_analysis
from .database import db_session, AnalysisResult
import datetime

# Create a Celery application instance.
# We configure it with the broker and backend URLs from our config file.
celery_app = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)

@celery_app.task(bind=True)
def run_full_analysis(self, ticker_symbol):
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
    db = db_session()
    try:
        # --- ARIMA Analysis ---
        # First, run the ARIMA analysis, which is relatively fast.
        self.update_state(state='PROGRESS', meta={'status': 'Fetching stock data...'})
        info, hist = analysis_engine.get_stock_data(ticker_symbol)
        if info is None:
            raise ValueError(f"Could not fetch data for {ticker_symbol.upper()}.")
        
        self.update_state(state='PROGRESS', meta={'status': 'Calculating technical indicators...'})
        hist = analysis_engine.calculate_technical_indicators(hist)
        self.update_state(state='PROGRESS', meta={'status': 'Generating ARIMA forecast...'})
        forecast, forecast_dates = analysis_engine.forecast_stock_price(hist)
        if forecast.empty:
            raise ValueError(f"Could not generate a forecast for {ticker_symbol.upper()}.")

        # Create the initial plot without any sentiment adjustment.
        self.update_state(state='PROGRESS', meta={'status': 'Creating initial plot...'})
        initial_plot_html = analysis_engine.create_plot(hist, forecast, forecast_dates, ticker_symbol)

        # --- Database Update (Part 1) ---
        # Store the initial ARIMA plot in the database immediately.
        # This provides a fast initial result to the user while the slower sentiment analysis runs.
        self.update_state(state='PROGRESS', meta={'status': 'Saving initial results...'})
        result = db.query(AnalysisResult).filter(AnalysisResult.ticker == ticker_symbol).first()
        if not result:
            result = AnalysisResult(ticker=ticker_symbol)
            db.add(result)
        
        result.arima_plot = initial_plot_html
        result.last_updated = datetime.datetime.utcnow()
        db.commit()

        # --- Reddit Sentiment Analysis ---
        # Now, run the slower Reddit sentiment analysis.
        self.update_state(state='PROGRESS', meta={'status': 'Analyzing Reddit sentiment...'})
        sentiment, posts, reddit_error = analysis_engine.get_reddit_sentiment(ticker_symbol)
        if reddit_error:
            # If Reddit analysis fails, we still have the ARIMA plot, so it's not a complete failure.
            # We can return an error message to be displayed to the user.
            raise ValueError(reddit_error)

        # --- Sentiment Adjustment ---
        # Adjust the forecast based on the sentiment score.
        # This is a simple linear adjustment, but it can be effective.
        self.update_state(state='PROGRESS', meta={'status': 'Adjusting forecast with sentiment...'})
        if sentiment > 0.1:
            adjustment = 1 + (sentiment * 0.5)
            forecast = forecast * adjustment
        elif sentiment < -0.1:
            adjustment = 1 + (sentiment * 0.5)
            forecast = forecast * adjustment
        
        # Create the final, sentiment-adjusted plot.
        self.update_state(state='PROGRESS', meta={'status': 'Creating final plot...'})
        final_plot_html = analysis_engine.create_plot(hist, forecast, forecast_dates, ticker_symbol)

        # --- Database Update (Part 2) ---
        # Update the database with the final, sentiment-adjusted results.
        self.update_state(state='PROGRESS', meta={'status': 'Saving final results...'})
        result.arima_plot = final_plot_html
        result.sentiment = sentiment
        result.sentiment_posts = str(posts) # Convert the list of posts to a string for database storage
        result.last_updated = datetime.datetime.utcnow()
        db.commit()

        # Return a success message.
        return {'status': 'complete', 'ticker': ticker_symbol}
    except Exception as e:
        self.update_state(state='FAILURE', meta={'status': str(e)})
        return {'status': 'failure', 'error': str(e)}
    finally:
        # Ensure the database session is always closed to prevent connection leaks.
        db_session.remove()

@celery_app.task(bind=True)
def run_hybrid_analysis_task(self, ticker_symbol):
    db = db_session()
    try:
        # --- Get Base Analysis Data ---
        self.update_state(state='PROGRESS', meta={'status': 'Fetching stock data...'})
        info, hist = analysis_engine.get_stock_data(ticker_symbol)
        if info is None:
            raise ValueError(f"Could not fetch data for {ticker_symbol.upper()}.")

        # --- Run Individual Models ---
        self.update_state(state='PROGRESS', meta={'status': 'Generating ARIMA forecast...'})
        arima_forecast, forecast_dates = analysis_engine.forecast_stock_price(hist)
        self.update_state(state='PROGRESS', meta={'status': 'Generating LSTM forecast...'})
        lstm_forecast = hybrid_analysis.forecast_with_lstm(hist)
        self.update_state(state='PROGRESS', meta={'status': 'Analyzing FinBERT sentiment...'})
        _, posts, _ = analysis_engine.get_reddit_sentiment(ticker_symbol)
        finbert_sentiment = hybrid_analysis.get_finbert_sentiment(posts)

        # --- Run Ensemble Prediction ---
        self.update_state(state='PROGRESS', meta={'status': 'Running ensemble prediction...'})
        ensemble_forecast = hybrid_analysis.run_ensemble_prediction(arima_forecast, lstm_forecast, finbert_sentiment)

        # --- Create Plot ---
        self.update_state(state='PROGRESS', meta={'status': 'Creating hybrid plot...'})
        hybrid_plot_html = analysis_engine.create_plot(hist, ensemble_forecast, forecast_dates, ticker_symbol)

        # --- Database Update ---
        self.update_state(state='PROGRESS', meta={'status': 'Saving hybrid results...'})
        result = db.query(AnalysisResult).filter(AnalysisResult.ticker == ticker_symbol).first()
        if not result:
            result = AnalysisResult(ticker=ticker_symbol)
            db.add(result)
        
        result.hybrid_plot = hybrid_plot_html
        result.last_updated = datetime.datetime.utcnow()
        db.commit()

        return {'status': 'complete', 'ticker': ticker_symbol}
    except Exception as e:
        self.update_state(state='FAILURE', meta={'status': str(e)})
        return {'status': 'failure', 'error': str(e)}
    finally:
        db_session.remove()