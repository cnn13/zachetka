from django.shortcuts import render


def index(request):
    """Страница-заглушка раздела «Архив материалов». Замени на настоящую страницу."""
    return render(request, "materials/index.html")
