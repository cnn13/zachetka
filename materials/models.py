from django.db import models

# Задача 1.4 (А): создай здесь модель Material.
# Поля: title (название), subject (предмет), teacher (преподаватель),
#       course (курс), year (год), file (FileField, upload_to="materials/"),
#       created_at (дата загрузки, auto_now_add=True).
# Потом зарегистрируй модель в admin.py и выполни:
#   python manage.py makemigrations
#   python manage.py migrate
