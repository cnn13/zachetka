import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .forms import BulkTicketForm
from .models import Subject, Ticket, TicketStatus


def subject_progress(user, subject):
    """Процент билетов предмета, отмеченных пользователем как «выучил» (задача 3.6)."""
    total = subject.tickets.count()
    if not total or not user.is_authenticated:
        return 0
    learned = TicketStatus.objects.filter(
        user=user, ticket__subject=subject, status=TicketStatus.LEARNED
    ).count()
    return round(learned * 100 / total)


@ensure_csrf_cookie
def index(request):
    """Список билетов по предметам со статусами и готовностью текущего пользователя."""
    subjects = list(Subject.objects.prefetch_related("tickets"))

    statuses = {}
    if request.user.is_authenticated:
        statuses = dict(
            TicketStatus.objects.filter(user=request.user).values_list("ticket_id", "status")
        )

    for subject in subjects:
        tickets = list(subject.tickets.all())
        for ticket in tickets:
            ticket.status = statuses.get(ticket.id, TicketStatus.DONT_KNOW)
        learned = sum(1 for t in tickets if t.status == TicketStatus.LEARNED)
        subject.ticket_list = tickets
        subject.progress_percentage = round(learned * 100 / len(tickets)) if tickets else 0

    return render(request, "tickets/index.html", {"subjects": subjects})


@require_POST
def update_status(request, ticket_id):
    """Задача 3.5: сохранить статус билета для текущего пользователя (запрос из JS)."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Нужно войти"}, status=401)

    ticket = get_object_or_404(Ticket, pk=ticket_id)
    try:
        status = json.loads(request.body or b"{}").get("status")
    except (ValueError, AttributeError):
        status = None
    if status not in dict(TicketStatus.STATUS_CHOICES):
        return JsonResponse({"error": "Неизвестный статус"}, status=400)

    TicketStatus.objects.update_or_create(
        user=request.user, ticket=ticket, defaults={"status": status}
    )
    return JsonResponse({"status": status, "progress": subject_progress(request.user, ticket.subject)})


@login_required
def bulk_add(request):
    """Задача 2.7: создание билетов из вставленного текста."""
    form = BulkTicketForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        count = form.save()
        messages.success(request, f"Создано билетов: {count}")
        return redirect("tickets:index")
    return render(request, "tickets/bulk_add.html", {"form": form, "has_subjects": Subject.objects.exists()})
