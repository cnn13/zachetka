import json

from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import RegisterForm
from .models import Profile, StudyGroup


def index(request):
    """Раздел «Профиль»: данные пользователя или ссылки на вход и регистрацию."""
    profile = None
    if request.user.is_authenticated:
        profile = Profile.objects.select_related("group").filter(user=request.user).first()
    return render(
        request,
        "accounts/index.html",
        {"profile": profile, "groups": StudyGroup.objects.all()},
    )


def register(request):
    """Задача 2.3 (ФТ-01): регистрация с выбором группы, после неё сразу вход."""
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(
        request,
        "accounts/register.html",
        {"form": form, "has_groups": StudyGroup.objects.exists()},
    )


@require_POST
def update_profile(request):
    """Смена учебной группы в профиле (запрос из JS, issue #5)."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Нужно войти"}, status=401)
    try:
        name = str(json.loads(request.body or b"{}").get("group", "")).strip()
    except (ValueError, AttributeError):
        name = ""
    # SQLite не сравнивает кириллицу без учёта регистра, поэтому сравниваем в Python
    group = next(
        (g for g in StudyGroup.objects.all() if g.name.casefold() == name.casefold()), None
    )
    if group is None:
        return JsonResponse({"error": "Такой группы нет в списке"}, status=400)
    Profile.objects.update_or_create(user=request.user, defaults={"group": group})
    return JsonResponse({"group": group.name})
