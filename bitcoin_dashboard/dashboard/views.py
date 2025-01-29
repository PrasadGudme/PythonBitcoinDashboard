import json
from django.shortcuts import render
import ccxt
import pandas as pd

# Fetch OHLCV data from exchange
def fetch_ohlcv(exchange_name, symbol, timeframe, limit=1000000000):
    try:
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({'rateLimit': 1200, 'enableRateLimit': True})
        exchange.load_markets()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

# Prepare chart data in format required for the chart
def prepare_chart_data(df):
    return [
        {
            "time": int(row.timestamp.timestamp()),  # Ensure Unix timestamp is used
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
        }
        for _, row in df.iterrows()
    ]

# Handle the rendering of the chart page
def index(request):
    exchanges = ['binance', 'coinbasepro', 'kraken']
    timeframes = ['1s', '1m', '5m', '15m', '30m', '45m', '1h', '4h', '1d', '1w']

    selected_exchange = request.GET.get('exchange', 'binance')
    selected_timeframe = request.GET.get('timeframe', '1h')

    # Fetch data for selected exchange and timeframe
    df = fetch_ohlcv(selected_exchange, "BTC/USDT", selected_timeframe)

    chart_data = []
    if df is not None:
        chart_data = prepare_chart_data(df)

    context = {
        "exchanges": exchanges,
        "timeframes": timeframes,
        "selected_exchange": selected_exchange,
        "selected_timeframe": selected_timeframe,
        "chart_data": json.dumps(chart_data),  # Send data as JSON string
    }
    return render(request, 'dashboard/index.html', context)
