import time
import datetime
import requests
import pandas as pd
from stocks.models import Stock


# Function to fetch OHLC data and update stock records
def fetch_stock_data():
    symbols = list(Stock.objects.values_list('symbol', flat=True))

    try:
        data = yf.download(symbols, period="1d", group_by='ticker', threads=False)

        for symbol in symbols:
            try:
                if symbol in data and not data[symbol].empty:
                    latest = data[symbol].iloc[-1]
                    stock = Stock.objects.get(symbol=symbol)
                    stock.open_price = latest['Open']
                    stock.high_price = latest['High']
                    stock.low_price = latest['Low']
                    stock.last_price = latest['Close']
                    stock.volume = int(latest['Volume'])
                    stock.unusual_activity = stock.volume > 1.5 * data[symbol]["Volume"].mean()
                    stock.save()
                    print(f"✅ Updated {symbol} data.")
                else:
                    print(f"⚠️ No data found for {symbol}.")
            except Exception as e:
                print(f"❌ Failed to update {symbol}: {e}")

    except yf.exceptions.YFRateLimitError:
        print("⚠️ Rate limit reached. Retrying after a short break...")
        time.sleep(180)
        fetch_stock_data()  # Retry after delay