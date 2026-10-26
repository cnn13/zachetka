import json
from datetime import timedelta

from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.formats import localize
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from tickets.models import Subject

from .models import PomodoroSession


def _hours(sessions):
    minutes = sessions.aggregate(total=Sum("duration_minutes"))["total"] or 0
    return round(minutes / 60, 1)


def _stats(user):
    """Сессии за сегодня и часы за сегодня и за 7 дней (задача 3.7)."""
    today = timezone.localdate()
    mine = PomodoroSession.objects.filter(user=user)
    today_sessions = mine.filter(created_at__date=today)
    week_sessions = mine.filter(created_at__date__gte=today - timedelta(days=6))
    return today_sessions, _hours(today_sessions), _hours(week_sessions)


@ensure_csrf_cookie
def index(request):
    """Страница таймера: выбор предмета, сессии и часы текущего пользователя."""
    context = {"subjects": Subject.objects.all(), "sessions": [], "today_hours": 0, "week_hours": 0}
    if request.user.is_authenticated:
        sessions, today_hours, week_hours = _stats(request.user)
        context.update(sessions=sessions, today_hours=today_hours, week_hours=week_hours)
    return render(request, "timer/index.html", context)


@require_POST
def save_session(request):
    """Задача 2.8: сохранить завершённую сессию (запрос из JS после 25 минут)."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Нужно войти"}, status=401)
    try:
        data = json.loads(request.body or b"{}")
        duration = int(data.get("duration_minutes", 25))
    except (ValueError, TypeError, AttributeError):
        return JsonResponse({"error": "Неверные данные"}, status=400)
    if not 1 <= duration <= 120:
        return JsonResponse({"error": "Неверная длительность"}, status=400)

    session = PomodoroSession.objects.create(
        user=request.user,
        subject_name=str(data.get("subject_name", ""))[:200],
        duration_minutes=duration,
    )
    _, today_hours, week_hours = _stats(request.user)
    return JsonResponse(
        {
            "time": timezone.localtime(session.created_at).strftime("%H:%M"),
            "subject_name": session.subject_name,
            "duration_minutes": session.duration_minutes,
            "today_hours": localize(today_hours),
            "week_hours": localize(week_hours),
        }
    )
