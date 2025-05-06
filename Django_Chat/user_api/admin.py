from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, FriendRequest

class UserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('profile_pic',)}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(FriendRequest)
