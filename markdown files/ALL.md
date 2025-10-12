# From: ERROR.md

# Error Log

## 2025-10-10

**Error:** Both simple and hybrid analyses were failing with the message "Analysis failed. Please try again."

**Root Cause:** The application was unable to connect to the Reddit API due to an issue with how the API credentials were being loaded.

**Fix:** Refactored the Reddit client initialization to be on-demand within the analysis functions, ensuring it uses the correct credentials from the application config.

---

## 2025-10-10 (Evening)

**Issue:** The hybrid analysis appears to hang or get stuck, with no terminal output for over 5 minutes.

**Analysis:** This was identified as a performance and feedback issue. The long-running analysis tasks (model download, LSTM training) gave no feedback, making the app appear frozen.

**Next Steps / Recommendations:** Improve user feedback by adding more granular progress updates from the backend and displaying them on the frontend.

---

## 2025-10-10 (Night)

**Issue:** The application would hang indefinitely if an analysis was started while the Celery worker was not running. The user had no way to know if the backend was processing the request or if it was stuck.

**Root Cause:** The frontend polling mechanism had no timeout. It would continue to poll the status of a "PENDING" task forever.

**Fix:** Implemented a timeout mechanism in the `pollTaskStatus` function in `frontend/src/App.js`.

1.  A timer is started when polling begins.
2.  The timeout is set to 3 minutes for simple analysis and 5 minutes for hybrid analysis.
3.  If the task does not complete within this time, the polling stops, and a specific error message is displayed to the user: "Analysis timed out. Please ensure backend services are running and try again."
4.  This provides clear feedback to the user when the Celery worker is down and prevents the application from appearing to be stuck.


---

# From: NOTE.md

# Project Assessment: Pre-Stocked

This project is a well-structured web application for stock analysis that combines time-series forecasting with sentiment analysis.

## Strengths:

*   **Clear Architecture:** The project is well-organized into a Flask backend and a React frontend.
*   **Asynchronous Tasks:** It uses Celery and Redis to run analysis in the background, which keeps the UI responsive.
*   **Component-Based Frontend:** The frontend is broken down into reusable components, which improves maintainability.
*   **Robust Error Handling:** The backend uses custom exceptions to provide specific error messages to the frontend.
*   **Hybrid Analysis:** The application uses a sophisticated approach by combining multiple models (ARIMA, LSTM, FinBERT) for its analysis.
*   **Good Documentation:** The project includes good technical and user-facing documentation.

## Weaknesses:

*   **Lack of Tests:** There is no automated test suite for the application's logic.
*   **UI/UX could be polished:** While functional, the user interface could be improved with a more professional design and user experience.

## Program Flow:

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

---

# From: RUN.md

# Pre-Stocked Application Setup

This document outlines the steps required to set up and run the Pre-Stocked application.

## 1. Backend Setup

The backend is a Python Flask application.

### Prerequisites

*   Python 3.x installed.
*   `pip` for package management.
*   Redis server installed and running.

### Steps

1.  **Create and activate a virtual environment:**

    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

    *   On macOS and Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

2.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your environment variables:**
    Create a `.env` file in the `api` directory and add your credentials. You can use `.env.example` as a template.

## 2. Frontend Setup

The frontend is a React application.

### Prerequisites

*   Node.js and `npm` installed.

### Steps

1.  **Navigate to the frontend directory:**

    ```bash
    cd frontend
    ```

2.  **Install npm dependencies:**

    ```bash
    npm install
    ```

3.  **Build the React app:**

    ```bash
    npm run build
    ```
    This will create an optimized production build in the `frontend/build` directory.

## 3. Running the Application

Once both the backend and frontend are set up, you need to run three processes in separate terminals:

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

The application will be accessible at `http://127.0.0.1:5000`.

---

# From: TECHDOC.md

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

---

# From: PROJECT.md

## PROJECT IDENTITY
- **Name:** Pre-Stocked
- **Core Objective:** To provide in-depth stock analysis by combining time-series forecasting with Reddit sentiment analysis, delivered through a responsive web interface.
- **Target Users:** Retail investors, financial students, and data enthusiasts who want to explore the relationship between market sentiment and stock price movements.
- **Key Note:** The project's core value proposition is the *synthesis* of quantitative financial data (stock prices) with qualitative public sentiment data (Reddit posts). The goal is not just to forecast a price, but to provide a richer context for that forecast.

## TECHNOLOGY STACK - WITH RATIONALE

*(This section details the technology choices and their roles in the application.)*

### FRONTEND:
*   **Framework: React**
    *   **WHY:** React was chosen to create a dynamic Single Page Application (SPA). This approach provides a fluid user experience, as all interactions happen on a single page without requiring full page reloads. Its component-based architecture is ideal for building a modular and maintainable UI, where components like the analysis form and results display can be developed and managed independently.
    *   **HOW:** The frontend is built as a hierarchy of React components, with a central `App.js` component managing the overall application state and orchestrating the UI. When a user submits the analysis form, `App.js` triggers an API call to the backend and then polls for status updates, re-rendering the UI with progress messages, and finally displaying the results without a page refresh.

*   **State Management: React Hooks (`useState`)**
    *   **WHY:** React Hooks were chosen over class-based components and external state management libraries (like Redux) for their simplicity and sufficiency for this project's needs. Hooks allow for managing state and side effects within functional components, resulting in more concise and readable code. Since the application state is largely self-contained within the main `App` component, a global state management solution was deemed unnecessary.
    *   **HOW:** `useState` is used to manage all pieces of state that change over the application's lifecycle, including the form input (`ticker`), the loading status (`loading`), error messages (`error`), real-time progress updates (`progress`), and the final analysis results (`analysis`). Each state variable is updated via its setter function, which triggers a re-render of the component to reflect the new state.

*   **Build Tools: Create React App (react-scripts)**
    *   **WHY:** Create React App was used to bootstrap the project, providing a pre-configured and optimized build environment out of the box. This avoids the significant effort required to manually configure Webpack, Babel, and other build tools, allowing for a faster development start. It also includes a development server with hot-reloading for an efficient development workflow.
    *   **HOW:** The `npm run build` command executes `react-scripts`, which bundles all JavaScript and CSS files, transpiles modern JavaScript for browser compatibility, and optimizes the static assets for production. The output is a `build` directory containing a static site that can be served by the Flask backend.

### BACKEND:
*   **Language/Framework: Python & Flask**
    *   **WHY:** Python is the de facto standard for data science and machine learning, providing access to a rich ecosystem of powerful libraries (e.g., `pandas`, `statsmodels`, `tensorflow`). Flask was chosen because it is a "micro-framework." It provides the bare essentials for building a web application without imposing a rigid structure, giving the developer the flexibility to integrate the data science components and asynchronous task queue in a clean and maintainable way.
    *   **HOW:** Flask is used to create a simple web server that exposes a REST API. It defines routes for starting an analysis (`/analyze`), checking its status (`/status/<task_id>`), and retrieving the results. For the root URL (`/`), it is configured to serve the `index.html` file from the React build, effectively hosting the entire SPA.

*   **API Type: REST**
    *   **WHY:** A RESTful API was chosen for its simplicity, statelessness, and widespread adoption. It is a natural fit for the application's client-server architecture, where the frontend is a distinct client that consumes the backend service. This is simpler to implement and consume than alternatives like GraphQL, which would be overkill for the limited data-fetching requirements of this application.
    *   **HOW:** The API is implemented with clear, resource-oriented endpoints. The frontend uses standard HTTP requests (`POST` to create an analysis task, `GET` to retrieve status or results). The API communicates using JSON, a lightweight and easy-to-parse data format.

### DATABASE:
*   **Primary DB: PostgreSQL**
    *   **WHY:** A relational database like PostgreSQL was chosen to ensure data integrity and to store the structured results of the analyses. The analysis results have a clear and consistent schema (ticker, plot, sentiment score, etc.), which maps well to a relational model. This is preferable to a NoSQL database, where the schema is more flexible but offers fewer guarantees about data consistency.
    *   **HOW:** The application uses SQLAlchemy as an Object-Relational Mapper (ORM), which allows developers to interact with the database using Python objects instead of writing raw SQL queries. The `AnalysisResult` model in `api/database.py` defines the structure of the `analysis_results` table. When an analysis is complete, a new `AnalysisResult` object is created and committed to the database, effectively caching the result.

*   **Caching / Message Broker: Redis**
    *   **WHY:** Redis was chosen for its versatility and high performance. It serves two distinct but critical roles: as a message broker for Celery and as a result backend. Its in-memory nature makes it extremely fast for these tasks, which is essential for a responsive asynchronous system.
    *   **HOW:** As a message broker, Redis holds the queue of analysis tasks that are waiting to be processed. When the Flask app initiates an analysis, it sends a message to a list in Redis. The Celery worker is constantly monitoring this list. As a result backend, Celery stores the state and return value of each task in Redis, allowing the Flask application to query the status of a task by its ID.

### EXTERNAL SERVICES:
*   **Yahoo Finance (via `yfinance` library)**
    *   **WHY:** To obtain historical stock price data, which is the foundation for the time-series forecasting.
    *   **HOW:** The `get_stock_data` function in `api/analysis_engine.py` uses the `yfinance` library to fetch up to 5 years of historical data for a given stock ticker.
    *   **DETAILS:** This is a free service, and the `yfinance` library provides a simple Python interface to it.

*   **Reddit API (via `praw` library)**
    *   **WHY:** To gather textual data (post titles and comments) for sentiment analysis, providing insight into market mood.
    *   **HOW:** The `get_reddit_sentiment` function in `api/analysis_engine.py` uses the `praw` library to connect to the Reddit API and search for posts mentioning the stock ticker.
    *   **DETAILS:** Requires Reddit API credentials (`client_id`, `client_secret`, `user_agent`) to be configured in a `.env` file in the `api` directory.

## PROJECT DETAILS
- **Repo Structure:** The project is organized into a monorepo structure with a clear separation of concerns:
    -   `api/`: Contains the Flask backend.
        -   `__init__.py`: Flask application factory and route definitions.
        -   `tasks.py`: Celery task definitions.
        -   `analysis_engine.py`: Core logic for simple analysis (ARIMA, VADER).
        -   `hybrid_analysis.py`: Logic for hybrid analysis (LSTM, FinBERT).
        -   `database.py`: SQLAlchemy models and database session management.
        -   `exceptions.py`: Custom exception classes for error handling.
    -   `frontend/`: Contains the React frontend application.
        -   `src/App.js`: The main application component.
        -   `src/components/`: Reusable UI components.
    -   `tests/`: Contains the `pytest` test suite for the backend.
    -   `venv/`: The Python virtual environment (not checked into git).

- **Local Setup:**
    1.  **Clone the repository.**
    2.  **Backend Setup:**
        ```bash
        # Create and activate a virtual environment
        python -m venv venv
        source venv/bin/activate
        # Install Python dependencies
        pip install -r requirements.txt
        # Create a .env file in the api/ directory with your credentials
        ```
    3.  **Frontend Setup:**
        ```bash
        cd frontend
        npm install
        npm run build
        cd ..
        ```
    4.  **Run the Application (in three separate terminals):**
        ```bash
        # Terminal 1: Start Redis
        redis-server
        # Terminal 2: Start the Celery worker
        celery -A api.tasks.celery_app worker -l info -P eventlet
        # Terminal 3: Start the Flask server
        python run.py
        ```
    - **Key Note on Local Setup:** For Windows users, the `eventlet` package is required for Celery to function correctly. This is included in `requirements.txt`. The command to start the Celery worker is also platform-specific.

- **Key Environment Variables:** (to be placed in `api/.env`)
    -   `DATABASE_URL`: The connection string for the PostgreSQL database. (e.g., `postgresql://user:password@localhost/prestocked`)
    -   `REDIS_URL`: The URL for the Redis server. (e.g., `redis://localhost:6379/0`)
    -   `REDDIT_CLIENT_ID`: Your Reddit API client ID.
    -   `REDDIT_CLIENT_SECRET`: Your Reddit API client secret.
    -   `RED_USER_AGENT`: Your Reddit API user agent. (e.g., `SentimentWebApp/0.1 by your_reddit_username`)

- **API Endpoints:**
    -   `POST /analyze`
        -   **Purpose:** Initiates an analysis task.
        -   **Request Body:** `{"ticker": "AAPL", "analysis_type": "simple"}`
        -   **Response Body:** `{"task_id": "some-uuid-string"}`
    -   `GET /status/<task_id>`
        -   **Purpose:** Polls the status of an analysis task.
        -   **Response Body (Success):** `{"state": "SUCCESS"}`
        -   **Response Body (In Progress):** `{"state": "PROGRESS", "status": "Generating LSTM forecast..."}`
        -   **Response Body (Failure):** `{"state": "FAILURE", "status": "StockDataError: No historical data found..."}`
    -   `GET /data/<ticker>` & `GET /hybrid_data/<ticker>`
        -   **Purpose:** Fetches the completed analysis results from the database.
        -   **Response Body:** A JSON object containing the plot HTML, sentiment score, and post data.

## ARCHITECTURE DECISIONS
-   **Asynchronous Task Processing (Celery & Redis)**
    *   **WHY:** The core analysis tasks are computationally expensive and would block the web server if run synchronously, leading to request timeouts. Celery allows these tasks to be offloaded to a separate worker process, ensuring the UI remains responsive.
    *   **TRADEOFFS:** This introduces additional complexity and moving parts into the system. It requires running and managing a separate Celery worker process and a Redis server, which increases the operational overhead.
    *   **Key Note:** The communication between the frontend and the asynchronous backend is handled via a polling mechanism. The frontend initiates a task, receives a `task_id`, and then periodically asks the backend for the status of that task. This is a simple and effective pattern for handling long-running background jobs.

-   **Hybrid Forecasting Model (ARIMA + LSTM + Sentiment)**
    *   **WHY:** To create a more robust forecast by combining a traditional statistical model (ARIMA), a deep learning model (LSTM), and market sentiment. This approach, known as an ensemble method, often yields better results than any single model by leveraging their different strengths.
    *   **TRADEOFFS:** This significantly increases the complexity and computational cost of the analysis. The LSTM model, in particular, requires more data and time to train. The logic for combining the models also adds another layer of complexity.
    *   **Key Note:** The FinBERT model used for hybrid sentiment analysis is a large transformer model. The first time a hybrid analysis is run, there will be a significant delay as the model is downloaded from Hugging Face Hub. Subsequent runs will be faster as the model will be cached locally.

## CURRENT STATE
- **Known Issues:**
    -   **UI/UX Polish:** While functional and improved with Bootstrap, the UI could benefit from a more thoughtful design, including better spacing, typography, and a more distinct visual identity.
    -   **Error Handling Granularity:** While custom exceptions are used, the frontend could do a better job of displaying user-friendly error messages for specific failure modes (e.g., "Invalid stock ticker" vs. a generic "Analysis failed").

- **Technical Debt:**
    -   **Test Coverage:** The `hybrid_analysis.py` module, which contains complex logic for the LSTM and ensemble models, currently lacks unit tests. This makes it difficult to refactor or modify this code with confidence.
    -   **Hardcoded Parameters:** Several key parameters (e.g., the number of Reddit posts to fetch, the look-back period for the LSTM model, the weights for the ensemble model) are hardcoded in the source code. These should be extracted into a configuration file to make them easier to tune.
    -   **Lack of Linting/Formatting:** There is no automated linter (like `flake8`) or code formatter (like `black`) configured for the project, which can lead to inconsistent code style.

- **Immediate Next Steps:**
    -   **Enhance Test Suite:** Prioritize writing unit tests for the `hybrid_analysis.py` module, mocking the TensorFlow/Keras and Transformers libraries to isolate the logic.
    -   **Refactor Configuration:** Move hardcoded parameters from the analysis modules into the Flask application's configuration.
    -   **Containerize the Application:** Create a `Dockerfile` for the backend and a `docker-compose.yml` file to orchestrate the entire application stack (Flask, React, Redis, Celery, PostgreSQL). This will simplify the local setup process and prepare the application for deployment.

    
