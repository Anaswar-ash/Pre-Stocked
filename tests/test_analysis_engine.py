import pandas as pd
import pytest
from unittest.mock import patch
from api.analysis_engine import calculate_technical_indicators, get_stock_data, forecast_stock_price
from api.exceptions import StockDataError


def test_calculate_technical_indicators():
    # Create a sample DataFrame
    data = {"Close": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}
    df = pd.DataFrame(data)

    # Calculate technical indicators
    df = calculate_technical_indicators(df)

    # Check that the SMA50 and SMA200 columns were added
    assert "SMA50" in df.columns
    assert "SMA200" in df.columns


@patch("api.analysis_engine.yf.Ticker")
def test_get_stock_data_success(mock_ticker):
    # Mock the yfinance Ticker object
    mock_instance = mock_ticker.return_value
    mock_instance.info = {"longName": "Test Inc.", "symbol": "TEST"}
    mock_instance.history.return_value = pd.DataFrame({"Close": [100, 110, 120]})

    info, hist = get_stock_data("TEST")

    assert info["longName"] == "Test Inc."
    assert not hist.empty


@patch("api.analysis_engine.yf.Ticker")
def test_get_stock_data_no_data(mock_ticker):
    # Mock the yfinance Ticker object to return an empty history
    mock_instance = mock_ticker.return_value
    mock_instance.info = {"longName": "Test Inc.", "symbol": "TEST"}
    mock_instance.history.return_value = pd.DataFrame()

    with pytest.raises(StockDataError):
        get_stock_data("TEST")


@patch("api.analysis_engine.find_best_arima_order", return_value=(1, 1, 1))
def test_forecast_stock_price(mock_find_order):
    # Create a sample DataFrame
    data = {"Close": [100 + i for i in range(100)]}
    df = pd.DataFrame(data)
    df.index = pd.to_datetime(pd.date_range(start="2022-01-01", periods=100))

    forecast, forecast_dates = forecast_stock_price(df, days_to_predict=10)

    assert len(forecast) == 10
    assert len(forecast_dates) == 10
