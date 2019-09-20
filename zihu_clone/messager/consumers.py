
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MessagesConsumer(AsyncWebsocketConsumer):
    """handle websocket request in the private messaging module"""

    async def connect(self):
        if self.scope['user'].is_anonymous:
            # refuse connection of users not logged in
            await self.close()
        else:
            await self.channel_layer.group_add(self.scope['user'].username, self.channel_name)
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """receive private messages"""
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        """leave the chat group"""
        await self.channel_layer.group_discard(self.scope['user'].username, self.channel_name)