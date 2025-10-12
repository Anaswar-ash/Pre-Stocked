def run_ensemble_prediction(arima_forecast, lstm_forecast, finbert_sentiment):
    """Combines predictions from multiple models using a weighted average."""
    weights = {"arima": 0.4, "lstm": 0.4, "sentiment": 0.2}

    sentiment_adjustment = 1 + (finbert_sentiment * weights["sentiment"])
    adjusted_arima = arima_forecast * sentiment_adjustment
    adjusted_lstm = lstm_forecast * sentiment_adjustment

    ensemble_forecast = (adjusted_arima * weights["arima"]) + (adjusted_lstm * weights["lstm"])

    return ensemble_forecast
