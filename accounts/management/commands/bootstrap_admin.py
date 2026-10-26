"""Создаёт или обновляет учётную запись администратора по секретам окружения."""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Создать/обновить администратора из ADMIN_USERNAME и ADMIN_PASSWORD"

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "admin676967")
        password = os.environ.get("ADMIN_PASSWORD", "")
        if not password:
            raise CommandError("Задайте ADMIN_PASSWORD в переменных окружения, не в исходниках.")
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)  # Django хранит не пароль, а защищённый хеш.
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Администратор {username}: {'создан' if created else 'обновлён'}."))
