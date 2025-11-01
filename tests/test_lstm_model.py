import numpy as np
import pandas as pd
import pytest
from tensorflow.keras.layers import LSTM, Dense

from api.analysis.lstm_model import create_lstm_model, forecast_with_lstm


def test_create_lstm_model():
    model = create_lstm_model(input_shape=(60, 1))
    assert len(model.layers) == 4
    assert isinstance(model.layers[0], LSTM)
    assert isinstance(model.layers[1], LSTM)
    assert isinstance(model.layers[2], Dense)
    assert isinstance(model.layers[3], Dense)

def test_forecast_with_lstm():
    # Create a sample DataFrame
    data = {"Close": [100 + i for i in range(100)]}
    df = pd.DataFrame(data)

    # Forecast with the LSTM model
    forecast = forecast_with_lstm(df, steps=10)

    # Check that the forecast has the correct length
    assert len(forecast) == 10
