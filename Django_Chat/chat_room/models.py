from django.db import models

class ChatRoom(models.Model):
    room_name = models.CharField(max_length=250, blank=True, null=True)
    