import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from ..models import Notification

User = get_user_model()

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
            
        # Create a notification group name based on user ID
        self.notification_group_name = f"notification_{self.user.id}"
        
        # Join the notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send any existing unread notifications on connect
        unread_notifications = await self.get_unread_notifications()
        if unread_notifications:
            await self.send_json({
                'type': 'notification_list',
                'notifications': unread_notifications
            })
    
    async def disconnect(self, close_code):
        # Leave the notification group
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get('action')
            
            if action == 'mark_read':
                notification_id = text_data_json.get('notification_id')
                success = await self.mark_notification_read(notification_id)
                await self.send_json({
                    'type': 'mark_read_response',
                    'notification_id': notification_id,
                    'success': success
                })
            
            elif action == 'mark_all_read':
                count = await self.mark_all_notifications_read()
                await self.send_json({
                    'type': 'mark_all_read_response',
                    'count': count,
                    'success': True
                })
                
            elif action == 'get_unread':
                unread_notifications = await self.get_unread_notifications()
                await self.send_json({
                    'type': 'notification_list',
                    'notifications': unread_notifications
                })
        
        except json.JSONDecodeError:
            await self.send_json({
                'type': 'error',
                'message': 'Invalid JSON format'
            })
        except Exception as e:
            await self.send_json({
                'type': 'error',
                'message': str(e)
            })
    
    # Receive message from notification group
    async def send_notification(self, event):
        # Send message to WebSocket
        await self.send_json({
            'type': 'new_notification',
            'notification': event['message']
        })
    
    @database_sync_to_async
    def get_unread_notifications(self):
        notifications = Notification.objects.filter(
            user=self.user,
            is_read=False
        ).order_by('-timestamp')[:20]
        
        return [
            {
                'id': notification.id,
                'message_id': notification.message.id if notification.message else None,
                'sender': notification.message.sender.username if notification.message else None,
                'room_id': notification.message.room.id if notification.message else None,
                'content': notification.message.content[:50] + '...' if notification.message and len(notification.message.content) > 50 else notification.message.content if notification.message else None,
                'timestamp': notification.timestamp.isoformat(),
                'is_read': notification.is_read,
                'notification_type': notification.notification_type
            }
            for notification in notifications
        ]
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=self.user)
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def mark_all_notifications_read(self):
        return Notification.objects.filter(user=self.user, is_read=False).update(is_read=True)
