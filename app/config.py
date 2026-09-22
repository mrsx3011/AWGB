import os
import sys
from datetime import timedelta

import pymysql.cursors


def env(nombre, default=None):
    valor = os.environ.get(nombre, default)
    if valor in (None, ""):
        print(f"❌ Falta la variable de entorno: {nombre}", flush=True)
        sys.exit(1)
    return valor


class Config:
    SECRET_KEY = env("KEY_SECRET")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)


TELEGRAM_TOKEN = env("TELEGRAM_TOKEN")
CHAT_ID = env("CHAT_ID")

DB_CONFIG = dict(
    host=env("DB_HOST"),
    port=int(os.environ.get("DB_PORT", 3306)),
    user=env("DB_USER"),
    password=env("DB_PASSWORD"),
    database=env("DB_NAME"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True,
    connect_timeout=10,
)
