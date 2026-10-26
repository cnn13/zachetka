from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("materials/", include("materials.urls")),
    path("tickets/", include("tickets.urls")),
    path("timer/", include("timer.urls")),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
]

# Не добавляем static(settings.MEDIA_URL, ...): иначе любой сможет открыть файл
# по прямой ссылке, минуя вход и проверку признака «Скрыт».
