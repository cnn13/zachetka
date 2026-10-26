from django.urls import path
from . import views

app_name = "materials"
urlpatterns = [
    path("<int:pk>/toggle_favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("", views.index, name="index"),
    path("upload/", views.upload, name="upload"),
    path("<int:pk>/file/", views.download, name="download"),
]
