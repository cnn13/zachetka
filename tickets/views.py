import json
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from urllib.parse import urlencode
from django.views.decorators.http import require_POST

from .forms import BulkTicketForm
from .models import Subject, Ticket, TicketProgress


@login_required
def index(request):
    """Билеты и личные оценки, которые не теряются при перезапуске."""
    subjects = list(Subject.objects.prefetch_related("tickets"))
    progress = dict(TicketProgress.objects.filter(user=request.user).values_list("ticket_id", "status"))
    for subject in subjects:
        all_tickets = list(subject.tickets.all())
        for ticket in all_tickets:
            ticket.current_status = progress.get(ticket.pk, TicketProgress.UNKNOWN)
        subject.progress_percentage = round(100 * sum(t.current_status == TicketProgress.LEARNED for t in all_tickets) / len(all_tickets)) if all_tickets else 0
    return render(request, "tickets/index.html", {"subjects": subjects, "statuses": TicketProgress.STATUS_CHOICES})


@login_required
@require_POST
def set_status(request, pk):
    """Менять оценку билета можно только от имени текущего пользователя."""
    ticket = get_object_or_404(Ticket, pk=pk)
    try:
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
    except (ValueError, TypeError):
        return JsonResponse({"error":"Некорректный JSON"}, status=400)
    status = data.get("status", "")
    if status not in dict(TicketProgress.STATUS_CHOICES):
        raise Http404("Неизвестная оценка")
    TicketProgress.objects.update_or_create(
        user=request.user, ticket=ticket, defaults={"status": status}
    )
    if request.content_type == "application/json":
        return JsonResponse({"ok":True,"status":status})
    # Возвращаемся на список либо на случайный билет, но не на чужой сайт.
    if request.POST.get("from_random") == "1":
        subject = str(ticket.subject_id) if request.POST.get("subject") == str(ticket.subject_id) else ""
        url = reverse("tickets:random")
        return redirect(f"{url}?{urlencode({'subject': subject})}" if subject else url)
    return redirect("tickets:index")


@login_required
def random_ticket(request):
    """Пока есть слабые билеты, 'выучил' не выдаём."""
    subject_raw = request.GET.get("subject", "")
    subjects = Subject.objects.all()
    candidates = Ticket.objects.select_related("subject")
    if subject_raw:
        if not subject_raw.isdigit():
            raise Http404("Предмет не найден")
        subject = get_object_or_404(Subject, pk=int(subject_raw))
        candidates = candidates.filter(subject=subject)

    progress = dict(TicketProgress.objects.filter(user=request.user).values_list("ticket_id", "status"))
    tickets = list(candidates)
    weak = [t for t in tickets if progress.get(t.pk, TicketProgress.UNKNOWN) != TicketProgress.LEARNED]
    pool = weak if weak else tickets
    ticket = random.choice(pool) if pool else None
    current_status = progress.get(ticket.pk, TicketProgress.UNKNOWN) if ticket else None
    return render(request, "tickets/random.html", {
        "ticket": ticket, "subjects": subjects, "current_status": current_status,
        "selected_subject": subject_raw,
    })


@login_required
def bulk_add(request):
    form = BulkTicketForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        count = form.save()
        messages.success(request, f"Создано билетов: {count}")
        return redirect("tickets:index")
    return render(request, "tickets/bulk_add.html", {"form": form, "has_subjects": Subject.objects.exists()})
