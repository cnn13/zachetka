"""Статистика завершённых помодоро и сохранение сессий на сервере."""
import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import PomodoroSession
from tickets.models import Subject


def _stats(request):
    now = timezone.now()
    today = timezone.localdate()
    sessions = PomodoroSession.objects.filter(user=request.user)
    today_minutes = sessions.filter(created_at__date=today).aggregate(total=Sum("duration_minutes"))["total"] or 0
    week_minutes = sessions.filter(created_at__gte=now-timedelta(days=7)).aggregate(total=Sum("duration_minutes"))["total"] or 0
    return {"today_hours": round(today_minutes / 60, 2), "week_hours": round(week_minutes / 60, 2)}


@login_required
def index(request):
    context = _stats(request)
    context["sessions"] = PomodoroSession.objects.filter(user=request.user)[:5]
    context["subjects"] = Subject.objects.all()
    return render(request, "timer/index.html", context)


@login_required
@require_POST
def save_session(request):
    """Фиксируем только полную 25-минутную сессию из клиентского таймера."""
    try:
        payload = json.loads(request.body)
        subject_name = str(payload.get("subject_name", "")).strip()[:200]
        duration = int(payload.get("duration_minutes", 0))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "Некорректные параметры"}, status=400)
    if not subject_name or duration != 25:
        return JsonResponse({"error": "Допускается только завершённая сессия 25 минут"}, status=400)
    # token используется как идемпотентный идентификатор завершения браузерного цикла.
    # Защита от двойной отправки хранится в БД, не в памяти процесса.
    token = str(payload.get("token", ""))
    if len(token) < 16 or len(token) > 100 or not all(c.isalnum() or c in "-_" for c in token):
        return JsonResponse({"error": "Недействительный идентификатор сессии"}, status=400)
    session, created = PomodoroSession.objects.get_or_create(
        user=request.user, client_token=token,
        defaults={"subject_name": subject_name, "duration_minutes": 25},
    )
    return JsonResponse({"ok": True, "created": created, "id": session.pk})


@login_required
def sessions(request):
    all_sessions = PomodoroSession.objects.filter(user=request.user)
    context = _stats(request)
    context["sessions"] = all_sessions[:200]
    context["session_count"] = all_sessions.count()
    context["total_hours"] = round((all_sessions.aggregate(x=Sum("duration_minutes"))["x"] or 0) / 60, 2)
    # Неделя, включая сегодня, для простого графика активности.
    day_stats = {}
    for item in all_sessions.filter(created_at__date__gte=timezone.localdate()-timedelta(days=6)):
        day = timezone.localtime(item.created_at).date()
        day_stats[day] = day_stats.get(day, 0) + item.duration_minutes
    max_minutes = max(day_stats.values(), default=1)
    days = [timezone.localdate()-timedelta(days=d) for d in range(6, -1, -1)]
    context["week_chart"] = [{"label": day.strftime("%d.%m"), "minutes": day_stats.get(day, 0), "height": round(100*day_stats.get(day, 0)/max_minutes)} for day in days]
    return render(request, "timer/sessions.html", context)
