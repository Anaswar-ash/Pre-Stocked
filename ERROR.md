# Error Log

## 2025-10-10

**Error:** Both simple and hybrid analyses were failing with the message "Analysis failed. Please try again."

**Root Cause:** The application was unable to connect to the Reddit API due to an issue with how the API credentials were being loaded. The `praw.Reddit` client was being initialized at the module level in `api/analysis_engine.py`, which caused problems with loading the environment variables from the `.env` file, especially in the context of the Celery worker.

**Fix:**

1.  **Refactored Reddit Client Initialization:** The global `praw.Reddit` instance was removed from `api/analysis_engine.py`.
2.  **Created `get_reddit_client()` Function:** A new function, `get_reddit_client()`, was created in `api/analysis_engine.py`. This function creates and returns an authenticated Reddit client on demand, getting the credentials from the `Config` object in `api/config.py`.
3.  **Updated `get_reddit_sentiment()`:** The `get_reddit_sentiment()` function was updated to use the new `get_reddit_client()` function.
4.  **Removed Redundant Code:** The unnecessary `load_dotenv()` call in `api/tasks.py` was removed.

This ensures that the Reddit API client is always initialized with the correct credentials, both in the main Flask application and in the Celery worker.

---

## 2025-10-10 (Evening)

**Issue:** The hybrid analysis appears to hang or get stuck, with no terminal output for over 5 minutes.

**Analysis:** This is not a crash, but a performance and feedback issue. The lack of progress updates from the Celery worker makes the application seem frozen. The root cause is likely one of the following long-running, CPU-intensive steps in the `run_hybrid_analysis_task`:

1.  **First-time Model Download:** The `transformers` library downloads the FinBERT model (several hundred MBs) the first time it's used. This can take a long time with no progress indication.
2.  **LSTM Model Training:** The `model.fit()` call for the LSTM model, while only one epoch, is running on 5 years of data and can be slow on a CPU.
3.  **FinBERT Inference:** Analyzing Reddit posts with FinBERT is also computationally expensive.

**Next Steps / Recommendations:**

To improve this, the following changes would be necessary:

1.  **More Granular Progress Updates:** Add more `self.update_state()` calls within the Celery task, specifically around the model download, LSTM training, and FinBERT analysis steps, to provide more detailed feedback.
2.  **Display Progress on Frontend:** The frontend should be updated to display the detailed status messages received from the backend, so the user knows what's happening (e.g., "Step 1 of 4: Downloading models...").