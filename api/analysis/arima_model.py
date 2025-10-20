import itertools
import logging

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from ..exceptions import AnalysisError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_best_arima_order(data):
    """
    Iterates through combinations of p, d, and q to find the best ARIMA model order based on AIC (Akaike Information Criterion).
    A lower AIC indicates a better model fit.
    """
    p = d = q = range(0, 3)
    pdq = list(itertools.product(p, d, q))

    best_aic = float("inf")
    best_order = None

    for order in pdq:
        try:
            model = ARIMA(data, order=order)
            model_fit = model.fit()
            if model_fit.aic < best_aic:
                best_aic = model_fit.aic
                best_order = order
        except Exception:
            continue

    return best_order

def forecast_stock_price(df, days_to_predict=30):
    """
    Forecasts the stock price using the best ARIMA model found.
    """
    try:
        best_order = find_best_arima_order(df['Close'])
        if best_order is None:
            logging.warning("Could not find a suitable ARIMA model. Falling back to default order (5,1,0).")
            best_order = (5, 1, 0)

        model = ARIMA(df['Close'], order=best_order)
        model_fit = model.fit()

        forecast = model_fit.forecast(steps=days_to_predict)

        forecast_dates = pd.to_datetime(df.index[-1]) + pd.to_timedelta(range(1, days_to_predict + 1), unit='D')

        return forecast, forecast_dates
    except Exception as e:
        logging.error(f"Error during ARIMA forecasting: {e}")
        raise AnalysisError("Failed to generate stock price forecast.") from e
