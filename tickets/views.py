from django.shortcuts import render


def index(request):
    """Страница-заглушка раздела «Билеты». Замени на настоящую страницу."""
    return render(request, "tickets/index.html")
