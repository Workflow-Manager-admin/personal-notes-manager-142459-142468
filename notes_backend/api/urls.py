from django.urls import path, include
from .views import (
    health,
    register,
    login,
    logout,
    NoteViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename="note")

urlpatterns = [
    path('health/', health, name='Health'),
    path('auth/register/', register, name='Register'),
    path('auth/login/', login, name='Login'),
    path('auth/logout/', logout, name='Logout'),
    path('', include(router.urls)),
]
