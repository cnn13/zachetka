from django.shortcuts import render


def index(request):
    """Страница-заглушка раздела «Таймер». Замени на настоящую страницу."""
    return render(request, "timer/index.html")
