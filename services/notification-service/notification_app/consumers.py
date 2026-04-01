import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'user_{self.user_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group (Kafka bridge sends 'notification_message' type)
    async def notification_message(self, event):
        message = event['message']
        notification_type = event['notification_type']
        order_id = event.get('order_id')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'notification_type': notification_type,
            'order_id': order_id,
            'source': 'kafka_event'
        }))
