import logging
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.metrics import mean_absolute_error, mean_squared_error

from . import arima_model, lstm_model
from ..exceptions import StockDataError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_backtesting(ticker_symbol, period="1y"):
    """
    Performs backtesting of the forecasting models.
    """
    try:
        # 1. Get historical data
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            raise StockDataError(f"No historical data found for ticker '{ticker_symbol}' for the given period.")

        # 2. Split data
        train_size = int(len(hist) * 0.8)
        train_data, test_data = hist[0:train_size], hist[train_size:]

        logging.info(f"Backtesting with {len(train_data)} training samples and {len(test_data)} testing samples.")

        # 3. Backtest ARIMA model
        arima_predictions = []
        history_arima = train_data.copy()
        for t in range(len(test_data)):
            logging.info(f"Backtesting ARIMA model: step {t+1}/{len(test_data)}")
            forecast, _ = arima_model.forecast_stock_price(history_arima, steps=1)
            arima_predictions.append(forecast.iloc[0])
            history_arima = pd.concat([history_arima, test_data.iloc[t:t+1]])

        arima_mae = mean_absolute_error(test_data['Close'], arima_predictions)
        arima_rmse = np.sqrt(mean_squared_error(test_data['Close'], arima_predictions))

        logging.info(f"ARIMA Backtesting Results: MAE={arima_mae:.4f}, RMSE={arima_rmse:.4f}")

        # 4. Backtest LSTM model
        lstm_predictions = []
        history_lstm = train_data.copy()
        for t in range(len(test_data)):
            logging.info(f"Backtesting LSTM model: step {t+1}/{len(test_data)}")
            forecast = lstm_model.forecast_with_lstm(history_lstm, steps=1)
            lstm_predictions.append(forecast[0])
            history_lstm = pd.concat([history_lstm, test_data.iloc[t:t+1]])

        lstm_mae = mean_absolute_error(test_data['Close'], lstm_predictions)
        lstm_rmse = np.sqrt(mean_squared_error(test_data['Close'], lstm_predictions))

        logging.info(f"LSTM Backtesting Results: MAE={lstm_mae:.4f}, RMSE={lstm_rmse:.4f}")

        return {
            "status": "success",
            "arima_mae": arima_mae,
            "arima_rmse": arima_rmse,
            "lstm_mae": lstm_mae,
            "lstm_rmse": lstm_rmse
        }

    except StockDataError as e:
        logging.error(f"Stock data error during backtesting: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred during backtesting: {e}")
        raise
