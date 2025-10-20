from flask import Flask, jsonify, request, send_from_directory
from .config import Config
from .database import db_session, init_db, AnalysisResult
from .tasks import run_full_analysis, run_hybrid_analysis_task, celery_app
from .errors import bad_request, internal_error
import datetime
import os

# Create and configure the Flask application
app = Flask(__name__, static_folder="../frontend/build")
app.config.from_object(Config)

# Initialize the database by creating tables if they don't exist
# This is called once when the application starts.
init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Handles the form submission for stock analysis."""
    ticker = request.form.get("ticker").upper()
    analysis_type = request.form.get("analysis_type", "simple")
    if not ticker or not ticker.isalnum() or not 2 <= len(ticker) <= 5:
        return bad_request("Invalid ticker symbol.")

    cache_time_limit = datetime.datetime.utcnow() - datetime.timedelta(hours=app.config["CACHE_TIME"])
    cached_result = AnalysisResult.query.filter(
        AnalysisResult.ticker == ticker, AnalysisResult.last_updated > cache_time_limit
    ).first()

    if cached_result and cached_result.arima_plot and analysis_type == "simple":
        return jsonify({"task_id": None})

    if cached_result and cached_result.hybrid_plot and analysis_type == "hybrid":
        return jsonify({"task_id": None})

    if analysis_type == "simple":
        task = run_full_analysis.delay(ticker)
    elif analysis_type == "hybrid":
        task = run_hybrid_analysis_task.delay(ticker)
    else:
        return bad_request("Invalid analysis type.")

    return jsonify({"task_id": task.id})


@app.route("/status/<task_id>")
def task_status(task_id):
    """Provides the status of a background task to the frontend."""
    task = celery_app.AsyncResult(task_id)
    if task.state == "PENDING":
        response = {"state": task.state, "status": "Pending..."}
    elif task.state != "FAILURE":
        response = {"state": task.state, "status": task.info.get("status", "")}
        if "result" in task.info:
            response["result"] = task.info["result"]
    else:
        response = {
            "state": task.state,
            "status": str(task.info),
        }
    return jsonify(response)


@app.route("/data/<ticker>")
def get_data(ticker):
    """API endpoint for the frontend to fetch the latest analysis data from the database."""
    result = AnalysisResult.query.filter(AnalysisResult.ticker == ticker).first()
    if result and result.arima_plot:
        return jsonify(
            {"arima_plot": result.arima_plot, "sentiment": result.sentiment, "posts": result.sentiment_posts}
        )
    else:
        return jsonify({"arima_plot": None, "sentiment": None, "posts": None})


@app.route("/hybrid_analyze", methods=["POST"])
def hybrid_analyze():
    """Handles the request to start a hybrid analysis task."""
    ticker = request.form.get("ticker").upper()
    if not ticker or not ticker.isalnum() or not 2 <= len(ticker) <= 5:
        return bad_request("Invalid ticker symbol.")

    task = run_hybrid_analysis_task.delay(ticker)
    return jsonify({"task_id": task.id})


@app.route("/hybrid_data/<ticker>")
def hybrid_data(ticker):
    """API endpoint for the frontend to fetch the latest hybrid analysis data from the database."""
    result = AnalysisResult.query.filter(AnalysisResult.ticker == ticker).first()
    if result and result.hybrid_plot:
        return jsonify({"hybrid_plot": result.hybrid_plot})
    else:
        return jsonify({"hybrid_plot": None})


@app.errorhandler(400)
def handle_bad_request(e):
    return bad_request(e.description)

@app.errorhandler(500)
def handle_internal_error(e):
    return internal_error("An unexpected error has occurred.")