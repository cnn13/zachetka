#!/usr/bin/env python3
"""Восстановление локальной SQLite-копии. Выполнять при остановленном сайте."""
import os
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("DATA_DIR", str(BASE_DIR))).expanduser()
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", str(DATA_DIR / "media"))).expanduser()


def restore(archive: Path) -> None:
    if os.environ.get("DATABASE_URL"):
        raise RuntimeError("PostgreSQL восстановите через pg_restore (см. README).")
    with ZipFile(archive) as src:
        if src.testzip():
            raise ValueError("Резервная копия повреждена")
        names = src.namelist()
        if "db.sqlite3" not in names:
            raise ValueError("Это не архив SQLite")
        if any(name.startswith("/") or ".." in Path(name).parts for name in names):
            raise ValueError("В архиве обнаружен небезопасный путь")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        # Не перезаписывайте работающую базу — остановите веб-сервер.
        temporary = DATA_DIR / "db.sqlite3.restore-tmp"
        try:
            with src.open("db.sqlite3") as db, temporary.open("wb") as out:
                shutil.copyfileobj(db, out)
            temporary.replace(DATA_DIR / "db.sqlite3")
        finally:
            temporary.unlink(missing_ok=True)
        for name in names:
            if name.startswith("media/") and not name.endswith("/"):
                dst = MEDIA_ROOT / Path(name).relative_to("media")
                dst.parent.mkdir(parents=True, exist_ok=True)
                with src.open(name) as uploaded, dst.open("wb") as out:
                    shutil.copyfileobj(uploaded, out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Использование: python scripts/restore.py путь/к/backup.zip")
    restore(Path(sys.argv[1]))
    print("Данные восстановлены. Проверьте пользователей, группы и файлы.")
