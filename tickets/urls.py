from django.urls import path

from . import views

app_name = "tickets"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.bulk_add, name="bulk_add"),
]
