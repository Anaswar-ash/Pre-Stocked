from flask import Flask, jsonify, request, send_from_directory
from config import Config
from database import SessionLocal, init_db, AnalysisResult
from tasks import run_full_analysis, run_hybrid_analysis_task
import datetime
import os

# Create and configure the Flask application
app = Flask(__name__, static_folder='frontend/build')
app.config.from_object(Config)

# Initialize the database by creating tables if they don't exist
# This is called once when the application starts.
init_db()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

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

@app.route('/hybrid_analyze', methods=['POST'])
def hybrid_analyze():
    """Handles the request to start a hybrid analysis task."""
    ticker = request.form.get('ticker').upper()
    if not ticker or not ticker.isalnum() or not 2 <= len(ticker) <= 5:
        return jsonify({'error': 'Invalid ticker symbol.'}), 400

    task = run_hybrid_analysis_task.delay(ticker)
    return jsonify({'task_id': task.id})

@app.route('/hybrid_result/<ticker>')
def hybrid_result(ticker):
    """Renders the hybrid results page."""
    return render_template('hybrid_results.html', ticker=ticker)

@app.route('/hybrid_data/<ticker>')
def hybrid_data(ticker):
    """API endpoint for the frontend to fetch the latest hybrid analysis data from the database."""
    db = SessionLocal()
    try:
        result = db.query(AnalysisResult).filter(AnalysisResult.ticker == ticker).first()
        if result and result.hybrid_plot:
            return jsonify({
                'hybrid_plot': result.hybrid_plot
            })
        else:
            return jsonify({'hybrid_plot': None})
    finally:
        db.close()

if __name__ == '__main__':
    # This allows the application to be run directly with `python app.py` for development.
    # The debug=True flag enables auto-reloading and a debugger.
    app.run(debug=True)