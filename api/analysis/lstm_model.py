import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential


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

def forecast_with_lstm(data, steps=30):
    """Forecasts stock prices using an LSTM model."""
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

    prediction_days = 60
    x_train, y_train = [], []
    for i in range(prediction_days, len(scaled_data)):
        x_train.append(scaled_data[i-prediction_days:i, 0])
        y_train.append(scaled_data[i, 0])

    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    model = create_lstm_model(input_shape=(x_train.shape[1], 1))
    model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=0)

    test_inputs = scaled_data[-prediction_days:].reshape(1, -1, 1)
    forecast = []
    current_input = test_inputs

    for _ in range(steps):
        predicted_price = model.predict(current_input)
        forecast.append(predicted_price[0, 0])
        current_input = np.append(current_input[:, 1:, :], [[predicted_price]], axis=1)

    forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1))
    return forecast.flatten()
