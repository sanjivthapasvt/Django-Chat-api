from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.exceptions import DenyConnection
from ..models import ChatRoom
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = int(self.scope['url_route']['kwargs']['chatroom_id'])
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        if not self.user or not self.user.is_authenticated:
            raise DenyConnection("User not authenticated")
        
        try:
            room = await database_sync_to_async(ChatRoom.objects.get)(id=self.room_id)
            is_participant = await database_sync_to_async(room.participants.filter(id=self.user.id).exists)()
            if not is_participant:
                raise DenyConnection("User is not in the chatroom")
        except ChatRoom.DoesNotExist:
            raise DenyConnection("Room does not exist")
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'show_typing',
                    'username': self.user.username
                }
            )
        elif event_type == 'stop_typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'hide_typing',
                    'username': self.user.username
                }
            )
    
    async def show_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username']
        }))
        
    async def hide_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'stop_typing',
            'username': event['username']
        }))
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))
