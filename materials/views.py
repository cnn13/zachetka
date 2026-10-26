from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .forms import MaterialUploadForm
from .models import Favorite, Material


@ensure_csrf_cookie
def index(request):
    """Архив материалов: список загруженного."""
    materials = Material.objects.select_related("subject").prefetch_related("tags")
    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(
            Favorite.objects.filter(user=request.user).values_list("material_id", flat=True)
        )
    return render(
        request, "materials/index.html", {"materials": materials, "favorite_ids": favorite_ids}
    )


@login_required
def upload(request):
    """Задача 2.4: форма загрузки материала (только для вошедших пользователей)."""
    form = MaterialUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save(user=request.user)
        messages.success(request, "Материал загружен.")
        return redirect("materials:index")
    return render(request, "materials/upload.html", {"form": form})


@require_POST
def toggle_favorite(request, material_id):
    """Добавить материал в избранное или убрать из него (запрос из JS)."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Нужно войти"}, status=401)
    material = get_object_or_404(Material, pk=material_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, material=material)
    if not created:
        favorite.delete()
    return JsonResponse({"favorite": created})
