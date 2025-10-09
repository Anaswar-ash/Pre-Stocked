# Pre-Stocked: A Stock Analysis & Forecasting Tool

**Author:** Ash

Pre-Stocked is a web-based application that provides in-depth stock analysis by combining time-series forecasting with Reddit sentiment analysis. It is built with a robust backend that uses asynchronous tasks to ensure a non-blocking user experience.

## Features

*   **Interactive Candlestick Charts:** Visualizes historical stock data with 50-day and 200-day Simple Moving Averages (SMAs).
*   **ARIMA Price Forecasting:** Generates a 30-day stock price forecast using an ARIMA model.
*   **Reddit Sentiment Analysis:** Fetches and analyzes posts from Reddit to determine the market sentiment for a given stock.
*   **Sentiment-Adjusted Forecast:** Adjusts the ARIMA forecast based on the calculated Reddit sentiment.
*   **Asynchronous Analysis:** Heavy-duty analysis tasks are run in the background using Celery and Redis, so the UI remains responsive.
*   **Database Caching:** Caches analysis results in a PostgreSQL database to provide instant results for recent queries.

## How It Works

1.  **User Input:** The user enters a stock ticker into the web interface.
2.  **Background Task:** A Celery background task is initiated to perform the analysis.
3.  **Data Fetching:** Historical stock data is fetched from Yahoo Finance using `yfinance`.
4.  **ARIMA Forecast:** An ARIMA model is used to forecast future stock prices. The initial forecast is cached in the database.
5.  **Reddit Sentiment Analysis:** The application fetches relevant posts from Reddit using the `praw` library and analyzes their sentiment with `vaderSentiment`.
6.  **Sentiment Adjustment:** The initial ARIMA forecast is adjusted based on the calculated sentiment score.
7.  **Final Result:** The final, sentiment-adjusted forecast is stored in the database and displayed to the user.

## Hybrid Analysis

This project also includes a more advanced "hybrid" analysis that combines multiple models for a more robust forecast:

*   **LSTM Forecasting:** A Long Short-Term Memory (LSTM) neural network is used for time-series forecasting, offering a more sophisticated alternative to ARIMA.
*   **FinBERT Sentiment Analysis:** We use FinBERT, a language model specifically pre-trained on financial text, to provide a more nuanced sentiment analysis than the default `vaderSentiment` library.
*   **Ensemble Model:** The final hybrid forecast is an ensemble of the ARIMA and LSTM models, weighted by the FinBERT sentiment score.

## Getting Started

### Prerequisites

*   Python 3.x
*   PostgreSQL
*   Redis
*   A Reddit account and API credentials.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Pre-Stocked.git
    cd Pre-Stocked
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up your environment variables:**
    Create a `.env` file in the `api` directory and add the following, replacing the placeholder values with your actual credentials:
    ```
    FLASK_SECRET_KEY='a_super_secret_key'
    DATABASE_URL='postgresql://user:password@host:port/database'
    REDDIT_CLIENT_ID='your_reddit_client_id'
    REDDIT_CLIENT_SECRET='your_reddit_client_secret'
    RED_USER_AGENT='your_reddit_user_agent'
    CELERY_BROKER_URL='redis://localhost:6379/0'
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
    ```

4.  **Run the database migrations:**
    The database tables will be created automatically when you first run the application.

5.  **Start the services:**
    You will need to run the Flask application, Redis server, and a Celery worker.
    *   **Redis:** `redis-server`
    *   **Celery Worker:** `celery -A api.tasks.celery_app worker --loglevel=info`
    *   **Flask App:** `python run.py`

6.  Open your web browser and navigate to `http://127.0.0.1:5000`.

## Disclaimer

This is not financial advice. All data and analysis are for informational purposes only.