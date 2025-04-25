from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

def user_profile_pic_path(instance, filename):
    return f'media/profile_pic/user_{instance.id}/{filename}'

class User(AbstractUser):
    profile_pic = models.ImageField(upload_to=user_profile_pic_path, blank=True, null=True)
    online_status = models.BooleanField(default=False, db_index=True)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]
    USERNAME_FIELD = "username"
    
    def __str__(self):
        return self.username
    
class FriendRequest(models.Model):
    STATUS_CHOICES= (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    )
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        
    def __str__(self):
        return f"Request from {self.from_user} to {self.to_user} - {self.status}"
    
    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError("Cannot send friend request to yourself")
        super().clean
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args,**kwargs)
        
    def accept(self):
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            
            self.from_user.friends.add(self.to_user)
            self.to_user.friends.add(self.from_user)
        else:
            raise ValidationError("Only pending requests can be accepted")

    def reject(self):
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
        else:
            raise ValidationError("Only pending requests can be rejected")