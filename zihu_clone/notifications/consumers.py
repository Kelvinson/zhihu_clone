import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationsConsumer(AsyncWebsocketConsumer):
    """Handle websocket request in messaging app"""
    async def connect(self):
        """set up connection"""
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add('notifications', self.channel_name)
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        await self.channel_layer.group_discard('notifications', self.channel_name)
