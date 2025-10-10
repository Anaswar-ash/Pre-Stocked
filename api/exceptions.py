"""Custom exception classes for the Pre-Stocked application."""

class StockDataError(Exception):
    """Custom exception for errors related to fetching stock data."""
    pass

class RedditAPIError(Exception):
    """Custom exception for errors related to the Reddit API."""
    pass

class AnalysisError(Exception):
    """Custom exception for errors that occur during the analysis process."""
    pass
