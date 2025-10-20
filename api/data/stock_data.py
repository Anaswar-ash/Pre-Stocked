import logging

import yfinance as yf

from ..exceptions import StockDataError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_stock_data(ticker_symbol):
    """
    Fetches historical stock data and company information from Yahoo Finance.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        hist = ticker.history(period="5y")
        if hist.empty:
            raise StockDataError(f"No historical data found for {ticker_symbol}")
        if 'longName' not in info or 'symbol' not in info:
            raise StockDataError(f"Incomplete company information for {ticker_symbol}")
        return info, hist
    except Exception as e:
        logging.error(f"Error fetching stock data for {ticker_symbol}: {e}")
        raise StockDataError(f"An error occurred while fetching data for {ticker_symbol} from Yahoo Finance.") from e

def calculate_technical_indicators(df):
    """
    Calculates 50-day and 200-day Simple Moving Averages (SMA).
    """
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    return df
