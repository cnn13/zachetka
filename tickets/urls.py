from django.urls import path
from . import views

app_name = "tickets"
urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.bulk_add, name="bulk_add"),
    path("random/", views.random_ticket, name="random"),
    path("<int:pk>/status/", views.set_status, name="set_status"),
]
