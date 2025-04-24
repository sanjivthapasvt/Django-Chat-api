from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChatRoom, Message, Notification


@receiver(m2m_changed, sender=ChatRoom.participants.through)
def update_group_room_name(sender, instance, action, pk_set, **kwargs):
    """
    Updates the group chat room_name automatically when participants are added,
    if the room is a group and doesn't have a custom name set.
    """
    # Only proceed if participants have been added, it's a group, and the name is not already set
    if action == 'post_add' and instance.is_group and not instance.room_name:
        try:
            # Refresh the instance from the database to ensure participants are up-to-date
            instance.refresh_from_db()

            participants = instance.participants.all()
            if participants.exists():
                participants_for_name = participants[:3]
                participant_usernames = ', '.join(user.username for user in participants_for_name)

                # Generate and set the new room name
                new_room_name = f"Group ({participant_usernames})"
                instance.room_name = new_room_name

                # Save the instance, updating only the room_name field
                instance.save(update_fields=['room_name'])

        except Exception as e:
            # debbuging
            print(f"Error updating group room name for room {instance.id}: {e}")


#Signals for notficatoin
@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if not created:
        return
    
    chatroom = instance.room
    participants = chatroom.participants.all()
    
    for user in participants:#skip creating notification for sender
        if user == instance.sender:
            continue
        
        #create notification
        notification = Notification.objects.create(
            user=user,
            messsage=instance,
            notification_type = "new_message"
        )
        
        #send realtime notification via websocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notificatoin_{user.id}",
            {
                "type": "send_notification",
                "message_id": instance.id,
                "sender": instance.sender.username,
                "room_id": chatroom.id,
                "content": instance.content[:50] + '...' if len(instance.content) >50 else instance.content,
                "timestamp": notification.timestamp.isoformat(),
                "is_read": False,
                "notification_type": notification.notification_type
         
            }
        )