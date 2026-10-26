from django.conf import settings
from django.db import models


class Subject(models.Model):
    """Предмет."""
    name = models.CharField("Название", max_length=200, unique=True)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ticket(models.Model):
    """Экзаменационный билет."""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="tickets", verbose_name="Предмет")
    number = models.PositiveIntegerField("Номер билета")
    text = models.TextField("Текст вопроса")

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"
        ordering = ["subject__name", "number"]
        constraints = [models.UniqueConstraint(fields=["subject", "number"], name="unique_ticket_number_per_subject")]

    def __str__(self):
        return f"{self.subject}: билет {self.number}"


class TicketProgress(models.Model):
    """Оценка билета хранится у каждого пользователя отдельно, в БД."""
    UNKNOWN = "unknown"
    BAD = "bad"
    LEARNED = "learned"
    STATUS_CHOICES = [(UNKNOWN, "Не знаю"), (BAD, "Плохо"), (LEARNED, "Выучил")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ticket_progress")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="progress")
    status = models.CharField("Оценка", max_length=10, choices=STATUS_CHOICES, default=UNKNOWN)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Прогресс билета"
        verbose_name_plural = "Прогресс билетов"
        constraints = [models.UniqueConstraint(fields=["user", "ticket"], name="unique_ticket_progress_per_user")]

    def __str__(self):
        return f"{self.user}: {self.ticket} — {self.get_status_display()}"
