from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from tickets.models import Subject
from .validators import validate_material_file


class Tag(models.Model):
    """Тег материала."""

    name = models.CharField("Тег", max_length=50, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Material(models.Model):
    """Лекция или конспект, доступный только авторизованным пользователям."""

    COURSE_CHOICES = [(i, f"{i} курс") for i in range(1, 7)]
    title = models.CharField("Название", max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="materials", verbose_name="Предмет")
    teacher = models.CharField("Преподаватель", max_length=200)
    course = models.PositiveSmallIntegerField("Курс", choices=COURSE_CHOICES)
    year = models.PositiveSmallIntegerField("Год", validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    file = models.FileField("Файл", upload_to="materials/", validators=[validate_material_file])
    tags = models.ManyToManyField(Tag, blank=True, related_name="materials", verbose_name="Теги")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Загрузил"
    )
    is_hidden = models.BooleanField("Скрыт", default=False, db_index=True)
    created_at = models.DateTimeField("Дата загрузки", auto_now_add=True)

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class MaterialFavorite(models.Model):
    """Избранное принадлежит конкретному зарегистрированному пользователю."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="material_favorites")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="favorites")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные материалы"
        constraints = [models.UniqueConstraint(fields=("user", "material"), name="unique_material_favorite")]
