import re

from django import forms
from django.db import transaction
from django.db.models import Max

from config.forms import BootstrapFormMixin

from .models import Subject, Ticket

MAX_LINES = 500
# «12. Вопрос» или «12) Вопрос» -> «Вопрос» (номер всё равно присваивается автоматически)
NUMBER_PREFIX = re.compile(r"^\d+[.)]\s+")


class BulkTicketForm(BootstrapFormMixin, forms.Form):
    """Задача 2.7 (ФТ-05): вставили текст — по одному билету в строке."""

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(), label="Предмет", empty_label="— выберите предмет —"
    )
    text = forms.CharField(
        label="Билеты (по одному в строке)",
        widget=forms.Textarea(attrs={"rows": 12}),
        help_text="Пустые строки пропускаются. Номера билетов присваиваются автоматически.",
    )

    def clean_text(self):
        text = self.cleaned_data["text"]
        if len(text.splitlines()) > MAX_LINES:
            raise forms.ValidationError(f"Слишком много строк (максимум {MAX_LINES}).")
        return text

    def lines(self):
        result = []
        for raw in self.cleaned_data["text"].splitlines():
            line = NUMBER_PREFIX.sub("", raw.strip())
            if line:
                result.append(line)
        return result

    @transaction.atomic
    def save(self):
        subject = self.cleaned_data["subject"]
        lines = self.lines()
        last = Ticket.objects.filter(subject=subject).aggregate(m=Max("number"))["m"] or 0
        Ticket.objects.bulk_create(
            [Ticket(subject=subject, number=last + i, text=line) for i, line in enumerate(lines, 1)]
        )
        return len(lines)
