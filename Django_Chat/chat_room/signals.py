from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChatRoom, Message, Notification
import logging
from django.db import transaction
from django.db import IntegrityError

# logger for error tracking
logger = logging.getLogger(__name__)

@receiver(m2m_changed, sender=ChatRoom.participants.through)
def update_group_room_name(sender, instance, action, pk_set, **kwargs):
    """
    Updates group chat room name when participants are added, if it's a group and no custom name is set.
    """
    # Check if participants were added, it's a group, and no custom name exists
    if action == 'post_add' and instance.is_group and not instance.room_name:
        try:
            # Refresh instance to ensure latest data
            instance.refresh_from_db()

            # Get all participants
            participants = instance.participants.all()
            if participants.exists():
                # Use first 3 participants for name
                participants_for_name = participants[:3]
                participant_usernames = ', '.join(user.username for user in participants_for_name)

                # Set new room name
                new_room_name = f"Group ({participant_usernames})"
                instance.room_name = new_room_name

                # Save only the room_name field
                instance.save(update_fields=['room_name'])

        except Exception as e:
            # Log any errors
            logger.error(f"Error updating group room name for room {instance.id}: {e}")

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """Creates notifications for new messages and sends them via WebSocket."""
    # Only process new messages
    if not created:
        return
    
    # Get chatroom and participants
    chatroom = instance.room
    participants = chatroom.participants.all()

    # Prepare notifications for each participant (except sender)
    notifications = []
    for user in participants:
        if user == instance.sender:
            continue
        notification = Notification(
            user=user,
            message=instance,
            notification_type="new_message"
        )
        notifications.append(notification)

    try:
        # Save notifications in a single transaction
        with transaction.atomic():
            Notification.objects.bulk_create(notifications)
    except Exception as e:
        # Log any errors
        logger.error(f"Error creating notifications for message {instance.id}: {e}")

    # Send notifications via WebSocket
    channel_layer = get_channel_layer()
    for notification in notifications:
        async_to_sync(channel_layer.group_send)(
            f"notification_{notification.user.id}",
            {
                "type": "send_notification",
                "message": {
                    "message_id": instance.id,
                    "sender": instance.sender.username,
                    "room_id": chatroom.id,
                    "content": instance.content[:50] + '...' if len(instance.content) > 50 else instance.content,
                    "timestamp": notification.timestamp.isoformat() if notification.timestamp else None,
                    "is_read": False,
                    "notification_type": notification.notification_type
                }
            }
        )