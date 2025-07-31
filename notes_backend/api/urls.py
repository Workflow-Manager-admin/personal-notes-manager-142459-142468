from django.urls import path
from .views import (
    health,
    register,
    login,
    logout,
    notes_list,
)

urlpatterns = [
    path('health/', health, name='Health'),
    path('auth/register/', register, name='Register'),
    path('auth/login/', login, name='Login'),
    path('auth/logout/', logout, name='Logout'),
    path('notes/', notes_list, name='NotesList'),
]
