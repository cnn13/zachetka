from django.contrib import admin
from .models import PomodoroSession
@admin.register(PomodoroSession)
class PomodoroSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "subject_name", "duration_minutes", "created_at"]
    list_filter = ["created_at", "subject_name"]
