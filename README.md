# Pre-Stocked: A Stock Analysis & Forecasting Tool

**Author:** Ash.

Pre-Stocked is a web-based application that provides in-depth stock analysis by combining time-series forecasting with Reddit sentiment analysis. It is built with a robust backend that uses asynchronous tasks to ensure a non-blocking user experience.

## Features

*   **Interactive Candlestick Charts:** Visualizes historical stock data with 50-day and 200-day Simple Moving Averages (SMAs).
*   **Two Analysis Modes:**
    *   **Simple Analysis:** Generates a 30-day stock price forecast using an ARIMA model and adjusts it based on Reddit sentiment analyzed with VADER.
    *   **Hybrid Analysis:** A more advanced analysis that combines ARIMA and a Long Short-Term Memory (LSTM) neural network for forecasting, with sentiment analysis powered by FinBERT, a language model specialized for financial text.
*   **Asynchronous Analysis:** Heavy-duty analysis tasks are run in the background using Celery and Redis, so the UI remains responsive.
*   **Database Caching:** Caches analysis results in a PostgreSQL database to provide instant results for recent queries.

## Technologies Used

*   **Backend:** Python, Flask, Celery, Redis, PostgreSQL
*   **Frontend:** React, JavaScript
*   **Data Science:** Pandas, NumPy, Scikit-learn, Statsmodels, TensorFlow, Keras, NLTK, FinBERT
*   **APIs:** Yahoo Finance (yfinance), Reddit (PRAW)

## Project Structure

```
Pre-Stocked/
├── api/            # Backend Flask application
│   ├── tasks/      # Celery tasks for async analysis
│   ├── models.py   # Database models
│   └── ...
├── frontend/       # Frontend React application
│   ├── src/
│   └── ...
├── tests/          # Tests for the backend
├── .gitignore
├── HOWTORUN.md
├── pyproject.toml
├── README.md
├── requirements.txt
└── run.py          # Main script to run the application
```

## System Architecture

The application is built on a modern, asynchronous architecture designed for responsiveness and scalability. It consists of the following key components:

1.  **Flask Web Application (`api/__init__.py`):** A lightweight web server that handles user requests, manages the analysis workflow, and serves the frontend.
2.  **Celery Distributed Task Queue (`api/tasks.py`):** Heavy computational tasks are offloaded to a Celery worker to run asynchronously.
3.  **Redis Message Broker:** Used as the message broker for Celery.
4.  **PostgreSQL Database (`api/database.py`):** Caches analysis results to provide instant results for recent queries.
5.  **Analysis Engine (`api/analysis_engine.py`):** Contains the core logic for stock data analysis, including data fetching, technical indicators, and ARIMA forecasting.
6.  **Hybrid Analysis Module (`api/hybrid_analysis.py`):** Contains the logic for the advanced hybrid analysis, including the LSTM model and FinBERT sentiment analysis.

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

## Program Flow

1.  **User Interaction (Frontend):**
    *   The user interacts with the `AnalysisForm` component to enter a stock ticker and choose an analysis type.
    *   On submission, a `POST` request is sent to the `/analyze` endpoint.

2.  **Backend Request Handling (Flask):
    *   The `/analyze` route starts a Celery background task (`run_full_analysis` or `run_hybrid_analysis_task`).
    *   It returns a `task_id` to the frontend.

3.  **Frontend Polling:**
    *   The frontend polls the `/status/<task_id>` endpoint every 5 seconds.

4.  **Asynchronous Analysis (Celery):
    *   The Celery worker executes the task.
    *   **Error Handling:** If an error occurs (e.g., invalid ticker, Reddit API failure), the task raises a custom exception (`StockDataError`, `RedditAPIError`, etc.). The task's state is set to `FAILURE`, and the error message is stored.
    *   If successful, the results are stored in the PostgreSQL database.

5.  **Backend Task Status:**
    *   The `/status/<task_id>` route returns the task's state.
    *   If the state is `FAILURE`, it returns the specific error message.

6.  **Frontend Display:**
    *   If the frontend receives a `FAILURE` state, it displays the specific error message to the user using the `ErrorMessage` component.
    *   If the task is `SUCCESS`ful, the frontend fetches the data from `/data/<ticker>` or `/hybrid_data/<ticker>` and displays it using the `ResultsDisplay` component.

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

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for details.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Disclaimer

This is not financial advice. All data and analysis are for informational purposes only.
