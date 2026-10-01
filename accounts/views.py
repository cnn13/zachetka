from django.shortcuts import render


def index(request):
    """Страница-заглушка раздела «Профиль». Замени на настоящую страницу."""
    return render(request, "accounts/index.html")
