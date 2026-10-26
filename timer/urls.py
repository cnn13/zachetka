from django.urls import path

from . import views

app_name = "timer"

urlpatterns = [
    path("", views.index, name="index"),
    path("save_session/", views.save_session, name="save_session"),
]
