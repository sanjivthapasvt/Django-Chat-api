from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet

router = DefaultRouter()
router.register(r'chatrooms', ChatRoomViewSet, basename='chatroom')
urlpatterns = router.urls
