
# Technical Documentation

This document provides a technical overview of the Pre-Stocked application.

## System Architecture

The application is built on a modern, asynchronous architecture designed for responsiveness and scalability. It consists of the following key components:

1.  **Flask Web Application (`app.py`):** A lightweight web server that handles user requests, manages the analysis workflow, and serves the frontend.
2.  **Celery Distributed Task Queue (`tasks.py`):** Heavy computational tasks, such as data analysis and sentiment scoring, are offloaded to a Celery worker to run asynchronously. This prevents the web server from being blocked.
3.  **Redis Message Broker:** Redis is used as the message broker for Celery, facilitating communication between the web application and the Celery workers.
4.  **PostgreSQL Database (`database.py`):** A PostgreSQL database is used to cache the results of the analysis. This improves performance by providing near-instant results for recently analyzed stocks.
5.  **Analysis Engine (`analysis_engine.py`):** This module contains the core logic for stock data analysis, including data fetching, technical indicator calculation, ARIMA forecasting, and Reddit sentiment analysis.

## Key Libraries and Technologies

*   **Flask:** The web framework used to build the user interface.
*   **Celery:** A distributed task queue for running background tasks.
*   **Redis:** An in-memory data store used as the Celery message broker and result backend.
*   **SQLAlchemy:** A SQL toolkit and Object-Relational Mapper (ORM) for interacting with the PostgreSQL database.
*   **psycopg2-binary:** A PostgreSQL adapter for Python.
*   **yfinance:** A library for downloading historical market data from Yahoo Finance.
*   **pandas:** Used for data manipulation and analysis.
*   **statsmodels:** Provides the ARIMA model for time-series forecasting.
*   **plotly:** A graphing library for creating interactive charts.
*   **praw:** The Python Reddit API Wrapper, used to fetch data from Reddit.
*   **vaderSentiment:** A lexicon and rule-based sentiment analysis tool that is specifically attuned to sentiments expressed in social media.
*   **python-dotenv:** Used to manage environment variables and keep sensitive credentials out of the source code.

## Code Structure

### `app.py`

*   **Routes:** Defines the application's URL endpoints:
    *   `/`: The home page.
    *   `/analyze`: Kicks off the analysis by creating a Celery task.
    *   `/result/<ticker>`: The results page, which polls for task completion.
    *   `/status/<task_id>`: An API endpoint to check the status of a Celery task.
    *   `/data/<ticker>`: An API endpoint to fetch the final analysis data from the database.

### `tasks.py`

*   **`run_full_analysis`:** A Celery task that orchestrates the entire analysis process, from fetching data to storing the results in the database.

### `analysis_engine.py`

*   **`get_stock_data()`:** Fetches stock data from Yahoo Finance.
*   **`calculate_technical_indicators()`:** Calculates SMAs.
*   **`forecast_stock_price()`:** Implements the ARIMA model.
*   **`get_reddit_sentiment()`:** Fetches and analyzes Reddit sentiment using `vaderSentiment`.
*   **`create_plot()`:** Generates the Plotly chart.

### `database.py`

*   **`AnalysisResult`:** The SQLAlchemy model for the `analysis_results` table.
*   **`init_db()`:** A function to create the database tables.

### `config.py`

*   **`Config`:** A class that loads all configuration from environment variables.

## Sentiment-Based Forecast Adjustment

The forecast is adjusted using a linear scaling factor based on the compound sentiment score from `vaderSentiment`:

```python
if sentiment > 0.1:
    adjustment = 1 + (sentiment * 0.5)
    forecast = forecast * adjustment
elif sentiment < -0.1:
    adjustment = 1 + (sentiment * 0.5)
    forecast = forecast * adjustment
```

This is a simple but effective model. Future improvements could involve more sophisticated, non-linear adjustment methods.

## Future Improvements

*   **More Advanced Models:** Incorporate more advanced forecasting models (e.g., LSTMs) and sentiment analysis techniques (e.g., using pre-trained language models like BERT).
*   **User Accounts:** Add user accounts to allow users to save and track their favorite stocks.
*   **Real-time Updates:** Use WebSockets to push real-time updates to the frontend, providing a more dynamic user experience.
