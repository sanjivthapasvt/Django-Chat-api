from django.db import models
from user_api.models import User
import uuid

class ChatRoom(models.Model):
    """Model for chat room"""
    room_name = models.CharField(max_length=200, null=True, blank=True)
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_rooms")
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    admins = models.ManyToManyField(User, related_name='admin_rooms')
    sharable_room_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    last_message = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_message_room')
    group_image = models.ImageField(upload_to="media/chat/group_images", null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_group', 'created_at']),
            models.Index(fields=['sharable_room_id']),
        ]
    
    def __str__(self):
        if self.is_group and self.room_name:
            return self.room_name
        # Only display up to 3 participant names
        participants = self.participants.all()[:3]
        if self.is_group:
            return f"Group Chat ({', '.join(user.username for user in participants)})"
        else:
            return f"Private Chat ({', '.join(user.username for user in participants)})"
    
    def save(self, *args, **kwargs):
        # checking if the room is new because pk is not saved yet is db
        is_new = self.pk is None
        # Save the room first
        super().save(*args, **kwargs)
        
    
    def add_participant(self, user, is_admin=False):
        """Add a participant to the room"""
        if self.is_group and self.participants.count() >= 50:
            raise ValueError("Group cannot have more than 50 members.")
        
        self.participants.add(user)
        if is_admin:
            self.admins.add(user)
    
    def remove_participant(self, user):
        """Remove a participant from the room"""
        if self.is_group:
            self.participants.remove(user)
            # remove from admins if they were an admin
            if user in self.admins.all():
                self.admins.remove(user)
    
    def update_last_message(self, message):
        """Update the last message in the room"""
        self.last_message = message
        self.save(update_fields=['last_message'])
    
    def convert_to_group(self, creator_user):
        if not self.is_group:
            # Create a new group chat
            group_chat = ChatRoom.objects.create(
                is_group=True,
                creator=creator_user,
                room_name=self.room_name,
                group_image=self.group_image
            )

            # Get existing participants and add the creator to the list
            existing_participants = list(self.participants.all())
            all_initial_participants = existing_participants + [creator_user]

            # add aLL initial participants using set()
            group_chat.participants.set(all_initial_participants)

            group_chat.admins.set(existing_participants)
            
            return group_chat
        return self
    
    @classmethod
    def get_or_create_private_chat(cls, user1, user2):
        """Get existing private chat between two users or create a new one"""
        # Look for existing private chat with exactly these two participants
        existing_rooms = ChatRoom.objects.filter(
            is_group=False,
            participants=user1
        ).filter(
            participants=user2
        )
        
        for room in existing_rooms:
            # If the room has exactly 2 participants and they are user1 and user2
            if room.participants.count() == 2:
                return room, False
        
        # Create new private room
        new_room = ChatRoom.objects.create(
            is_group=False,
            creator=user1
        )
        new_room.participants.add(user1, user2)
        return new_room, True



class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="chat/images", blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['room', 'timestamp']),
            models.Index(fields=['content']),  # For message searching
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Update the last message in the room
            self.room.update_last_message(self)

class MessageReadStatus(models.Model):
    """Model to Track read status of messages per user"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('message', 'user')
        indexes = [
            models.Index(fields=['user', 'message']),
        ]


class Notification(models.Model):
    """Notification model for new messages"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    NOTIFICATION_TYPES = (
        ('new_message', 'New Message'),
        ('mention', 'Mention'),
        ('room_invite', 'Room Invite'),
        ('system', 'System Notification')
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='new_message')
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    def __str__(self):
        return f"Notification for {self.user.username}: {self.notification_type}"