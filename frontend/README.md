# Pre-Stocked Frontend

This document provides a detailed overview of the React frontend for the Pre-Stocked application.

## Overview

The frontend is a **Single Page Application (SPA)** built with [React](https://reactjs.org/) and bootstrapped with [Create React App](https://github.com/facebook/create-react-app). It provides a user interface for entering a stock ticker, selecting an analysis type, and viewing the results.

## Running the Frontend in Development

For professional development, it is recommended to run the frontend and backend servers separately. This allows you to take advantage of React's **hot-reloading** feature, where changes to the frontend code are instantly visible in the browser without a full page refresh.

1.  **Start the Backend:** In one terminal, start the Flask server and the Celery worker as described in the main project `README.md`.

2.  **Start the Frontend:** In a second terminal, navigate to the `frontend` directory and run:
    ```bash
    npm start
    ```

3.  **View the App:** A new browser tab will automatically open to `http://localhost:3000`. You can now make changes to the frontend code in the `src` directory, and they will be reflected live in the browser.

### How API Requests Work in Development

This project is configured to proxy API requests from the React development server (on port 3000) to the Flask backend server (on port 5000). This is handled by the `"proxy": "http://localhost:5000"` setting in `package.json`. This avoids Cross-Origin Resource Sharing (CORS) errors during development.

## Project Structure

The frontend code is organized into a component-based architecture:

*   **`public/`**: Contains the main `index.html` shell for the application.
*   **`src/`**: Contains all the React source code.
    *   **`App.js`**: The main container component. It manages the application's state and the logic for communicating with the backend API.
    *   **`index.js`**: The entry point for the React application.
    *   **`App.css` & `index.css`**: CSS files for styling the application.
    *   **`components/`**: This directory contains reusable UI components.
        *   **`AnalysisForm.js`**: The form where the user enters the stock ticker and chooses the analysis type.
        *   **`ResultsDisplay.js`**: The component responsible for rendering the Plotly chart and other analysis results.
        *   **`LoadingSpinner.js`**: A simple loading indicator that is displayed while an analysis is in progress.
        *   **`ErrorMessage.js`**: Displays specific error messages received from the backend.

## State Management and Data Flow

The application uses React's built-in state management (`useState` and `useEffect` hooks) to manage its data flow.

1.  **State:** The main state is held in the `App.js` component:
    *   `ticker`: The stock ticker entered by the user.
    *   `analysis`: The analysis results received from the backend.
    *   `loading`: A boolean flag to indicate when an analysis is in progress.
    *   `error`: A string to hold any error messages.

2.  **Data Flow:**
    *   The user enters a ticker in the `AnalysisForm` component.
    *   When the form is submitted, the `handleSubmit` function in `App.js` is called.
    *   `App.js` sends a request to the backend `/analyze` endpoint and receives a `task_id`.
    *   `App.js` then polls the `/status/<task_id>` endpoint. During this time, the `loading` state is true, and the `LoadingSpinner` is displayed.
    *   If the backend task fails, the specific error message is received and stored in the `error` state, and the `ErrorMessage` component is displayed.
    *   If the task succeeds, `App.js` fetches the final results from the `/data` or `/hybrid_data` endpoint and stores them in the `analysis` state.
    *   The `ResultsDisplay` component receives the `analysis` data as a prop and renders the results.

---

(The default Create React App documentation follows...)