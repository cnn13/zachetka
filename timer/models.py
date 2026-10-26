from django.conf import settings
from django.db import models

class PomodoroSession(models.Model):
    """Завершённая учебная сессия пользователя."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pomodoro_sessions")
    subject_name = models.CharField("Предмет", max_length=200)
    duration_minutes = models.PositiveSmallIntegerField("Минут", default=25)
    client_token = models.CharField("Идентификатор цикла", max_length=100)
    created_at = models.DateTimeField("Завершено", auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "client_token"], name="unique_pomodoro_session_per_user")]
        ordering = ["-created_at"]
        verbose_name = "Помодоро-сессия"
        verbose_name_plural = "Помодоро-сессии"
