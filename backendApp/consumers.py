from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the UUID from the URL path
        self.user_uuid = self.scope['url_route']['kwargs']['uuid']
        
        # Set up the room name
        self.room_group_name = f"notifications_{self.user_uuid}"

        # Add to the group
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

    async def receive(self, text_data):
        pass

    async def follow_request_notification(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'follow_request',
            'count': event['count'],
            'message': event['message']
        }))