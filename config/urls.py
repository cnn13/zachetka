from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("materials/", include("materials.urls")),  # Архив (А)
    path("tickets/", include("tickets.urls")),      # Билеты (Б)
    path("timer/", include("timer.urls")),          # Таймер (Т)
    path("accounts/", include("accounts.urls")),    # Профиль (М)
    path("admin/", admin.site.urls),
]

# Во время разработки Django сам отдаёт загруженные файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
