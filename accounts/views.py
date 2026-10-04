from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegisterForm
from .models import Profile, StudyGroup


def index(request):
    """Раздел «Профиль»: данные пользователя или ссылки на вход и регистрацию."""
    profile = None
    if request.user.is_authenticated:
        profile = Profile.objects.select_related("group").filter(user=request.user).first()
    return render(request, "accounts/index.html", {"profile": profile})


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
