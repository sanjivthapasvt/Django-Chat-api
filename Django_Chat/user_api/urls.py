from django.urls import path, include
from .views import LoginView, RegisterView, LogoutView
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
]
