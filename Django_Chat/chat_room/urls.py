from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, MessageViewSet, NotificationViewSet
from rest_framework_nested.routers import NestedDefaultRouter
router = DefaultRouter()
router.register(r'chatrooms', ChatRoomViewSet, basename='chatroom')
router.register(r'notifications', NotificationViewSet, basename='notification')
chatroom_router = NestedDefaultRouter(router, r'chatrooms', lookup='chatroom')
chatroom_router.register(r'messages', MessageViewSet, basename='chatroom-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(chatroom_router.urls)),
]