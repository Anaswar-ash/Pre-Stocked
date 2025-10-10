# Technical Documentation

**Author:** Ash

This document provides a technical overview of the Pre-Stocked application.

## System Architecture

The application is built on a modern, asynchronous architecture designed for responsiveness and scalability. It consists of the following key components:

1.  **Flask Web Application (`api/__init__.py`):** A lightweight web server that handles user requests, manages the analysis workflow, and serves the frontend.
2.  **Celery Distributed Task Queue (`api/tasks.py`):** Heavy computational tasks are offloaded to a Celery worker to run asynchronously.
3.  **Redis Message Broker:** Used as the message broker for Celery.
4.  **PostgreSQL Database (`api/database.py`):** Caches analysis results to provide instant results for recent queries.
5.  **Analysis Engine (`api/analysis_engine.py`):** Contains the core logic for stock data analysis, including data fetching, technical indicators, and ARIMA forecasting.
6.  **Hybrid Analysis Module (`api/hybrid_analysis.py`):** Contains the logic for the advanced hybrid analysis, including the LSTM model and FinBERT sentiment analysis.

## Key Libraries and Technologies

*   **Flask:** Web framework for the API.
*   **Celery & eventlet:** For background tasks, with `eventlet` for stable performance on Windows.
*   **Redis:** In-memory data store for Celery.
*   **SQLAlchemy & psycopg2-binary:** For interacting with the PostgreSQL database.
*   **yfinance, pandas, statsmodels, scikit-learn, TensorFlow/Keras, transformers:** The core data science and machine learning stack.
*   **plotly:** For interactive charts.
*   **praw & vaderSentiment:** For Reddit data and sentiment analysis.
*   **python-dotenv:** For managing environment variables.

## Error Handling

The application uses a set of custom exception classes defined in `api/exceptions.py` to provide more granular error handling:

*   `StockDataError`: Raised when there is an issue fetching data from Yahoo Finance.
*   `RedditAPIError`: Raised for errors related to the Reddit API (e.g., authentication, connection issues).
*   `AnalysisError`: Raised for general errors during the analysis process (e.g., model fitting).

These exceptions are caught within the Celery tasks (`api/tasks.py`), and the error messages are passed to the frontend to provide specific feedback to the user.

## Code Structure

### Backend (`api/`)

*   **`__init__.py`:** Defines the Flask app and its routes (`/analyze`, `/status/<task_id>`, etc.).
*   **`tasks.py`:** Contains the Celery tasks (`run_full_analysis`, `run_hybrid_analysis_task`) that orchestrate the analysis.
*   **`analysis_engine.py` & `hybrid_analysis.py`:** Contain the core analysis logic.
*   **`exceptions.py`:** Defines the custom exception classes.
*   **`database.py` & `config.py`:** Handle database and application configuration.

### Frontend (`frontend/src/`)

The frontend is built with React and follows a component-based architecture:

*   **`App.js`:** The main container component that manages state and orchestrates the UI.
*   **`components/AnalysisForm.js`:** The form for user input.
*   **`components/ResultsDisplay.js`:** Displays the analysis results.
*   **`components/LoadingSpinner.js`:** A loading indicator shown during analysis.
*   **`components/ErrorMessage.js`:** Displays error messages to the user.

## Hybrid Analysis Ensemble Model

The hybrid forecast is a weighted average of the ARIMA and LSTM models, with a sentiment adjustment from FinBERT.

```python
# From api/hybrid_analysis.py
def run_ensemble_prediction(arima_forecast, lstm_forecast, finbert_sentiment):
    # ... (weighted average logic)
```
