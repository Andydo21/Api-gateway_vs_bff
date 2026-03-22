import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
import websockets
import asyncio

logger = logging.getLogger(__name__)

class WebSocketProxyConsumer(AsyncWebsocketConsumer):
    """
    A simple proxy consumer that forwards WebSocket traffic to another service.
    """
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs'].get('user_id')
        # Internal URL of the notification service
        self.target_url = f"ws://notification-service:4007/ws/notifications/{self.user_id}/"
        
        await self.accept()
        
        try:
            self.proxy_ws = await websockets.connect(self.target_url)
            # Start a task to listen for messages from the target and forward them to the client
            self.listen_task = asyncio.create_task(self.receive_from_proxy())
        except Exception as e:
            logger.error(f"Failed to connect to proxy target: {e}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'proxy_ws'):
            await self.proxy_ws.close()
        if hasattr(self, 'listen_task'):
            self.listen_task.cancel()

    async def receive(self, text_data=None, bytes_data=None):
        # Forward message from client to target
        if text_data:
            await self.proxy_ws.send(text_data)
        elif bytes_data:
            await self.proxy_ws.send(bytes_data)

    async def receive_from_proxy(self):
        try:
            async for message in self.proxy_ws:
                await self.send(text_data=message if isinstance(message, str) else None,
                               bytes_data=message if isinstance(message, bytes) else None)
        except Exception as e:
            logger.error(f"Error in proxy receive task: {e}")
            await self.close()
