from datetime import datetime, timedelta
from requests.exceptions import RequestException, Timeout
from io import StringIO
import time
import requests
import pandas as pd
from stocks.models import Stock


# 🟢 1. Update Symbols from NSE Bhavcopy
def update_symbols():
    def get_bhavcopy_data(date_str):
        url = f'https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            return pd.read_csv(StringIO(response.text))
        except (RequestException, Timeout, pd.errors.ParserError):
            return None

    today = datetime.now().date()
    while True:
        date_str = today.strftime('%d%m%Y')
        df = get_bhavcopy_data(date_str)
        if df is not None and not df.empty:
            break
        today -= timedelta(days=1)

    # Filter EQ and BE series
    filtered_df = df[df[' SERIES'].isin([' EQ', ' BE'])]
    symbols_dict = {row['SYMBOL']: f"{row['SYMBOL']}.NS" for _, row in filtered_df.iterrows()}

    # Update database
    for symbol, name in symbols_dict.items():
        Stock.objects.update_or_create(symbol=name, defaults={"name": symbol})

    print(f"✅ Updated {len(symbols_dict)} stock symbols.")
    return symbols_dict


# 🟢 2. Download Yahoo Finance Data and Update Database
def download_yfin_data():
    interval = 'daily'
    successful_download = 0
    failed_download = 0

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365 * 20)).strftime('%Y-%m-%d')

    delay_seconds = 0.2
    symbols = Stock.objects.values_list('symbol', flat=True)

    for symbol in symbols:
        print(f"🔄 Fetching data for {symbol}...")

        try:
            url = f'https://query2.finance.yahoo.com/v8/finance/chart/{symbol}'
            params = {
                'period1': int(time.mktime(time.strptime(start_date, '%Y-%m-%d'))),
                'period2': int(time.mktime(time.strptime(end_date, '%Y-%m-%d'))),
                'interval': '1d',
                'events': 'history'
            }

            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()

            json_data = response.json()
            result = json_data.get('chart', {}).get('result', [])[0]

            if not result:
                print(f"⚠️ No valid result for {symbol}")
                continue

            timestamps = result.get('timestamp', [])
            indicators = result.get('indicators', {}).get('quote', [{}])[0]

            # Extract OHLC and Volume safely
            data = {
                'Date': [datetime.fromtimestamp(ts) for ts in timestamps],
                'Open': indicators.get('open', [None] * len(timestamps)),
                'High': indicators.get('high', [None] * len(timestamps)),
                'Low': indicators.get('low', [None] * len(timestamps)),
                'Close': indicators.get('close', [None] * len(timestamps)),
                'Volume': indicators.get('volume', [0] * len(timestamps))
            }

            # Create DataFrame and filter missing values
            df_data = pd.DataFrame(data).set_index('Date')
            df_data.dropna(subset=['Close'], inplace=True)

            if df_data.empty:
                print(f"❌ No valid OHLC data for {symbol}")
                failed_download += 1
                continue

            # Update latest stock data
            latest = df_data.iloc[-1]
            stock = Stock.objects.filter(symbol=symbol).first()
            if stock:
                stock.open_price = latest['Open']
                stock.high_price = latest['High']
                stock.low_price = latest['Low']
                stock.last_price = latest['Close']
                stock.volume = int(latest['Volume'])

                # Detect unusual activity (volume spike)
                average_volume = df_data['Volume'].mean()
                stock.unusual_activity = stock.volume > 1.5 * average_volume

                stock.save()
                successful_download += 1
                print(f"✅ Updated {symbol}: Last Price - {latest['Close']}, Volume - {latest['Volume']}")

        except Exception as e:
            print(f"❌ Failed to update {symbol}: {e}")
            failed_download += 1

        time.sleep(delay_seconds)

    print(f"\n🎯 Success: {successful_download} | ❌ Failed: {failed_download}")


# 🟢 3. Save Symbols to Database
def save_symbols_to_db():
    symbols_dict = update_symbols()
    for nse_symbol, yf_symbol in symbols_dict.items():
        Stock.objects.update_or_create(symbol=yf_symbol, defaults={"name": nse_symbol})
    print(f"✅ Saved {len(symbols_dict)} symbols to the database.")