from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import BulkTicketForm
from .models import Subject


def index(request):
    """Список билетов по предметам с подсчетом процента готовности."""
    subjects = Subject.objects.prefetch_related("tickets")
    
    # Считаем процент готовности для каждого предмета динамически
    for subject in subjects:
        all_tickets = subject.tickets.all()
        total_count = all_tickets.count()
        
        if total_count > 0:
            # Считаем только билеты со статусом 'learned'
            learned_count = all_tickets.filter(status='learned').count()
            subject.progress_percentage = int((learned_count / total_count) * 100)
        else:
            subject.progress_percentage = 0 # Если билетов нет, то 0%
            
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
