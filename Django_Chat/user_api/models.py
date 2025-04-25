from django.db import models
from django.contrib.auth.models import AbstractUser

def user_profile_pic_path(instance, filename):
    return f'media/profile_pic/user_{instance.id}/{filename}'

class User(AbstractUser):
    profile_pic = models.ImageField(upload_to=user_profile_pic_path, blank=True, null=True)
    online_status = models.BooleanField(default=False, db_index=True)
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]
    USERNAME_FIELD = "username"
    
    def __str__(self):
        return self.username