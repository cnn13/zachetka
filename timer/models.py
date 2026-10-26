from django.conf import settings
from django.db import models


class PomodoroSession(models.Model):
    """Завершённая сессия помодоро-таймера (задачи 2.8 и 3.7)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pomodoro_sessions",
        verbose_name="Пользователь",
    )
    subject_name = models.CharField("Предмет", max_length=200, blank=True)
    duration_minutes = models.PositiveSmallIntegerField("Длительность, мин", default=25)
    created_at = models.DateTimeField("Завершена", auto_now_add=True)

    class Meta:
        verbose_name = "Сессия таймера"
        verbose_name_plural = "Сессии таймера"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}: {self.subject_name or 'без предмета'}, {self.duration_minutes} мин"
