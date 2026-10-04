from django.conf import settings
from django.db import models


class StudyGroup(models.Model):
    """Учебная группа (список групп заполняется в админке)."""

    name = models.CharField("Группа", max_length=50, unique=True)

    class Meta:
        verbose_name = "Учебная группа"
        verbose_name_plural = "Учебные группы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Profile(models.Model):
    """Профиль пользователя: к какой группе он относится (задача 2.3)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    group = models.ForeignKey(
        StudyGroup, on_delete=models.PROTECT, related_name="profiles", verbose_name="Группа"
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"{self.user} ({self.group})"
