import os

from django.core.exceptions import ValidationError

MAX_SIZE = 20 * 1024 * 1024  # 20 МБ (НФТ-05)

# Допустимые расширения и «подпись» — первые байты настоящего файла
SIGNATURES = {
    ".pdf": b"%PDF",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
    ".png": b"\x89PNG\r\n\x1a\n",
}
ALLOWED_EXTENSIONS = [ext.lstrip(".") for ext in SIGNATURES]


def validate_material_file(file):
    """Разрешены только PDF, JPG и PNG, не больше 20 МБ."""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in SIGNATURES:
        raise ValidationError("Допустимы только файлы PDF, JPG и PNG.")
    if file.size > MAX_SIZE:
        raise ValidationError("Файл больше 20 МБ.")
    head = file.read(len(SIGNATURES[ext]))
    file.seek(0)
    if not head.startswith(SIGNATURES[ext]):
        raise ValidationError("Содержимое файла не совпадает с его расширением.")
