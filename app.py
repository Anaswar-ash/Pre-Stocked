from flask import Flask, render_template, request, jsonify, url_for, redirect
from config import Config
from database import SessionLocal, init_db, AnalysisResult
from tasks import run_full_analysis
import datetime

# Create and configure the Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database by creating tables if they don't exist
# This is called once when the application starts.
init_db()

@app.route('/')
def index():
    """Renders the home page of the application."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handles the form submission for stock analysis.

    This route is triggered when the user submits the stock ticker.
    It validates the ticker, checks for a recent cached result in the database,
    and if no fresh result is found, it starts a new background analysis task.
    """
    ticker = request.form.get('ticker').upper()
    if not ticker or not ticker.isalnum() or not 2 <= len(ticker) <= 5:
        return render_template('index.html', error="Invalid ticker symbol.")

    db = SessionLocal()
    try:
        # Check for a recent cached result (e.g., within the last hour)
        # This helps to reduce redundant analyses and provide faster responses.
        cache_time_limit = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        cached_result = db.query(AnalysisResult).filter(
            AnalysisResult.ticker == ticker,
            AnalysisResult.last_updated > cache_time_limit
        ).first()

        if cached_result and cached_result.arima_plot:
            # If a fresh result is found in the cache, redirect directly to the results page.
            return redirect(url_for('get_result', ticker=ticker))

    finally:
        db.close()

    # If no fresh cache is found, start the background analysis task using Celery.
    # .delay() is the method to call a Celery task asynchronously.
    task = run_full_analysis.delay(ticker)
    # Redirect to the results page, passing the task ID.
    # The frontend will use this ID to poll for the task's status.
    return redirect(url_for('get_result', ticker=ticker, task_id=task.id))

@app.route('/result/<ticker>')
def get_result(ticker):
    """Renders the results page.

    This page will use JavaScript to poll the backend for the analysis status and data.
    The task_id is passed in the URL to allow the frontend to know which task to poll.
    """
    task_id = request.args.get('task_id')
    return render_template('results.html', ticker=ticker, task_id=task_id)

@app.route('/status/<task_id>')
def task_status(task_id):
    """Provides the status of a background task to the frontend.

    This is an API endpoint that the frontend polls to get updates on the analysis task.
    It returns the task's state (e.g., PENDING, SUCCESS, FAILURE) and any status messages.
    """
    task = run_full_analysis.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pending...'}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'status': task.info.get('status', '')}
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # If the task failed, report the error to the frontend.
        response = {
            'state': task.state,
            'status': str(task.info),  # The exception raised during the task
        }
    return jsonify(response)

@app.route('/data/<ticker>')
def get_data(ticker):
    """API endpoint for the frontend to fetch the latest analysis data from the database.

    Once the analysis task is complete, the frontend calls this endpoint to get the
    final results (the plot, sentiment score, and Reddit posts).
    """
    db = SessionLocal()
    try:
        result = db.query(AnalysisResult).filter(AnalysisResult.ticker == ticker).first()
        if result and result.arima_plot:
            # If results are found, return them as JSON.
            return jsonify({
                'arima_plot': result.arima_plot,
                'sentiment': result.sentiment,
                'posts': result.sentiment_posts
            })
        else:
            # This case occurs if the frontend polls for data before the task has saved anything.
            # The frontend will continue to poll this endpoint until it receives data.
            return jsonify({'arima_plot': None, 'sentiment': None, 'posts': None})
    finally:
        db.close()

if __name__ == '__main__':
    # This allows the application to be run directly with `python app.py` for development.
    # The debug=True flag enables auto-reloading and a debugger.
    app.run(debug=True)