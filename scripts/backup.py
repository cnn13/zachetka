#!/usr/bin/env python3
"""Резервная копия БД + media в ZIP; сохраняем последние семь успешных копий."""
from __future__ import annotations

import os
import sqlite3
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse
from zipfile import ZIP_DEFLATED, ZipFile

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("DATA_DIR", str(BASE_DIR))).expanduser()
DB_URL = os.environ.get("DATABASE_URL", "")
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", str(DATA_DIR / "media"))).expanduser()
BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", str(DATA_DIR / "backups"))).expanduser()
KEEP = 7


def create_backup() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    BACKUP_DIR.chmod(0o700)  # Копия содержит пользовательские файлы и пароли в виде хешей.
    moment = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    target = BACKUP_DIR / f"zachetka-{moment}.zip"
    # Файл .tmp не учитывается как готовая резервная копия.
    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        if DB_URL:
            if urlparse(DB_URL).scheme not in ("postgresql", "postgres"):
                raise RuntimeError("Поддерживаются PostgreSQL и SQLite")
            # pg_dump читает согласованный снимок базы без остановки приложения.
            # Пароль держим только в окружении, он не появится в параметрах процесса.
            uri = urlparse(DB_URL)
            env = {**os.environ, "PGCONNECT_TIMEOUT": "15", "PGPASSWORD": unquote(uri.password or "")}
            if os.environ.get("DB_SSLMODE"):
                env["PGSSLMODE"] = os.environ["DB_SSLMODE"]
            result = subprocess.run(
                ["pg_dump", "--host", uri.hostname or "localhost",
                 "--port", str(uri.port or 5432), "--username", unquote(uri.username or ""),
                 "--dbname", unquote(uri.path.lstrip("/")),
                 "--format=custom", "--file", str(work / "database.dump")],
                env=env, capture_output=True, text=True,
            )
            if result.returncode:
                raise RuntimeError(f"pg_dump завершился с ошибкой: {result.stderr.strip()}")
        else:
            source = DATA_DIR / "db.sqlite3"
            if not source.is_file():
                raise FileNotFoundError(f"База данных отсутствует: {source}")
            # SQLite online-backup даёт консистентную копию даже при активном сайте.
            with sqlite3.connect(source) as src, sqlite3.connect(work / "db.sqlite3") as dst:
                src.backup(dst)

        pending = BACKUP_DIR / f".{target.name}.tmp"
        try:
            # Создаём файл с правами 0600, чтобы другие пользователи его не прочитали.
            fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as output, ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
                data_file = work / ("database.dump" if DB_URL else "db.sqlite3")
                archive.write(data_file, data_file.name)
                if MEDIA_ROOT.exists():
                    for file in MEDIA_ROOT.rglob("*"):
                        if file.is_file():
                            archive.write(file, "media/" + file.relative_to(MEDIA_ROOT).as_posix())
            pending.replace(target)
        finally:
            pending.unlink(missing_ok=True)

    backups = sorted(BACKUP_DIR.glob("zachetka-*.zip"), reverse=True)
    for old in backups[KEEP:]:
        old.unlink()
    return target


if __name__ == "__main__":
    print("Резервная копия:", create_backup())
