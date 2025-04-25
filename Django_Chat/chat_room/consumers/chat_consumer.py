from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from channels.exceptions import DenyConnection
from ..models import ChatRoom, User
from channels.db import database_sync_to_async
from ..models import Message, MessageReadStatus

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = int(self.scope['url_route']['kwargs']['chatroom_id'])
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        # Deny connection if the user is not authenticated
        if not self.user or not self.user.is_authenticated:
            raise DenyConnection("User not authenticated")
        
        # Check if the user is a participant in the room
        try:
            room = await database_sync_to_async(ChatRoom.objects.get)(id=self.room_id)
            is_participant = await database_sync_to_async(room.participants.filter(id=self.user.id).exists)()
            if not is_participant:
                raise DenyConnection("User is not in the chatroom")
        except ChatRoom.DoesNotExist:
            raise DenyConnection("Room does not exist")
        
        # Add the user to the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.set_online_status(True)
        await self.accept()
        
    async def disconnect(self, close_code):
        # Remove the user from the room group
        await self.set_online_status(False)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
    @database_sync_to_async
    def set_online_status(self, status: bool):
        user = User.objects.get(id=self.user.id)
        user.online_status = status
        user.save()
          
    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        # Handle 'typing' and 'stop_typing' events
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
        elif event_type =='read_message':
            await self.handle_read_message(data)

    # Send 'typing' event to the group
    async def show_typing(self, event):
        await self.send_json({
            'type': 'typing',
            'username': event['username']
        })
        
    # Send 'stop_typing' event to the group
    async def hide_typing(self, event):
        await self.send_json({
            'type': 'stop_typing',
            'username': event['username']
        })
    
    # Send a new message to the group
    async def chat_message(self, event):
        await self.send_json({
            'type': 'new_message',
            'message': event['message']
        })

    # Send 'message.read' event when the message is marked as read
    async def message_read(self, event):
        await self.send_json({
            "type": "message.read",
            "message_id": event["message_id"],
            "reader": event["reader"],
            "read_at": event["read_at"]
        })



    async def handle_read_message(self, data):
        message_id = data.get("message_id")
        try:
            message = await database_sync_to_async(Message.objects.select_related('room').get)(id=message_id)
            
            if message.sender_id == self.user.id:
                return
            
            # Create read status
            read_status, created = await database_sync_to_async(MessageReadStatus.objects.get_or_create)(
                message=message, user=self.user
            )

            if created:
                await self.channel_layer.group_send(
                    f"chat_{message.room.id}",
                    {
                        "type": "message.read",
                        "message_id": message.id,
                        "reader": {
                            "id": self.user.id,
                            "username": self.user.username,
                        },
                        "read_at": read_status.timestamp.isoformat()
                    }
                )

        except Message.DoesNotExist:
            pass
