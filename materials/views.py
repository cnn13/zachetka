import json
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MaterialUploadForm
from .models import Material, MaterialFavorite


@login_required
def index(request):
    """Архив. Все критерии поиска действуют одновременно и остаются в URL."""
    visible = Material.objects.filter(is_hidden=False)
    qs = visible.select_related("subject").prefetch_related("tags")
    selected = {key: request.GET.get(key, "").strip() for key in ("q", "subject", "teacher", "course", "year")}

    if selected["q"]:
        qs = qs.filter(Q(title__icontains=selected["q"]) | Q(teacher__icontains=selected["q"]) | Q(tags__name__icontains=selected["q"])).distinct()
    if selected["subject"]:
        qs = qs.filter(subject_id=selected["subject"]) if selected["subject"].isdigit() else qs.none()
    if selected["teacher"]:
        qs = qs.filter(teacher=selected["teacher"])
    for field in ("course", "year"):
        if selected[field]:
            qs = qs.filter(**{field: int(selected[field])}) if selected[field].isdigit() else qs.none()

    subjects = visible.order_by("subject__name").values("subject_id", "subject__name").distinct()
    teachers = visible.order_by("teacher").values_list("teacher", flat=True).distinct()
    courses = visible.order_by("course").values_list("course", flat=True).distinct()
    years = visible.order_by("year").values_list("year", flat=True).distinct()
    favorite_ids = set(MaterialFavorite.objects.filter(user=request.user, material__is_hidden=False).values_list("material_id", flat=True))
    for item in qs:
        item.is_favorite = item.pk in favorite_ids
    return render(request, "materials/index.html", {
        "materials": qs, "subjects": subjects, "teachers": teachers,
        "courses": courses, "years": years, "selected": selected,
    })


@login_required
def download(request, pk):
    """Никакой прямой выдачи из MEDIA_ROOT; скрытый файл отвечает 404."""
    material = get_object_or_404(Material.objects.filter(is_hidden=False), pk=pk)
    if not material.file:
        raise Http404("Не найдено")
    try:
        stream = material.file.open("rb")
    except (FileNotFoundError, OSError):
        raise Http404("Не найдено")
    as_attachment = request.GET.get("download") == "1"
    response = FileResponse(stream, as_attachment=as_attachment, filename=Path(material.file.name).name)
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
def upload(request):
    """Сервер проверяет файл в форме и валидаторе модели."""
    form = MaterialUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save(user=request.user)
        messages.success(request, "Материал загружен.")
        return redirect("materials:index")
    return render(request, "materials/upload.html", {"form": form})


@login_required
@require_POST
def toggle_favorite(request, pk):
    """Состояние избранного сохраняется в базе, а не только в браузере."""
    material = get_object_or_404(Material, pk=pk, is_hidden=False)
    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Некорректный запрос"}, status=400)
    if not isinstance(payload.get("favorite"), bool):
        return JsonResponse({"error": "Поле favorite должно быть логическим"}, status=400)
    favorite = payload["favorite"]
    if favorite:
        MaterialFavorite.objects.get_or_create(user=request.user, material=material)
    else:
        MaterialFavorite.objects.filter(user=request.user, material=material).delete()
    return JsonResponse({"ok": True, "favorite": favorite})
