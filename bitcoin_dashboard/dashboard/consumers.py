import json
from channels.generic.websocket import AsyncWebsocketConsumer
import ccxt
import asyncio

class ChartConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept WebSocket connection
        await self.accept()

        # Initialize exchange details
        self.exchange = 'binance'
        self.symbol = 'BTC/USDT'
        self.timeframe = '1m'  # Default timeframe

        # Start the real-time data task
        self.fetch_task = asyncio.create_task(self.send_realtime_data())

    async def disconnect(self, close_code):
        # Cancel the task when the WebSocket disconnects
        if hasattr(self, 'fetch_task'):
            self.fetch_task.cancel()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        # Handle the 'update_timeframe' action
        if action == 'update_timeframe':
            timeframe = text_data_json.get('timeframe')
            
            # Update the timeframe in the consumer
            self.timeframe = timeframe
            print(f"Updated timeframe to: {self.timeframe}")

            # Send acknowledgment back to client
            await self.send(text_data=json.dumps({
                'action': 'timeframe_updated',
                'timeframe': self.timeframe
            }))

            # Restart the data fetching with the new timeframe
            if hasattr(self, 'fetch_task'):
                self.fetch_task.cancel()  # Cancel the previous task
            self.fetch_task = asyncio.create_task(self.send_realtime_data())  # Start with the new timeframe

    async def send_realtime_data(self):
        exchange_class = getattr(ccxt, self.exchange)
        exchange = exchange_class({'rateLimit': True, 'enableRateLimit': True})

        while True:
            try:
                # Fetch the latest OHLCV data based on the current timeframe
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
                await asyncio.sleep(1)  # Fetch every second (adjust as needed)
            except Exception as e:
                print(f"Error fetching data: {e}")
                await asyncio.sleep(5)  # Retry after a short delay