# Pre-Stocked: A Stock Analysis & Forecasting Tool

**Author:** Ash

Pre-Stocked is a web-based application that provides in-depth stock analysis by combining time-series forecasting with Reddit sentiment analysis. It is built with a robust backend that uses asynchronous tasks to ensure a non-blocking user experience.

## Features

*   **Interactive Candlestick Charts:** Visualizes historical stock data with 50-day and 200-day Simple Moving Averages (SMAs).
*   **Two Analysis Modes:**
    *   **Simple Analysis:** Generates a 30-day stock price forecast using an ARIMA model and adjusts it based on Reddit sentiment analyzed with VADER.
    *   **Hybrid Analysis:** A more advanced analysis that combines ARIMA and a Long Short-Term Memory (LSTM) neural network for forecasting, with sentiment analysis powered by FinBERT, a language model specialized for financial text.
*   **Asynchronous Analysis:** Heavy-duty analysis tasks are run in the background using Celery and Redis, so the UI remains responsive.
*   **Database Caching:** Caches analysis results in a PostgreSQL database to provide instant results for recent queries.

## How It Works

1.  **User Input:** The user enters a stock ticker and chooses an analysis type.
2.  **Background Task:** A Celery background task is initiated to perform the analysis.
3.  **Data Fetching:** Historical stock data is fetched from Yahoo Finance and relevant posts from Reddit.
4.  **Forecasting & Sentiment Analysis:** The application uses a combination of models (ARIMA, LSTM, VADER, FinBERT) to forecast future stock prices and analyze sentiment.
5.  **Ensemble/Adjustment:** The forecast is adjusted based on the calculated sentiment score.
6.  **Final Result:** The final forecast is stored in the database and displayed to the user.

## Getting Started

### Prerequisites

*   Python 3.x
*   PostgreSQL
*   Redis
*   Node.js and npm
*   A Reddit account and API credentials.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Pre-Stocked.git
    cd Pre-Stocked
    ```

2.  **Backend Setup:**
    *   Create a virtual environment and activate it.
    *   Install Python dependencies: `pip install -r requirements.txt`
    *   Create a `.env` file in the `api` directory with your credentials (use `.env.example` as a template).

3.  **Frontend Setup:**
    *   Navigate to the `frontend` directory: `cd frontend`
    *   Install npm dependencies: `npm install`
    *   Build the React app: `npm run build`
    *   Navigate back to the root directory: `cd ..`

### Running the Application

You will need to run three processes in separate terminals:

1.  **Start the Redis server:**
    ```bash
    redis-server
    ```

2.  **Start the Celery worker:**

    *   On Windows:
        ```bash
        celery -A api.tasks.celery_app worker -l info -P eventlet
        ```

    *   On macOS and Linux:
        ```bash
        celery -A api.tasks.celery_app worker --loglevel=info
        ```

3.  **Start the Flask server:**

    ```bash
    python run.py
    ```

Open your web browser and navigate to `http://127.0.0.1:5000`.

## Disclaimer

This is not financial advice. All data and analysis are for informational purposes only.
