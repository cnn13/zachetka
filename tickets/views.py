from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import BulkTicketForm
from .models import Subject


def index(request):
    """Список билетов по предметам."""
    subjects = Subject.objects.prefetch_related("tickets")
    return render(request, "tickets/index.html", {"subjects": subjects})


@login_required
def bulk_add(request):
    """Задача 2.7: создание билетов из вставленного текста."""
    form = BulkTicketForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        count = form.save()
        messages.success(request, f"Создано билетов: {count}")
        return redirect("tickets:index")
    return render(request, "tickets/bulk_add.html", {"form": form, "has_subjects": Subject.objects.exists()})
