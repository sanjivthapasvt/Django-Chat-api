from django.urls import path, include
from .views import LoginView, RegisterView, LogoutView, UserProfileView, FriendRequestViewSet, FriendModelViewSet,ListUserViewSet
from rest_framework.routers import DefaultRouter
from .serializers import MyTokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView
router = DefaultRouter()
router.register(r'friend-requests', FriendRequestViewSet, basename='friend_requests')
router.register(r'friends', FriendModelViewSet, basename='friends')
router.register(r'users', ListUserViewSet, basename='users')
#for jwt to send username when getting access token with refresh tiken
class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer
urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', UserProfileView.as_view(), name="profile_update" ),
    
    #for jwt 
    path('token/refresh/', MyTokenRefreshView.as_view(),name='token_refresh'),
    
    #for friend request
    path('', include(router.urls))
]
