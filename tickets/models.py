from django.db import models

# Задача 1.6 (Б): создай здесь модели Subject и Ticket.
# Subject: name (название предмета).
# Ticket: subject (ForeignKey на Subject), number (номер билета), text (текст вопроса).
# Потом зарегистрируй модели в admin.py и выполни:
#   python manage.py makemigrations
#   python manage.py migrate
