from datetime import datetime

from ..constants import ARG_TZ, DIAS_ES, MESES_ES
from ..database import CAMPOS, todos, uno
from ..logging_utils import log


def fecha_larga(fecha_iso):
    try:
        d = datetime.strptime(str(fecha_iso), "%Y-%m-%d")
    except (ValueError, TypeError):
        return fecha_iso or ""
    return f"{DIAS_ES[d.weekday()]} {d.day} de {MESES_ES[d.month - 1]}"


def hoy_str():
    return datetime.now(ARG_TZ).strftime("%Y-%m-%d")


def obtener_local(uid, usuario=None):
    r = uno(f"SELECT {CAMPOS} FROM locales WHERE id=%s", (uid,))
    if r and usuario is not None and r["usuario"] != usuario:
        log("SEGURIDAD", f"⛔ '{usuario}' intentó acceder al local {uid} de '{r['usuario']}'")
        return None
    return r


def locales_de_hoy(usuario):
    return todos(f"SELECT {CAMPOS} FROM locales WHERE usuario=%s AND fecha=%s ORDER BY id DESC",
                 (usuario, hoy_str()))


def contar_locales_hoy(usuario):
    return uno("SELECT COUNT(*) AS n FROM locales WHERE usuario=%s AND fecha=%s",
               (usuario, hoy_str()))["n"]


def proximo_numero_del_dia(usuario):
    return uno("SELECT COALESCE(MAX(numero),0)+1 AS n FROM locales WHERE usuario=%s AND fecha=%s",
               (usuario, hoy_str()))["n"]


def calles_de_hoy(usuario):
    filas = todos("SELECT direccion FROM locales WHERE usuario=%s AND fecha=%s", (usuario, hoy_str()))
    calles = set()
    for f in filas:
        partes = f["direccion"].rsplit(" ", 1)
        calles.add(partes[0] if len(partes) == 2 else f["direccion"])
    return sorted(calles)
