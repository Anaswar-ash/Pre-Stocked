# Project Assessment: Pre-Stocked

This project is a well-structured web application for stock analysis that combines time-series forecasting with sentiment analysis.

## Strengths:

*   **Clear Architecture:** The project is organized into a Flask backend and a React frontend.
*   **Asynchronous Tasks:** It uses Celery and Redis to run analysis in the background, which keeps the UI responsive.
*   **Hybrid Analysis:** The application uses a sophisticated approach by combining multiple models (ARIMA, LSTM, FinBERT) for its analysis.
*   **Good Documentation:** The `README.md` and `TECHDOC.md` files provide a good overview of the project.

## Weaknesses:

*   **Lack of Tests:** There is no test suite for the application's logic, which makes it difficult to maintain and extend.
*   **Basic UI:** The user interface is functional but could be improved.

## Program Flow:

1.  **User Interaction (Frontend):**
    *   User enters a stock ticker and selects an analysis type (simple or hybrid) in the React frontend.
    *   A `POST` request is sent to the `/analyze` endpoint on the Flask backend.

2.  **Backend Request Handling (Flask):**
    *   The `/analyze` route in `api/__init__.py` receives the request.
    *   It validates the ticker and checks for a recent cached result in the PostgreSQL database.
    *   If a fresh cached result exists, it returns a response to the frontend, and the process ends.
    *   If no fresh cache is found, it starts a background task (`run_full_analysis` or `run_hybrid_analysis_task`) using Celery.
    *   It returns a `task_id` to the frontend.

3.  **Frontend Polling:**
    *   The frontend receives the `task_id` and starts polling the `/status/<task_id>` endpoint every 5 seconds.

4.  **Backend Task Status:**
    *   The `/status/<task_id>` route checks the state of the Celery task.
    *   It returns the task's status (`PENDING`, `PROGRESS`, `SUCCESS`, or `FAILURE`) to the frontend.

5.  **Asynchronous Analysis (Celery):**
    *   The Celery worker picks up the task from the Redis message broker.
    *   The task (`run_full_analysis` or `run_hybrid_analysis_task` in `api/tasks.py`) executes the analysis steps:
        *   Fetches stock data from Yahoo Finance.
        *   Calculates technical indicators.
        *   Performs time-series forecasting (ARIMA, LSTM).
        *   Analyzes Reddit sentiment (Vader, FinBERT).
        *   Adjusts the forecast based on sentiment.
        *   Stores the results in the PostgreSQL database.
    *   The task updates its state and progress information, which is accessible via the `/status/<task_id>` endpoint.

6.  **Frontend Data Fetching:**
    *   Once the frontend sees that the task is `SUCCESS`ful, it stops polling.
    *   It then sends a `GET` request to `/data/<ticker>` or `/hybrid_data/<ticker>` to fetch the final analysis data from the database.

7.  **Backend Data Serving:**
    *   The `/data/<ticker>` or `/hybrid_data/<ticker>` route queries the database for the results and returns them as JSON to the frontend.

8.  **Frontend Display:**
    *   The frontend receives the data and displays the Plotly chart, sentiment score, and other analysis results to the user.
