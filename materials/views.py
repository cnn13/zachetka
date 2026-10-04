from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import MaterialUploadForm
from .models import Material


def index(request):
    """Архив материалов: список загруженного."""
    materials = Material.objects.select_related("subject").prefetch_related("tags")
    return render(request, "materials/index.html", {"materials": materials})


@login_required
def upload(request):
    """Задача 2.4: форма загрузки материала (только для вошедших пользователей)."""
    form = MaterialUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save(user=request.user)
        messages.success(request, "Материал загружен.")
        return redirect("materials:index")
    return render(request, "materials/upload.html", {"form": form})
