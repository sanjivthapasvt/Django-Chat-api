from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import ChatRoom


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
