import json
from channels.generic.websocket import AsyncWebsocketConsumer
import ccxt
import asyncio

class ChartConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Initialize exchange details
        self.exchange = 'binance'
        self.symbol = 'BTC/USDT'
        self.timeframe = '1m'

        # Start real-time data task
        self.fetch_task = asyncio.create_task(self.send_realtime_data())

    async def disconnect(self, close_code):
        # Cancel the task when the WebSocket disconnects
        if hasattr(self, 'fetch_task'):
            self.fetch_task.cancel()

    async def send_realtime_data(self):
        exchange_class = getattr(ccxt, self.exchange)
        exchange = exchange_class({'rateLimit': True, 'enableRateLimit': True})

        while True:
            try:
                # Fetch the latest OHLCV data
                ohlcv = exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=500)
                if ohlcv:
                    latest = ohlcv[-1]
                    data = {
                        "time": int(latest[0] / 1000),  # Unix timestamp
                        "open": latest[1],
                        "high": latest[2],
                        "low": latest[3],
                        "close": latest[4],
                        "volume": latest[5],
                    }
                    await self.send(json.dumps(data))  # Send data to WebSocket
                await asyncio.sleep(1)  # Fetch every second
            except Exception as e:
                print(f"Error fetching data: {e}")
                await asyncio.sleep(5)
