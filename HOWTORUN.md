# How to Run

## Getting Started

### Prerequisites

- Python 3.x
- PostgreSQL
- Redis
- Node.js and npm
- A Reddit account and API credentials.

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
    **Note:** If you are on Windows, you will need to install Redis from the official website: https://redis.io/docs/getting-started/installation/install-redis-on-windows/

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
