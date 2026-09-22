import traceback
from datetime import datetime

import requests

from ..config import CHAT_ID, TELEGRAM_TOKEN
from ..constants import ARG_TZ
from ..database import ejecutar, uno
from ..logging_utils import log


def _telegram(metodo, **kwargs):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{metodo}"
    resp = requests.post(url, timeout=60, **kwargs)
    log("TELEGRAM", f"{metodo} -> HTTP {resp.status_code}")
    if not resp.ok:
        log("TELEGRAM", f"❌ Respuesta de Telegram: {resp.text[:300]}")
    return resp


def _post_telegram_texto(texto):
    resp = _telegram("sendMessage", json={"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"})
    if resp.status_code == 400:
        log("TELEGRAM", "↩️ Reintentando sin Markdown")
        resp = _telegram("sendMessage", json={"chat_id": CHAT_ID, "text": texto})
    resp.raise_for_status()


def enviar_reporte_telegram(uid, encabezado=None):
    from .scheduler_service import recalcular_horarios_pendientes

    log("ENVIO", f"▶️ Iniciando envío del local id={uid} (re-envío={bool(encabezado)})")
    try:
        r = uno("SELECT id AS uid, usuario, nombre, direccion, objecion, numero, estado, foto, foto_mime "
                "FROM locales WHERE id=%s", (uid,))
        if not r:
            log("ENVIO", f"⚠️ El local {uid} ya no existe en la BD, se cancela")
            return
        if encabezado is None and r["estado"] == "enviado":
            log("ENVIO", f"⚠️ El local {uid} ya estaba enviado, se omite")
            return

        if encabezado:
            _post_telegram_texto(encabezado)

        if r["foto"]:
            log("ENVIO", f"📷 Enviando foto ({len(r['foto'])} bytes)")
            resp = _telegram(
                "sendPhoto",
                data={"chat_id": CHAT_ID, "caption": f"📌 Local N° {r['numero']}"},
                files={"photo": (f"local_{uid}.jpg", r["foto"], r["foto_mime"] or "image/jpeg")},
            )
            resp.raise_for_status()
        else:
            log("ENVIO", "⚠️ El local no tiene foto en la BD")

        _post_telegram_texto(f"{r['nombre']}")
        _post_telegram_texto(f"{r['direccion']}")
        _post_telegram_texto(f" {r['objecion'] if r['objecion'] else 'Sin objeción registrada.'}")

        if encabezado is None:
            ejecutar("UPDATE locales SET estado='enviado', hora_envio_real=%s WHERE id=%s",
                     (datetime.now(ARG_TZ).strftime("%H:%M:%S"), uid))
            recalcular_horarios_pendientes(r["usuario"])
        log("ENVIO", f"✅ Local id={uid} enviado correctamente")
    except Exception as e:
        log("ENVIO", f"❌ FALLÓ el envío del local {uid}: {e!r}")
        log("ENVIO", traceback.format_exc())
        raise
