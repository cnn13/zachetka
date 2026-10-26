import os
from django.core.exceptions import ValidationError

MAX_SIZE = 20 * 1024 * 1024
SIGNATURES = {
    ".pdf": b"%PDF",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".png": b"\x89PNG\r\n\x1a\n",
}
ALLOWED_EXTENSIONS = [ext.lstrip(".") for ext in SIGNATURES]


def validate_material_file(file):
    """Проверяем реальный размер и заголовок файла на сервере."""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in SIGNATURES:
        raise ValidationError("Допустимы только файлы PDF, JPG и PNG.")
    if file.size > MAX_SIZE:
        raise ValidationError("Файл больше 20 МБ. Выберите файл размером до 20 МБ.")
    head = file.read(len(SIGNATURES[ext]))
    file.seek(0)
    if not head.startswith(SIGNATURES[ext]):
        raise ValidationError("Содержимое файла не совпадает с его расширением.")
