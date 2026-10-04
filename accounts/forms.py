from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction

from config.forms import BootstrapFormMixin

from .models import Profile, StudyGroup


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    """Регистрация: логин, пароль (дважды) и выбор группы."""

    group = forms.ModelChoiceField(
        queryset=StudyGroup.objects.all(), label="Группа", empty_label="— выберите группу —"
    )

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(user=user, group=self.cleaned_data["group"])
        return user


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    """Обычная форма входа Django, но с оформлением Bootstrap."""
