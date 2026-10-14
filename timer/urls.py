from django.urls import path
from . import views

app_name = 'timer'

urlpatterns = [
    path('', views.index, name='index'),
    path('sessions/', views.sessions, name='sessions'),  # Наш новый адрес!
]
