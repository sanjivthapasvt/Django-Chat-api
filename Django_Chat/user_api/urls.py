from django.urls import path, include
from .views import LoginView, RegisterView, LogoutView, UserProfileView

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('profile/', UserProfileView.as_view(), name="profile_update" )
]
