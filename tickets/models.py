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
        # Наш список возможных статусов
    STATUS_CHOICES = [
        ('dont_know', 'Не знаю'),
        ('bad', 'Плохо'),
        ('learned', 'Выучил'),
    ]
    status = models.CharField(
        "Статус", 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='learned' # По умолчанию ставим «Выучил», как в твоем дизайне
    )

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
