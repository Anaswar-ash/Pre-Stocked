from celery import Celery

from . import analysis_engine, hybrid_analysis
from .config import Config
from .database import db_session
from .exceptions import AnalysisError, RedditAPIError, StockDataError

# Create a Celery application instance.
# We configure it with the broker and backend URLs from our config file.
celery_app = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)


@celery_app.task(bind=True)
        _info, hist = analysis_engine.get_stock_data(ticker_symbol)

        self.update_state(state="PROGRESS", meta={"status": "Calculating technical indicators..."})
        hist = analysis_engine.calculate_technical_indicators(hist)

        self.update_state(state="PROGRESS", meta={"status": "Generating ARIMA forecast..."})
        forecast, forecast_dates = analysis_engine.forecast_stock_price(hist)

        # ... (database update)

        self.update_state(state="PROGRESS", meta={"status": "Analyzing Reddit sentiment..."})
        sentiment, posts, _ = analysis_engine.get_reddit_sentiment(ticker_symbol)

        # ... (sentiment adjustment and final plot)

        return {"status": "complete", "ticker": ticker_symbol}
    except (StockDataError, RedditAPIError, AnalysisError) as e:
        self.update_state(state="FAILURE", meta={"status": str(e)})
        return {"status": "failure", "error": str(e)}
    except Exception:
        # Catch any other unexpected errors
        self.update_state(state="FAILURE", meta={"status": "An unexpected error occurred."})
        return {"status": "failure", "error": "An unexpected error occurred."}
    finally:
        db_session.remove()


@celery_app.task(bind=True)
def run_hybrid_analysis_task(self, ticker_symbol):
    """Celery task to run the hybrid stock analysis..."""
    db_session()
    try:
        # ... (analysis steps)
        self.update_state(state="PROGRESS", meta={"status": "Fetching stock data..."})
        info, hist = analysis_engine.get_stock_data(ticker_symbol)

        self.update_state(state="PROGRESS", meta={"status": "Generating ARIMA forecast..."})
        arima_forecast, forecast_dates = analysis_engine.forecast_stock_price(hist)

        self.update_state(state="PROGRESS", meta={"status": "Generating LSTM forecast..."})
        hybrid_analysis.forecast_with_lstm(hist)

        self.update_state(state="PROGRESS", meta={"status": "Analyzing FinBERT sentiment..."})
        _, posts, _ = analysis_engine.get_reddit_sentiment(ticker_symbol)
        hybrid_analysis.get_finbert_sentiment(posts)

        # ... (ensemble prediction and plot)

        return {"status": "complete", "ticker": ticker_symbol}
    except (StockDataError, RedditAPIError, AnalysisError) as e:
        self.update_state(state="FAILURE", meta={"status": str(e)})
        return {"status": "failure", "error": str(e)}
    except Exception:
        # Catch any other unexpected errors
        self.update_state(state="FAILURE", meta={"status": "An unexpected error occurred during hybrid analysis."})
        return {"status": "failure", "error": "An unexpected error occurred during hybrid analysis."}
    finally:
        db_session.remove()
