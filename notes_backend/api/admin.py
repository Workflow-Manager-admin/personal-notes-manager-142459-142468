# Register your models here.

from django.contrib import admin
from .models import Note

# PUBLIC_INTERFACE
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """
    Admin interface for the Note model.
    Provides list display and search/filter capabilities for manual inspection and management.
    """
    list_display = ('id', 'title', 'owner', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'owner__username')
    list_filter = ('created_at', 'updated_at', 'owner')
