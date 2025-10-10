# Pre-Stocked Application Setup

This document outlines the steps required to set up and run the Pre-Stocked application.

## 1. Backend Setup

The backend is a Python Flask application.

### Prerequisites

*   Python 3.x installed.
*   `pip` for package management.

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

Once both the backend and frontend are set up, you can start the application.

1.  **Navigate back to the project root directory (if you are in the `frontend` directory):**
    ```bash
    cd ..
    ```
2.  **Run the Flask server:**

    ```bash
    python run.py
    ```

The application will be accessible at `http://127.0.0.1:5000`.
