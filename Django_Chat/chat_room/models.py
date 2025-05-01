from django.db import models, transaction
from user_api.models import User
import uuid
from django.core.exceptions import ValidationError

# ------------------------------
# ChatRoom model
# ------------------------------
class ChatRoom(models.Model):
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
            models.Index(fields=['is_group', 'created_at', 'last_message']),
            models.Index(fields=['sharable_room_id']),
        ]

    def __str__(self):
        if self.is_group and self.room_name:
            return self.room_name
        # Return names of up to 3 participants for private chats
        participants = self.participants.all()[:3]
        return f"{'Group' if self.is_group else 'Private'} Chat ({', '.join(user.username for user in participants)})"

    def clean(self):
        """Model-level validation"""
        if self.is_group and self.participants.count() > 50:
            raise ValidationError("A group cannot have more than 50 members.")

    def add_participant(self, user, is_admin=False):
        """Adds a participant to the room"""
        if self.is_group and self.participants.count() >= 50:
            raise ValueError("Group cannot have more than 50 members.")
        self.participants.add(user)
        if is_admin:
            self.admins.add(user)

    def remove_participant(self, user):
        """Removes a participant and admin status (if any)"""
        self.participants.remove(user)
        self.admins.remove(user)

    def update_last_message(self, message):
        """Updates the latest message in the room"""
        self.last_message = message
        self.save(update_fields=['last_message'])

    def convert_to_group(self, creator_user):
        """
        Converts a private chat to group chat
        by cloning participants and metadata.
        """
        if not self.is_group:
            group_chat = ChatRoom.objects.create(
                is_group=True,
                creator=creator_user,
                room_name=self.room_name,
                group_image=self.group_image
            )
            existing_participants = list(self.participants.all())
            group_chat.participants.set(existing_participants + [creator_user])
            group_chat.admins.set(existing_participants)
            return group_chat
        return self

    @classmethod
    def get_or_create_private_chat(cls, user1, user2):
        """Returns existing private chat between two users or creates a new one"""
        existing_rooms = cls.objects.filter(
            is_group=False,
            participants=user1
        ).filter(
            participants=user2
        )

        for room in existing_rooms:
            if room.participants.count() == 2:
                return room, False

        with transaction.atomic():
            new_room = cls.objects.create(is_group=False, creator=user1)
            new_room.participants.add(user1, user2)
        return new_room, True


# ------------------------------
# Message model
# ------------------------------
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="chat/images", blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['room', 'timestamp']),
            models.Index(fields=['content']),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}" if self.content else f"{self.sender.username}: [Image]"

    def save(self, *args, **kwargs):
        """Save message and update last message in room if new"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.room.update_last_message(self)


# ------------------------------
# MessageReadStatus model
# ------------------------------
class MessageReadStatus(models.Model):
    """Tracks which users have read which messages"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')
        indexes = [
            models.Index(fields=['user', 'message']),
        ]


# ------------------------------
# Notification model
# ------------------------------
class Notification(models.Model):
    """Represents notifications for message events"""
    NOTIFICATION_TYPES = (
        ('new_message', 'New Message'),
        ('mention', 'Mention'),
        ('room_invite', 'Room Invite'),
        ('system', 'System Notification')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='new_message')

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.notification_type}"
