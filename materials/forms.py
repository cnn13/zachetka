from django import forms
from django.utils import timezone

from config.forms import BootstrapFormMixin

from .models import Material, Tag
from .validators import ALLOWED_EXTENSIONS

MAX_TAGS = 10


class MaterialUploadForm(BootstrapFormMixin, forms.ModelForm):
    """Задача 2.4 (ФТ-02): загрузка PDF/JPG/PNG с тегами."""

    tags_input = forms.CharField(
        label="Теги",
        required=False,
        help_text="Через запятую, например: лекция, экзамен, шпаргалка",
    )

    class Meta:
        model = Material
        fields = ["title", "subject", "teacher", "course", "year", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs["accept"] = ",".join(f".{e}" for e in ALLOWED_EXTENSIONS)
        self.fields["file"].help_text = "PDF, JPG или PNG, до 20 МБ"
        self.fields["year"].initial = timezone.localdate().year

    def clean_tags_input(self):
        names = []
        for part in self.cleaned_data["tags_input"].split(","):
            name = " ".join(part.split()).lower()
            if name and name not in names:
                names.append(name)
        if len(names) > MAX_TAGS:
            raise forms.ValidationError(f"Слишком много тегов (максимум {MAX_TAGS}).")
        if any(len(n) > 50 for n in names):
            raise forms.ValidationError("Тег не должен быть длиннее 50 символов.")
        return names

    def save(self, user=None):
        material = super().save(commit=False)
        material.uploaded_by = user
        material.save()
        material.tags.set([Tag.objects.get_or_create(name=n)[0] for n in self.cleaned_data["tags_input"]])
        return material
