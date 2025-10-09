import os
from dotenv import load_dotenv

# Construct the path to the .env file.
# We assume that the .env file is located in the same directory as this config.py file.
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Load environment variables from the specified .env file.
load_dotenv(dotenv_path=dotenv_path)

class Config:
    """Configuration class for the Flask application.

    This class encapsulates the application's configuration variables.
    Loading configuration from environment variables is a best practice because it allows for
    easy changes between different environments (development, testing, production) without
    modifying the code.
    """
    
    # A secret key is required for Flask to manage sessions and other security features.
    # It should be a long, random string to be secure.
    # For production environments, this should always be set as an environment variable.
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_development')
    
    # --- Database Configuration ---
    # The connection URL for the PostgreSQL database.
    # The format is: postgresql://<user>:<password>@<host>:<port>/<database>
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # --- Reddit API Configuration ---
    # These are the credentials for your Reddit application, which are required to access the Reddit API.
    # You can get these by creating a new application on Reddit's developer portal.
    REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
    RED_USER_AGENT = os.environ.get('RED_USER_AGENT')
    
    # --- Celery Configuration ---
    # The URL for the message broker (Redis). Celery uses this to send and receive messages for background tasks.
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    # The URL for the result backend (also Redis). Celery uses this to store the results and status of tasks.
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # --- Cache Configuration ---
    # The time in hours to cache the analysis results.
    CACHE_TIME = int(os.environ.get('CACHE_TIME', 1))