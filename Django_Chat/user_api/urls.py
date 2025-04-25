from django.urls import path, include
from .views import LoginView, RegisterView, LogoutView, UserProfileView, FriendRequestViewSet, FriendViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'friend-requests', FriendRequestViewSet, basename='friend_requests')
router.register(r'friends', FriendViewSet, basename='friends')

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', UserProfileView.as_view(), name="profile_update" ),
    #for friend request
    path('', include(router.urls))
]
