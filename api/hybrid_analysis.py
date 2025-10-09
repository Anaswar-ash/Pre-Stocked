# --- IMPORTS ---
import numpy as np
import pandas as pd
from transformers import pipeline
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

# --- SETUP ---
# Initialize the FinBERT sentiment analysis pipeline
finbert = pipeline('sentiment-analysis', model='ProsusAI/finbert')

# --- LSTM MODEL ---
def create_lstm_model(input_shape):
    """Creates a simple LSTM model."""
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        LSTM(50),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def forecast_with_lstm(data, days_to_predict=30):
    """Forecasts stock prices using an LSTM model."""
    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

    # Create the training data
    prediction_days = 60
    x_train, y_train = [], []
    for i in range(prediction_days, len(scaled_data)):
        x_train.append(scaled_data[i-prediction_days:i, 0])
        y_train.append(scaled_data[i, 0])

    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    # Create and train the LSTM model
    model = create_lstm_model(input_shape=(x_train.shape[1], 1))
    model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=0)

    # Make the prediction
    test_inputs = scaled_data[-prediction_days:].reshape(1, -1, 1)
    forecast = []
    current_input = test_inputs

    for _ in range(days_to_predict):
        predicted_price = model.predict(current_input)
        forecast.append(predicted_price[0, 0])
        # Update the input for the next prediction
        current_input = np.append(current_input[:, 1:, :], [[predicted_price]], axis=1)

    # Inverse transform the forecast
    forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1))
    return forecast.flatten()

# --- FINBERT SENTIMENT ---
def get_finbert_sentiment(posts):
    """Analyzes sentiment of Reddit posts using FinBERT."""
    if not posts or not isinstance(posts, list):
        return 0

    # FinBERT expects a list of strings
    # We'll use the post titles for analysis
    post_titles = [post['title'] for post in posts]
    sentiments = finbert(post_titles)

    # Convert sentiment to a numerical score
    score_map = {'positive': 1, 'neutral': 0, 'negative': -1}
    total_score = sum(score_map.get(s['label'], 0) for s in sentiments)

    return total_score / len(sentiments) if sentiments else 0

# --- ENSEMBLE MODEL ---
def run_ensemble_prediction(arima_forecast, lstm_forecast, finbert_sentiment):
    """Combines predictions from multiple models using a weighted average."""
    # Define the weights for each model
    # These weights can be tuned for better performance
    weights = {
        'arima': 0.4,
        'lstm': 0.4,
        'sentiment': 0.2
    }

    # Apply the sentiment adjustment to the forecasts
    sentiment_adjustment = 1 + (finbert_sentiment * weights['sentiment'])
    adjusted_arima = arima_forecast * sentiment_adjustment
    adjusted_lstm = lstm_forecast * sentiment_adjustment

    # Combine the adjusted forecasts
    ensemble_forecast = (adjusted_arima * weights['arima']) + (adjusted_lstm * weights['lstm'])

    return ensemble_forecast
