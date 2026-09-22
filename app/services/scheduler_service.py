import random
import threading
from datetime import datetime, timedelta

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
from apscheduler.schedulers.background import BackgroundScheduler

from ..constants import (ARG_TZ, BUFFER_INICIAL_MINUTOS, HORA_APERTURA, HORA_CIERRE,
                         INTERVALO_MINIMO_MINUTOS, MARGEN_JITTER_MINUTOS)
from ..database import CAMPOS, ejecutar, todos
from ..logging_utils import log
from .locales import hoy_str

lock = threading.Lock()
scheduler = BackgroundScheduler(timezone=ARG_TZ)


def _listener(event):
    if event.code == EVENT_JOB_ERROR:
        log("SCHEDULER", f"❌ El job {event.job_id} FALLÓ: {event.exception!r}")
        log("SCHEDULER", event.traceback or "")
    elif event.code == EVENT_JOB_MISSED:
        log("SCHEDULER", f"⚠️ El job {event.job_id} se perdió su horario (misfire)")
    else:
        log("SCHEDULER", f"✅ Job {event.job_id} ejecutado")


scheduler.add_listener(_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)
scheduler.start()


def agendar(uid, run_date):
    from .telegram_service import enviar_reporte_telegram

    scheduler.add_job(
        func=enviar_reporte_telegram, trigger="date", run_date=run_date,
        id=f"job_{uid}", replace_existing=True, args=[uid],
        misfire_grace_time=3600,
    )
    log("SCHEDULER", f"🕒 Job job_{uid} agendado para {run_date.strftime('%Y-%m-%d %H:%M:%S')}")


def reprogramar_jobs_pendientes():
    log("SCHEDULER", "♻️ Recreando jobs pendientes desde la BD...")
    ahora = datetime.now(ARG_TZ)
    pendientes = todos(f"SELECT {CAMPOS} FROM locales WHERE estado='pendiente' AND fecha=%s", (hoy_str(),))
    usuarios = set()
    for r in pendientes:
        usuarios.add(r["usuario"])
        if not r["hora_manual"]:
            continue
        try:
            run_date = datetime.fromisoformat(r["hora_programada_iso"])
        except ValueError:
            continue
        if run_date <= ahora:
            run_date = ahora + timedelta(minutes=INTERVALO_MINIMO_MINUTOS)
        agendar(r["uid"], run_date)
    for u in usuarios:
        recalcular_horarios_pendientes(u)
    log("SCHEDULER", f"♻️ Listo: {len(pendientes)} pendiente(s), {len(usuarios)} usuario(s)")


def recalcular_horarios_pendientes(usuario):
    with lock:
        ahora = datetime.now(ARG_TZ)
        apertura = ARG_TZ.localize(datetime.combine(ahora.date(), HORA_APERTURA))
        cierre = ARG_TZ.localize(datetime.combine(ahora.date(), HORA_CIERRE))

        pendientes = todos(
            "SELECT id AS uid FROM locales WHERE usuario=%s AND fecha=%s "
            "AND estado='pendiente' AND hora_manual=0 ORDER BY id",
            (usuario, ahora.strftime("%Y-%m-%d")))
        n = len(pendientes)
        log("HORARIOS", f"Recalculando para '{usuario}': {n} pendiente(s) automático(s)")
        if n == 0:
            return

        fin_calculo = cierre
        if ahora < apertura:
            inicio_calculo = apertura + timedelta(minutes=BUFFER_INICIAL_MINUTOS)
        else:
            restante_seg = max((fin_calculo - ahora).total_seconds(), 0)
            paso_natural_min = (restante_seg / 60.0) / n
            offset_min = max(INTERVALO_MINIMO_MINUTOS, min(BUFFER_INICIAL_MINUTOS, paso_natural_min))
            inicio_calculo = ahora + timedelta(minutes=offset_min)

        if fin_calculo <= inicio_calculo:
            fin_calculo = inicio_calculo + timedelta(minutes=INTERVALO_MINIMO_MINUTOS * max(n - 1, 0))

        if n == 1:
            horarios = [fin_calculo]
        else:
            paso = (fin_calculo - inicio_calculo).total_seconds() / (n - 1)
            horarios = [inicio_calculo + timedelta(seconds=paso * i) for i in range(n)]
            jitter_seg = min(MARGEN_JITTER_MINUTOS * 60, paso * 0.4)
            for i in range(1, n - 1):
                horarios[i] += timedelta(seconds=random.uniform(-jitter_seg, jitter_seg))
            horarios[-1] = fin_calculo
            horarios.sort()
            horarios = [max(h, inicio_calculo) for h in horarios]
            for i in range(1, n):
                minimo = horarios[i - 1] + timedelta(minutes=INTERVALO_MINIMO_MINUTOS)
                if horarios[i] < minimo:
                    horarios[i] = minimo

        for reg, h in zip(pendientes, horarios):
            log("HORARIOS", f"Local id={reg['uid']} -> {h.strftime('%H:%M:%S')}")
            ejecutar("UPDATE locales SET hora_programada=%s, hora_programada_iso=%s WHERE id=%s",
                     (h.strftime("%H:%M:%S"), h.isoformat(), reg["uid"]))
            agendar(reg["uid"], h)
