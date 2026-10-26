import re
from django import forms
from django.db import transaction
from django.db.models import Max
from config.forms import BootstrapFormMixin
from .models import Subject, Ticket
MAX_LINES = 500
NUMBER_PREFIX = re.compile(r"^\d+[.)]\s+")

class BulkTicketForm(BootstrapFormMixin, forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), label="Предмет", empty_label="— выберите предмет —")
    text = forms.CharField(label="Билеты (по одному в строке)", widget=forms.Textarea(attrs={"rows": 12}), help_text="Номера присваиваются автоматически")
    def clean_text(self):
        value = self.cleaned_data["text"]
        if len(value.splitlines()) > MAX_LINES:
            raise forms.ValidationError(f"Слишком много строк (максимум {MAX_LINES}).")
        return value
    def lines(self):
        return [line for raw in self.cleaned_data["text"].splitlines() if (line := NUMBER_PREFIX.sub("", raw.strip()))]
    @transaction.atomic
    def save(self):
        subject = self.cleaned_data["subject"]
        lines = self.lines()
        last = Ticket.objects.filter(subject=subject).aggregate(m=Max("number"))["m"] or 0
        Ticket.objects.bulk_create([Ticket(subject=subject,number=last+i,text=line) for i,line in enumerate(lines,1)])
        return len(lines)
