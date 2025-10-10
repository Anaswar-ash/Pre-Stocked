# Technical Documentation

**Author:** Ash

This document provides a technical overview of the Pre-Stocked application.

## System Architecture

The application is built on a modern, asynchronous architecture designed for responsiveness and scalability. It consists of the following key components:

1.  **Flask Web Application (`api/__init__.py`):** A lightweight web server that handles user requests, manages the analysis workflow, and serves the frontend.
2.  **Celery Distributed Task Queue (`api/tasks.py`):** Heavy computational tasks, such as data analysis and sentiment scoring, are offloaded to a Celery worker to run asynchronously. This prevents the web server from being blocked.
3.  **Redis Message Broker:** Redis is used as the message broker for Celery, facilitating communication between the web application and the Celery workers.
4.  **PostgreSQL Database (`api/database.py`):** A PostgreSQL database is used to cache the results of the analysis. This improves performance by providing near-instant results for recently analyzed stocks.
5.  **Analysis Engine (`api/analysis_engine.py`):** This module contains the core logic for stock data analysis, including data fetching, technical indicator calculation, and ARIMA forecasting.
6.  **Hybrid Analysis Module (`api/hybrid_analysis.py`):** This module contains the logic for the more advanced hybrid analysis, including the LSTM model and FinBERT sentiment analysis.

## Key Libraries and Technologies

*   **Flask:** The web framework used to build the API.
*   **Celery:** A distributed task queue for running background tasks.
*   **Redis:** An in-memory data store used as the Celery message broker and result backend.
*   **eventlet:** A concurrent networking library used as the Celery worker pool on Windows for better stability.
*   **SQLAlchemy:** A SQL toolkit and Object-Relational Mapper (ORM) for interacting with the PostgreSQL database.
*   **psycopg2-binary:** A PostgreSQL adapter for Python.
*   **yfinance:** A library for downloading historical market data from Yahoo Finance.
*   **pandas:** Used for data manipulation and analysis.
*   **statsmodels:** Provides the ARIMA model for time-series forecasting.
*   **scikit-learn:** Used for data preprocessing (e.g., `MinMaxScaler`) before training the LSTM model.
*   **TensorFlow/Keras:** Used to build and train the LSTM neural network.
*   **transformers:** Provides the `pipeline` API to use the pre-trained FinBERT model from Hugging Face.
*   **plotly:** A graphing library for creating interactive charts.
*   **praw:** The Python Reddit API Wrapper, used to fetch data from Reddit.
*   **vaderSentiment:** A lexicon and rule-based sentiment analysis tool used in the simple analysis.
*   **python-dotenv:** Used to manage environment variables.

## Code Structure

### `api/__init__.py`

*   **Routes:** Defines the application's URL endpoints:
    *   `/`: Serves the React frontend.
    *   `/analyze`: Kicks off the analysis by creating a Celery task (`run_full_analysis` or `run_hybrid_analysis_task`).
    *   `/status/<task_id>`: An API endpoint to check the status of a Celery task.
    *   `/data/<ticker>`: An API endpoint to fetch the simple analysis data from the database.
    *   `/hybrid_data/<ticker>`: An API endpoint to fetch the hybrid analysis data from the database.

### `api/tasks.py`

*   **`run_full_analysis`:** A Celery task that orchestrates the simple analysis.
*   **`run_hybrid_analysis_task`:** A Celery task that orchestrates the hybrid analysis.

### `api/analysis_engine.py`

*   **`get_stock_data()`:** Fetches stock data from Yahoo Finance.
*   **`calculate_technical_indicators()`:** Calculates SMAs.
*   **`forecast_stock_price()`:** Implements the ARIMA model.
*   **`get_reddit_sentiment()`:** Fetches and analyzes Reddit sentiment using `vaderSentiment`.
*   **`create_plot()`:** Generates the Plotly chart.
*   **`get_reddit_client()`:** A helper function to create an authenticated PRAW client.

### `api/hybrid_analysis.py`

*   **`create_lstm_model()`:** Creates a simple LSTM model for time-series forecasting.
*   **`forecast_with_lstm()`:** Forecasts stock prices using the LSTM model.
*   **`get_finbert_sentiment()`:** Analyzes sentiment of Reddit posts using FinBERT.
*   **`run_ensemble_prediction()`:** Combines predictions from ARIMA and LSTM, weighted by the FinBERT sentiment score.

## Hybrid Analysis Ensemble Model

The hybrid forecast is an ensemble of the ARIMA and LSTM models, with a sentiment adjustment from FinBERT. The final forecast is a weighted average of the two models, and the sentiment adjustment is applied to both models before combining them.

```python
# From api/hybrid_analysis.py

def run_ensemble_prediction(arima_forecast, lstm_forecast, finbert_sentiment):
    """Combines predictions from multiple models using a weighted average."""
    weights = {
        'arima': 0.4,
        'lstm': 0.4,
        'sentiment': 0.2
    }

    sentiment_adjustment = 1 + (finbert_sentiment * weights['sentiment'])
    adjusted_arima = arima_forecast * sentiment_adjustment
    adjusted_lstm = lstm_forecast * sentiment_adjustment

    ensemble_forecast = (adjusted_arima * weights['arima']) + (adjusted_lstm * weights['lstm'])

    return ensemble_forecast
```