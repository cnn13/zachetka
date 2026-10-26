import json
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .forms import RegisterForm
from .models import Profile, StudyGroup


def index(request):
    profile = None
    if request.user.is_authenticated:
        profile = Profile.objects.select_related("group").filter(user=request.user).first()
    return render(request, "accounts/index.html", {"profile": profile, "groups": StudyGroup.objects.all()})


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        next_url = request.GET.get("next") or request.POST.get("next")
        if next_url and next_url.startswith("/") and not next_url.startswith("//"):
            return redirect(next_url)
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form, "has_groups": StudyGroup.objects.exists()})


@login_required
@require_POST
def update_profile(request):
    """Смена группы только на существующую в справочнике."""
    try:
        data = json.loads(request.body)
        name = str(data.get("group", "")).strip()
        group = StudyGroup.objects.get(name=name)
    except (json.JSONDecodeError, ValueError, StudyGroup.DoesNotExist):
        return JsonResponse({"error": "Выберите существующую группу"}, status=400)
    Profile.objects.update_or_create(user=request.user, defaults={"group": group})
    return JsonResponse({"ok": True, "group": group.name})
