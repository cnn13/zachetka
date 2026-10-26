from django.conf import settings
from django.db import models


class Subject(models.Model):
    """Предмет (задача 1.6)."""

    name = models.CharField("Название", max_length=200, unique=True)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ticket(models.Model):
    """Экзаменационный билет, привязанный к предмету (задача 1.6)."""

    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="tickets", verbose_name="Предмет"
    )
    number = models.PositiveIntegerField("Номер билета")
    text = models.TextField("Текст вопроса")

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"
        ordering = ["subject__name", "number"]
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "number"], name="unique_ticket_number_per_subject"
            )
        ]

    def __str__(self):
        return f"{self.subject}: билет {self.number}"


class TicketStatus(models.Model):
    """Статус билета у конкретного пользователя (задачи 3.5–3.6).

    У каждого пользователя свой статус: «не знаю», «плохо» или «выучил».
    Если записи нет, считается «не знаю».
    """

    DONT_KNOW = "dont_know"
    BAD = "bad"
    LEARNED = "learned"
    STATUS_CHOICES = [
        (DONT_KNOW, "Не знаю"),
        (BAD, "Плохо"),
        (LEARNED, "Выучил"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ticket_statuses",
        verbose_name="Пользователь",
    )
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="statuses", verbose_name="Билет"
    )
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default=DONT_KNOW)
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        verbose_name = "Статус билета"
        verbose_name_plural = "Статусы билетов"
        constraints = [
            models.UniqueConstraint(fields=["user", "ticket"], name="unique_status_per_user_ticket")
        ]

    def __str__(self):
        return f"{self.user}: {self.ticket} — {self.get_status_display()}"
