from django.urls import path

from . import views

app_name = "tickets"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.bulk_add, name="bulk_add"),
    path("update_status/<int:ticket_id>/", views.update_status, name="update_status"),
]
