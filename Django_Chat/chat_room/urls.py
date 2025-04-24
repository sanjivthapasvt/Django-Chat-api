from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, MessageViewSet
from rest_framework_nested.routers import NestedDefaultRouter
router = DefaultRouter()
router.register(r'chatrooms', ChatRoomViewSet, basename='chatroom')

chatroom_router = NestedDefaultRouter(router, r'chatrooms', lookup='chatroom')
chatroom_router.register(r'messages', MessageViewSet, basename='chatroom-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(chatroom_router.urls)),
]