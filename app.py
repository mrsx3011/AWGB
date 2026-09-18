import json
import os
import random
import threading
from urllib.parse import quote

import requests
from datetime import datetime, timedelta, time as dtime
import pytz
from flask import (
    Flask, render_template_string, request, flash, redirect, url_for,
    send_from_directory, jsonify
)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

app = Flask(__name__)
app.secret_key = "admin123"

# Configuración de Telegram y archivos
TELEGRAM_TOKEN = "8736941358:AAG8aDuoEUkxNULlP2iewoJrcBM_VF0_fEk"
CHAT_ID = "6060692704"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Archivo donde se persiste TODO el historial (sobrevive reinicios del server)
DATA_FILE = os.path.join(BASE_DIR, 'datos.json')

# Zona horaria de Argentina
ARG_TZ = pytz.timezone('America/Argentina/Buenos_Aires')

# ------------------------------------------------------------------
# Configuración de la ventana horaria de envíos
# ------------------------------------------------------------------
HORA_APERTURA = dtime(10, 0)      # la app "abre" a las 10:00
HORA_CIERRE = dtime(15, 55)       # el ÚLTIMO local del día SIEMPRE se manda a las 15:55
BUFFER_INICIAL_MINUTOS = 18       # margen entre las 10:00 y el primer envío del día (10:18)
INTERVALO_MINIMO_MINUTOS = 2      # separación mínima absoluta entre un local y el siguiente
MARGEN_JITTER_MINUTOS = 20        # variabilidad agregada a los horarios intermedios

# Meta diaria de locales, solo informativa para el usuario
TOTAL_LOCALES_OBJETIVO = 20

# Valor especial del select de objeciones que dispara la elección aleatoria
OBJECION_RANDOM = "Random"

# Lista de objeciones disponibles (se sirve también vía /api/objeciones)
OBJECIONES = [
    "El dueño no se encontraba en el local.",
    "Ya tenian mercado pago y no lo quieren cambiar.",
    "Acaban de pedir otra terminal hace poco.",
    "Lo tienen que pensar.",
    "Lo tiene que hablar con un familiar.",
    "No le gusta trabajar con bancos por problemas en el pasado.",
    "Tienen que hablarlo con un familiar.",
    "No estan interesados.",
]

# Nombres en español para armar fechas del estilo "Jueves 19 de Septiembre"
DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def fecha_larga(fecha_iso):
    """Convierte '2026-09-19' en 'Jueves 19 de Septiembre'."""
    try:
        d = datetime.strptime(fecha_iso, "%Y-%m-%d")
    except (ValueError, TypeError):
        return fecha_iso or ""
    return f"{DIAS_ES[d.weekday()]} {d.day} de {MESES_ES[d.month - 1]}"


# Estado en memoria: almacena la fecha del 'día actual' y las calles registradas
estado_calles = {
    "fecha": datetime.now(ARG_TZ).strftime("%Y-%m-%d"),
    "calles": set()
}

# Lock para proteger el estado compartido entre requests y el scheduler
lock = threading.Lock()

# uid_counter: identificador interno único que NUNCA se reinicia (clave del dict).
# El "numero" que ve el usuario sí se reinicia todos los días (Local N° 1, 2, 3...).
uid_counter = 1

# Historial COMPLETO de locales (de todos los días).
# clave: uid interno -> dict con la info del local (incluye "fecha" y "numero")
registros = {}

scheduler = BackgroundScheduler()
scheduler.start()


# ============================================================================
# PERSISTENCIA — todo se guarda en disco para que sobreviva recargas y caídas
# ============================================================================
def guardar_estado():
    """
    Vuelca el historial completo a datos.json. Se llama después de cada
    cambio (alta, edición, envío, borrado, reprogramación), así que si la
    página se recarga o el servidor se reinicia, no se pierde nada.
    """
    try:
        with lock:
            data = {
                "uid_counter": uid_counter,
                "registros": list(registros.values()),
                "calles": {
                    "fecha": estado_calles["fecha"],
                    "lista": sorted(list(estado_calles["calles"])),
                },
            }
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DATA_FILE)   # escritura atómica: nunca queda a medias
    except OSError as e:
        print(f"[persistencia] No se pudo guardar: {e}")


def cargar_estado():
    """Levanta el historial de datos.json al arrancar el servidor."""
    global uid_counter
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        print(f"[persistencia] No se pudo leer {DATA_FILE}: {e}")
        return

    with lock:
        uid_counter = data.get("uid_counter", 1)
        for r in data.get("registros", []):
            if "uid" in r:
                registros[r["uid"]] = r
        calles_guardadas = data.get("calles", {})
        estado_calles["fecha"] = calles_guardadas.get(
            "fecha", datetime.now(ARG_TZ).strftime("%Y-%m-%d"))
        estado_calles["calles"] = set(calles_guardadas.get("lista", []))

    print(f"[persistencia] {len(registros)} locales cargados desde disco.")


def reprogramar_jobs_pendientes():
    """
    Después de un reinicio, los jobs del scheduler se pierden (viven en
    memoria). Esta función los vuelve a crear para los locales de HOY que
    quedaron pendientes.
    """
    hoy = datetime.now(ARG_TZ).strftime("%Y-%m-%d")
    ahora = datetime.now(ARG_TZ)

    with lock:
        pendientes_hoy = [r for r in registros.values()
                          if r["estado"] == "pendiente" and r.get("fecha") == hoy]

    for r in pendientes_hoy:
        if not r.get("hora_manual"):
            continue  # los automáticos los reagenda recalcular_horarios_pendientes()
        try:
            run_date = datetime.fromisoformat(r["hora_programada_iso"])
        except (ValueError, KeyError):
            continue
        if run_date <= ahora:
            run_date = ahora + timedelta(minutes=INTERVALO_MINIMO_MINUTOS)
        try:
            scheduler.add_job(
                func=enviar_reporte_telegram, trigger='date', run_date=run_date,
                id=f"job_{r['uid']}", replace_existing=True,
                args=[r["uid"], r["nombre"], r["direccion"], r["filepath"], r["objecion"]]
            )
        except Exception as e:
            print(f"[scheduler] No se pudo reagendar {r['uid']}: {e}")

    recalcular_horarios_pendientes()


def verificar_dia():
    """
    Si cambió el día (hora de Argentina), limpia las calles sugeridas.
    OJO: el historial de locales NO se borra nunca — queda disponible en la
    sección "Lista de locales", agrupado por fecha.
    """
    hoy = datetime.now(ARG_TZ).strftime("%Y-%m-%d")
    cambio = False
    with lock:
        if estado_calles["fecha"] != hoy:
            estado_calles["fecha"] = hoy
            estado_calles["calles"].clear()
            cambio = True
    if cambio:
        guardar_estado()


def obtener_calles_actualizadas():
    """Limpia las calles si cambió el día según la hora de Argentina."""
    verificar_dia()
    with lock:
        return sorted(list(estado_calles["calles"]))


def registros_de_hoy():
    hoy = datetime.now(ARG_TZ).strftime("%Y-%m-%d")
    with lock:
        return [r for r in registros.values() if r.get("fecha") == hoy]


def contar_locales_hoy():
    return len(registros_de_hoy())


def proximo_numero_del_dia():
    """El N° de local que ve el usuario se reinicia cada día: 1, 2, 3..."""
    return len(registros_de_hoy()) + 1


def recalcular_horarios_pendientes():
    """
    Recalcula y reprograma el horario de envío de TODOS los locales de HOY
    que estén pendientes, repartiéndolos de forma equitativa entre el
    momento actual (o las 10:18 si el día recién está arrancando) y las
    15:55, que es siempre el límite para el último local del día.

    Cada vez que se agrega un nuevo local, se elimina uno o se envía uno
    manualmente, hay que volver a llamar a esta función para que los
    horarios de los locales que todavía están pendientes se vuelvan a
    repartir entre todos.

    Para que no quede algo demasiado robótico (siempre el mismo intervalo
    exacto), a los horarios intermedios se les agrega una variación
    aleatoria de +/- MARGEN_JITTER_MINUTOS. El primero y el último
    (siempre 15:55) no llevan variación.

    IMPORTANTE sobre INTERVALO_MINIMO_MINUTOS (2 min): es solamente un
    PISO de seguridad, para que nunca salgan dos locales casi pegados.
    NO es el ritmo de envío. El ritmo siempre se calcula repartiendo de
    forma proporcional el tiempo que queda entre ahora y las 15:55 entre
    todos los pendientes, así se cubre la mayor parte posible de la
    ventana horaria. Los 2 minutos sólo entran en juego si quedan tantos
    locales y tan poco tiempo que el reparto proporcional daría menos que
    eso.

    Los locales cuya hora fue fijada a mano (hora_manual = True, vía
    /ajustar_hora) quedan afuera de este reparto automático.
    """
    ahora = datetime.now(ARG_TZ)
    hoy_str = ahora.strftime("%Y-%m-%d")
    apertura = ARG_TZ.localize(datetime.combine(ahora.date(), HORA_APERTURA))
    cierre = ARG_TZ.localize(datetime.combine(ahora.date(), HORA_CIERRE))

    with lock:
        pendientes = sorted(
            (r for r in registros.values()
             if r["estado"] == "pendiente"
             and r.get("fecha") == hoy_str
             and not r.get("hora_manual")),
            key=lambda r: r["uid"]
        )

    n = len(pendientes)
    if n == 0:
        return

    fin_calculo = cierre

    # ------------------------------------------------------------------
    # Punto de partida del cálculo.
    #
    # El primer pendiente NO se ancla a "ahora + 2 minutos": ese era el
    # error que hacía que, al enviarse un local, el siguiente saltara a
    # 2 minutos y se comiera toda la ventana horaria. Los 2 minutos son
    # sólo un piso de seguridad (que nunca salgan dos locales casi
    # pegados), no el ritmo de envío.
    #
    # El hueco inicial es proporcional: se calcula cuánto tiempo queda
    # hasta las 15:55 y se divide por la cantidad de pendientes, de modo
    # que el espacio entre "ahora" y el primer envío sea del mismo orden
    # que el espacio entre un local y el siguiente. Ese hueco se limita
    # entre 2 y 18 minutos.
    # ------------------------------------------------------------------
    if ahora < apertura:
        # El día todavía no arrancó: el primero sale 10:18 como siempre.
        inicio_calculo = apertura + timedelta(minutes=BUFFER_INICIAL_MINUTOS)
    else:
        restante_seg = max((fin_calculo - ahora).total_seconds(), 0)
        paso_natural_min = (restante_seg / 60.0) / n
        offset_min = max(INTERVALO_MINIMO_MINUTOS,
                         min(BUFFER_INICIAL_MINUTOS, paso_natural_min))
        inicio_calculo = ahora + timedelta(minutes=offset_min)

    # Caso límite: si ya pasamos (o estamos muy cerca de) las 15:55,
    # igual garantizamos el mínimo de 2 minutos entre locales y los
    # mandamos lo antes posible, en cadena.
    if fin_calculo <= inicio_calculo:
        fin_calculo = inicio_calculo + timedelta(
            minutes=INTERVALO_MINIMO_MINUTOS * max(n - 1, 0)
        )

    if n == 1:
        # Si queda un solo pendiente, es el ÚLTIMO del día: va a las 15:55.
        # (Antes se lo mandaba a "ahora + 2 min", que era el bug principal.)
        horarios = [fin_calculo]
    else:
        total_segundos = (fin_calculo - inicio_calculo).total_seconds()
        paso = total_segundos / (n - 1)
        horarios = [inicio_calculo + timedelta(seconds=paso * i) for i in range(n)]

        # Jitter en los horarios intermedios (no en el primero ni en el
        # último). Se limita al 40% del paso: si hay muchos locales y el
        # paso es chico, un margen fijo de 20 min los amontonaría.
        jitter_seg = min(MARGEN_JITTER_MINUTOS * 60, paso * 0.4)
        for i in range(1, n - 1):
            horarios[i] += timedelta(seconds=random.uniform(-jitter_seg, jitter_seg))

        horarios[-1] = fin_calculo  # el último SIEMPRE a las 15:55 (o al cierre calculado)

        # Reordenar (el jitter puede desordenar), no dejar ninguno antes
        # del inicio válido, y garantizar el mínimo de
        # INTERVALO_MINIMO_MINUTOS entre locales consecutivos.
        horarios.sort()
        horarios = [max(h, inicio_calculo) for h in horarios]
        for i in range(1, n):
            minimo = horarios[i - 1] + timedelta(minutes=INTERVALO_MINIMO_MINUTOS)
            if horarios[i] < minimo:
                horarios[i] = minimo

    # Reprogramar cada job y actualizar el registro correspondiente.
    with lock:
        for registro, nuevo_horario in zip(pendientes, horarios):
            uid = registro["uid"]
            registro["hora_programada"] = nuevo_horario.strftime("%H:%M:%S")
            registro["hora_programada_iso"] = nuevo_horario.isoformat()

            job_id = f"job_{uid}"
            try:
                scheduler.reschedule_job(job_id, trigger='date', run_date=nuevo_horario)
            except JobLookupError:
                scheduler.add_job(
                    func=enviar_reporte_telegram,
                    trigger='date',
                    run_date=nuevo_horario,
                    id=job_id,
                    args=[uid, registro["nombre"], registro["direccion"],
                          registro["filepath"], registro["objecion"]]
                )

    guardar_estado()


def _post_telegram_texto(texto):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    )


def enviar_reporte_telegram(uid, nombre_local, direccion, filepath, objecion,
                            encabezado=None, numero_mostrado=None):
    """
    Envía el reporte del local por Telegram, DESGLOSADO en varios mensajes:
      0) (opcional) un encabezado, usado por el re-envío: "R.E FECHA: ..."
      1) la foto del local
      2) el nombre del local
      3) la dirección (calle + altura)
      4) la objeción registrada (o aviso de que no hubo objeción)
    """
    url_photo = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    # 0) Encabezado del re-envío (va arriba de todo)
    if encabezado:
        _post_telegram_texto(encabezado)

    if numero_mostrado is None:
        with lock:
            reg = registros.get(uid)
            numero_mostrado = reg["numero"] if reg else uid

    # 1) Foto del local
    if filepath and os.path.exists(filepath):
        with open(filepath, 'rb') as photo_file:
            requests.post(
                url_photo,
                data={"chat_id": CHAT_ID, "caption": f"📌 Local N° {numero_mostrado}"},
                files={"photo": photo_file}
            )

    # 2) Nombre del local
    _post_telegram_texto(f"{nombre_local}")

    # 3) Dirección y altura
    _post_telegram_texto(f"{direccion}")

    # 4) Objeción
    _post_telegram_texto(f" {objecion if objecion else 'Sin objeción registrada.'}")

    # Si es un envío normal (no un re-envío), marcar como enviado.
    if encabezado is None:
        with lock:
            if uid in registros:
                registros[uid]["estado"] = "enviado"
                registros[uid]["hora_envio_real"] = datetime.now(ARG_TZ).strftime("%H:%M:%S")
        # Como este local ya salió de la lista de "pendientes", hay que
        # repartir de nuevo el tiempo restante entre los que quedan.
        recalcular_horarios_pendientes()
        guardar_estado()


# ============================================================================
# DISEÑO — tokens y estilos base compartidos por las pantallas
# ============================================================================
BASE_CSS = """
:root{
    --ink-900:#1A2027; --ink-700:#333D45; --ink-600:#57626C; --ink-300:#A6AFB6;
    --paper:#F1F4F3; --surface:#FFFFFF; --line:#E3E7E6;
    --brand-600:#0B6E99; --brand-700:#095777; --brand-100:#E4F1F6;
    --amber-600:#B4720A; --amber-700:#8F5B08; --amber-100:#FBEBD2; --amber-200:#F3D8A4;
    --green-600:#1E8A5D; --green-700:#166B48; --green-100:#DFF3E7;
    --red-600:#C1352B; --red-700:#9C2A22; --red-100:#F8E1DE;
    --radius-sm:8px; --radius-md:12px; --radius-lg:16px;
    --shadow-card:0 1px 2px rgba(20,25,30,.04), 0 8px 20px rgba(20,25,30,.06);
}
*{ box-sizing:border-box; }
html{ -webkit-text-size-adjust:100%; }
body{
    font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background:var(--paper); color:var(--ink-900); margin:0; padding:22px 16px 60px;
    -webkit-font-smoothing:antialiased;
}
a{ color:var(--brand-600); }
h2{ font-size:19px; font-weight:700; letter-spacing:-0.01em; margin:0; color:var(--ink-900); }

.page{ max-width:560px; margin:0 auto; }
.page-wide{ max-width:1140px; margin:0 auto; }

.topbar{ display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; gap:10px; flex-wrap:wrap; }
.navlinks{ display:flex; gap:14px; flex-wrap:wrap; }
.navlinks a{ text-decoration:none; font-weight:600; font-size:13.5px; display:inline-flex; align-items:center; gap:6px; }

.contador-wrap{ background:var(--surface); border:1px solid var(--line); border-radius:var(--radius-md);
    padding:13px 16px; margin-bottom:18px; box-shadow:var(--shadow-card); }
.contador-top{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:8px; }
.contador-label{ font-size:12.5px; font-weight:600; color:var(--ink-600); }
.contador-num{ font-size:13px; font-weight:700; color:var(--ink-900); }
.contador-track{ height:6px; background:var(--paper); border-radius:99px; overflow:hidden; }
.contador-fill{ height:100%; background:var(--brand-600); border-radius:99px; transition:width .4s ease; }

.alert{ background:var(--green-100); color:var(--green-700); padding:11px 14px; margin-bottom:16px;
    border-radius:var(--radius-sm); font-size:13.5px; font-weight:500; border:1px solid #c7e9d5; }

.card{ background:var(--surface); border:1px solid var(--line); border-radius:var(--radius-lg);
    padding:20px; box-shadow:var(--shadow-card); }

.field{ margin-bottom:16px; }
label{ display:block; margin-bottom:6px; font-weight:600; font-size:13px; color:var(--ink-700); }
input[type="text"], input[type="number"], input[type="file"], input[type="time"], select{
    width:100%; padding:10px 12px; border:1px solid var(--line);
    border-radius:var(--radius-sm); font-size:14px; background:var(--surface); color:var(--ink-900);
    font-family:inherit;
}
input:focus, select:focus{ outline:none; border-color:var(--brand-600); box-shadow:0 0 0 3px var(--brand-100); }
select{ appearance:none; -webkit-appearance:none;
    background-image:url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20'%3e%3cpath fill='%2357626C' d='M5.5 7.5l4.5 4.5 4.5-4.5z'/%3e%3c/svg%3e");
    background-repeat:no-repeat; background-position:right 10px center; padding-right:32px; }

button{ font-family:inherit; }
.btn-primary{ background:var(--brand-600); color:#fff; border:none; padding:12px 16px; border-radius:var(--radius-sm);
    cursor:pointer; font-size:14.5px; font-weight:600; width:100%; }
.btn-primary:hover{ background:var(--brand-700); }

.btn-pill{ display:inline-flex; align-items:center; gap:6px; padding:7px 12px; border-radius:99px;
    font-size:12.5px; font-weight:600; border:1px solid transparent; cursor:pointer; white-space:nowrap;
    transition:background .15s ease, transform .05s ease; line-height:1; font-family:inherit; text-decoration:none; }
.btn-pill:active{ transform:scale(.96); }

.badge{ display:inline-flex; align-items:center; gap:4px; padding:4px 10px; border-radius:99px;
    font-size:11.5px; font-weight:700; white-space:nowrap; }
.badge-pendiente{ background:var(--amber-100); color:var(--amber-700); }
.badge-enviado{ background:var(--green-100); color:var(--green-700); }
.badge-manual{ background:var(--brand-100); color:var(--brand-700); font-size:10px; padding:2px 7px; margin-left:5px; }

.empty{ text-align:center; padding:52px 20px; color:var(--ink-600); background:var(--surface);
    border:1px dashed var(--line); border-radius:var(--radius-lg); }

/* Preview de foto + lightbox */
.preview-box{ display:none; margin-top:10px; }
.preview-thumb, .foto-actual{ display:block; max-width:200px; max-height:200px; border-radius:var(--radius-md);
    border:1px solid var(--line); cursor:zoom-in; object-fit:cover; }
.preview-hint, .foto-hint{ font-size:12px; color:var(--ink-600); margin-top:6px; }

.zoom-overlay{ display:none; position:fixed; inset:0; background:rgba(15,18,20,.9); z-index:1000;
    align-items:center; justify-content:center; overflow:auto; cursor:zoom-out; padding:20px; box-sizing:border-box; }
.zoom-overlay.activo{ display:flex; }
.zoom-overlay img{ max-width:90%; max-height:90%; cursor:zoom-in; border-radius:8px; }
.zoom-overlay img.zoom-in{ max-width:none; max-height:none; width:auto; transform:scale(1.9); cursor:zoom-out; }
.zoom-close{ position:fixed; top:16px; right:18px; color:#fff; font-size:22px; cursor:pointer; z-index:1001;
    width:36px; height:36px; display:flex; align-items:center; justify-content:center;
    background:rgba(255,255,255,.14); border-radius:50%; line-height:1; }

/* Aviso de copia local (localStorage) */
.cache-note{ font-size:11.5px; color:var(--ink-300); text-align:center; margin-top:18px; }
"""

ZOOM_JS = """
function abrirZoom(src) {
    if (!src) return;
    const overlay = document.getElementById('zoomOverlay');
    const img = document.getElementById('zoomImg');
    img.src = src;
    img.classList.remove('zoom-in');
    overlay.classList.add('activo');
}
function cerrarZoom(event, forzar) {
    if (forzar || event.target.id === 'zoomOverlay') {
        document.getElementById('zoomOverlay').classList.remove('activo');
    }
}
function toggleZoom(event) {
    event.stopPropagation();
    event.target.classList.toggle('zoom-in');
}
"""

ZOOM_HTML = """
    <div class="zoom-overlay" id="zoomOverlay" onclick="cerrarZoom(event)">
        <span class="zoom-close" onclick="cerrarZoom(event, true)">&times;</span>
        <img id="zoomImg" src="" alt="Zoom" onclick="toggleZoom(event)">
    </div>
"""

# JS que guarda una copia de todos los datos en el localStorage del navegador
# en cada carga de página. Es un respaldo de lectura: si el servidor no
# responde, la sección "Lista de locales" igual puede mostrar la última copia.
CACHE_JS = """
const CACHE_KEY = 'locales_backup_v1';

function guardarCacheLocal(datos) {
    try {
        localStorage.setItem(CACHE_KEY, JSON.stringify({
            guardado: new Date().toISOString(),
            datos: datos
        }));
    } catch (e) {
        console.warn('No se pudo guardar en localStorage:', e);
    }
}

function leerCacheLocal() {
    try {
        const raw = localStorage.getItem(CACHE_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch (e) {
        return null;
    }
}
"""


HTML_FORM = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro de Local</title>
    <style>""" + BASE_CSS + """
    </style>
</head>
<body>
<div class="page">
    <div class="topbar">
        <h2>Registro de local</h2>
        <div class="navlinks">
            <a href="{{ url_for('dashboard') }}">📊 Dashboard</a>
            <a href="{{ url_for('lista') }}">🗂️ Lista</a>
        </div>
    </div>

    <div class="contador-wrap">
        <div class="contador-top">
            <span class="contador-label">Locales registrados hoy</span>
            <span class="contador-num">{{ total_locales }}/{{ objetivo }}</span>
        </div>
        <div class="contador-track">
            <div class="contador-fill" style="width: {{ (total_locales / objetivo * 100) if objetivo else 0 }}%;"></div>
        </div>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="alert">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <div class="card">
        <form method="POST" enctype="multipart/form-data">
            <div class="field">
                <label>Local</label>
                <input type="text" name="local" required placeholder="Ej: Sucursal Centro">
            </div>

            <div class="field">
                <label>Calle</label>
                <input type="text" name="calle" list="calles_registradas" required placeholder="Ej: Av. Corrientes" autocomplete="off">
                <datalist id="calles_registradas">
                    {% for calle in calles %}
                        <option value="{{ calle }}"></option>
                    {% endfor %}
                </datalist>
            </div>

            <div class="field">
                <label>Altura</label>
                <input type="text" name="altura" required placeholder="Ej: 1234">
            </div>

            <div class="field">
                <label>Objeción (si aplica)</label>
                <select name="objecion">
                    <option value="">Sin objeción / venta realizada</option>
                    <option value="{{ objecion_random }}">🎲 Random — elige una al azar</option>
                    {% for obj in objeciones %}
                        <option value="{{ obj }}">{{ obj }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="field">
                <label>Foto del local</label>
                <input type="file" name="foto" id="fotoInput" accept="image/*" required onchange="mostrarPreview(event)">
                <div class="preview-box" id="previewBox">
                    <img class="preview-thumb" id="previewImg" alt="Vista previa" onclick="abrirZoom(this.src)">
                    <div class="preview-hint">Click en la imagen para hacer zoom</div>
                </div>
            </div>

            <button type="submit" class="btn-primary">Enviar registro</button>
        </form>
    </div>

    <div class="cache-note" id="cacheNote"></div>
</div>
""" + ZOOM_HTML + """
    <script id="datos-json" type="application/json">{{ datos_json | safe }}</script>
    <script>
        """ + CACHE_JS + """
        """ + ZOOM_JS + """

        function mostrarPreview(event) {
            const file = event.target.files[0];
            const box = document.getElementById('previewBox');
            const img = document.getElementById('previewImg');
            if (!file) { box.style.display = 'none'; img.src = ''; return; }
            const reader = new FileReader();
            reader.onload = function(e) { img.src = e.target.result; box.style.display = 'block'; };
            reader.readAsDataURL(file);
        }

        // Guardar copia local de todo el historial en cada carga
        (function () {
            try {
                const datos = JSON.parse(document.getElementById('datos-json').textContent);
                guardarCacheLocal(datos);
                const cache = leerCacheLocal();
                if (cache) {
                    const f = new Date(cache.guardado);
                    document.getElementById('cacheNote').textContent =
                        '💾 Copia local guardada: ' + f.toLocaleString('es-AR');
                }
            } catch (e) { console.warn(e); }
        })();
    </script>
</body>
</html>
"""


HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Locales</title>
    <style>""" + BASE_CSS + """

        .table-card{ background:var(--surface); border:1px solid var(--line); border-radius:var(--radius-lg);
            overflow:visible; box-shadow:var(--shadow-card); }
        table{ width:100%; border-collapse:collapse; }
        th{ background:var(--paper); color:var(--ink-600); text-align:left; font-size:12px; font-weight:700;
            padding:12px 14px; border-bottom:1px solid var(--line); }
        th:first-child{ border-top-left-radius:var(--radius-lg); }
        th:last-child{ border-top-right-radius:var(--radius-lg); }
        td{ padding:11px 14px; font-size:13.5px; border-bottom:1px solid var(--line); color:var(--ink-700);
            vertical-align:middle; position:relative; }
        tr:last-child td{ border-bottom:none; }
        tr:hover td{ background:#FAFBFB; }

        .thumb{ width:42px; height:42px; object-fit:cover; border-radius:8px; border:1px solid var(--line);
            cursor:zoom-in; display:block; }
        .countdown{ font-size:11px; color:var(--ink-600); margin-top:2px; }
        .objecion-cell{ max-width:190px; font-size:12px; color:var(--ink-600); }

        .action-groups{ display:flex; align-items:center; gap:6px; flex-wrap:wrap; position:relative; }
        .btn-enviar{ background:var(--brand-600); color:#fff; }
        .btn-enviar:hover{ background:var(--brand-700); }
        .chip-enviado{ background:var(--green-100); color:var(--green-700); cursor:default; }
        .btn-conf{ background:var(--surface); color:var(--ink-700); border-color:var(--line); }
        .btn-conf:hover{ background:var(--paper); }
        .btn-conf.activo{ background:var(--paper); border-color:var(--ink-300); }
        .btn-auto{ background:var(--surface); color:var(--ink-600); border-color:var(--line); }
        .btn-auto:hover{ background:var(--paper); }
        .btn-manual{ background:var(--amber-100); color:var(--amber-700); border-color:var(--amber-200); }
        .btn-manual:hover{ background:#F5DFB0; }

        .conf-menu{ position:relative; display:inline-block; }
        .conf-panel{ display:none; position:absolute; right:0; top:calc(100% + 6px); background:var(--surface);
            border:1px solid var(--line); border-radius:var(--radius-md); box-shadow:0 10px 28px rgba(20,25,30,.16);
            padding:8px; min-width:230px; z-index:200; }
        .conf-panel.abierto{ display:block; }
        .conf-item{ display:flex; align-items:center; gap:8px; padding:9px 10px; border-radius:8px; font-size:13px;
            color:var(--ink-700); text-decoration:none; cursor:pointer; width:100%; border:none; background:none;
            text-align:left; font-family:inherit; }
        .conf-item:hover{ background:var(--paper); }
        .conf-item.danger{ color:var(--red-600); }
        .conf-item.danger:hover{ background:var(--red-100); }
        .conf-divider{ height:1px; background:var(--line); margin:6px 4px; }
        .conf-label{ font-size:11px; font-weight:700; color:var(--ink-300); padding:6px 10px 2px; }
        .conf-time-row{ display:flex; gap:6px; align-items:center; padding:4px 10px 8px; }
        .conf-time-row input[type="time"]{ flex:1; padding:7px 8px; font-size:12.5px; }
        .conf-time-row button{ padding:7px 11px; border-radius:8px; border:none; background:var(--brand-600);
            color:#fff; font-size:12px; font-weight:600; cursor:pointer; white-space:nowrap; }
        .conf-time-row button:hover{ background:var(--brand-700); }

        @media (max-width: 760px){
            body{ padding:16px 10px 60px; }
            table, thead, tbody, tr{ display:block; width:100%; }
            thead{ display:none; }
            tr{ background:var(--surface); border:1px solid var(--line); border-radius:var(--radius-md);
                margin-bottom:12px; padding:6px 4px; }
            td{ display:flex; justify-content:space-between; align-items:center; gap:12px;
                border-bottom:1px dashed var(--line); padding:9px 10px; }
            tr td:last-child{ border-bottom:none; }
            td::before{ content:attr(data-label); font-weight:600; color:var(--ink-600); font-size:11.5px; flex-shrink:0; }
            td.td-photo{ justify-content:flex-start; }
            td.td-photo::before{ content:''; }
            td.td-photo .thumb{ width:56px; height:56px; }
            td.td-actions{ display:block; }
            td.td-actions::before{ content:''; }
            td.td-actions .action-groups{ justify-content:flex-end; }
        }
    </style>
</head>
<body>
<div class="page-wide">
    <div class="topbar">
        <h2>📊 Dashboard de locales</h2>
        <div class="navlinks">
            <a href="{{ url_for('index') }}">➕ Nuevo registro</a>
            <a href="{{ url_for('lista') }}">🗂️ Lista de locales</a>
        </div>
    </div>

    <div class="contador-wrap">
        <div class="contador-top">
            <span class="contador-label">Locales registrados hoy</span>
            <span class="contador-num">{{ total_locales }}/{{ objetivo }}</span>
        </div>
        <div class="contador-track">
            <div class="contador-fill" style="width: {{ (total_locales / objetivo * 100) if objetivo else 0 }}%;"></div>
        </div>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="alert">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% if registros %}
    <div class="table-card">
    <table>
        <thead>
            <tr>
                <th>Foto</th><th>N° Local</th><th>Nombre</th><th>Dirección</th><th>Objeción</th>
                <th>Registrado</th><th>Envío estimado</th><th>Estado</th><th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for r in registros %}
            <tr>
                <td class="td-photo" data-label="Foto">
                    <img class="thumb" src="{{ url_for('uploaded_file', filename=r.foto) }}"
                         alt="Foto local {{ r.numero }}" onclick="abrirZoom(this.src)">
                </td>
                <td data-label="N° Local">{{ r.numero }}</td>
                <td data-label="Nombre">{{ r.nombre }}</td>
                <td data-label="Dirección">{{ r.direccion }}</td>
                <td class="objecion-cell" data-label="Objeción">{{ r.objecion if r.objecion else '—' }}</td>
                <td data-label="Registrado">{{ r.hora_registro }}</td>
                <td data-label="Envío estimado">
                    <div>
                        {{ r.hora_programada }}
                        {% if r.hora_manual %}<span class="badge-manual">🔒 Manual</span>{% endif %}
                        {% if r.estado == 'pendiente' %}
                            <div class="countdown" data-target="{{ r.hora_programada_iso }}"></div>
                        {% endif %}
                    </div>
                </td>
                <td data-label="Estado">
                    {% if r.estado == 'enviado' %}
                        <span class="badge badge-enviado">✅ Enviado</span>
                    {% else %}
                        <span class="badge badge-pendiente">⏳ En proceso</span>
                    {% endif %}
                </td>
                <td class="td-actions" data-label="Acciones">
                    <div class="action-groups">
                        <!-- Grupo 1: Enviar -->
                        {% if r.estado == 'pendiente' %}
                        <form method="POST" action="{{ url_for('enviar_ahora', uid=r.uid) }}"
                              onsubmit="return confirm('¿Enviar el Local N° {{ r.numero }} ahora mismo?');">
                            <button type="submit" class="btn-pill btn-enviar">📤 Enviar</button>
                        </form>
                        {% else %}
                        <span class="btn-pill chip-enviado">✅ Enviado</span>
                        {% endif %}

                        <!-- Grupo 2: Conf -->
                        <div class="conf-menu">
                            <button type="button" class="btn-pill btn-conf" id="conf-btn-{{ r.uid }}"
                                    onclick="toggleConf(event, {{ r.uid }})">⚙️ Conf</button>
                            <div class="conf-panel" id="conf-panel-{{ r.uid }}">
                                <a class="conf-item" href="{{ url_for('editar', uid=r.uid) }}">✏️ Editar datos</a>
                                <a class="conf-item" target="_blank" rel="noopener"
                                   href="https://www.google.com/maps/search/?api=1&query={{ r.direccion_url }}">📍 Ver ubicación</a>
                                {% if r.estado == 'pendiente' %}
                                <div class="conf-divider"></div>
                                <div class="conf-label">Reprogramar envío</div>
                                <form method="POST" action="{{ url_for('ajustar_hora', uid=r.uid) }}" class="conf-time-row">
                                    <input type="time" id="hora-input-{{ r.uid }}" name="nueva_hora"
                                           value="{{ r.hora_programada[:5] }}" required>
                                    <button type="submit">Fijar</button>
                                </form>
                                {% endif %}
                                <div class="conf-divider"></div>
                                <form method="POST" action="{{ url_for('eliminar', uid=r.uid) }}"
                                      onsubmit="return confirm('¿Eliminar el Local N° {{ r.numero }}? Esta acción no se puede deshacer.');">
                                    <button type="submit" class="conf-item danger">🗑️ Eliminar local</button>
                                </form>
                            </div>
                        </div>

                        <!-- Grupo 3: Manual / Auto -->
                        {% if r.estado == 'pendiente' %}
                            {% if r.hora_manual %}
                            <form method="POST" action="{{ url_for('auto_hora', uid=r.uid) }}">
                                <button type="submit" class="btn-pill btn-manual" title="Volver al reparto automático">🔒 Manual</button>
                            </form>
                            {% else %}
                            <button type="button" class="btn-pill btn-auto" title="Fijar hora manual"
                                    onclick="abrirConfParaHora({{ r.uid }})">🔄 Auto</button>
                            {% endif %}
                        {% endif %}
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    </div>
    {% else %}
        <div class="empty">Todavía no hay locales registrados hoy.</div>
    {% endif %}

    <div class="cache-note" id="cacheNote"></div>
</div>
""" + ZOOM_HTML + """
    <script id="datos-json" type="application/json">{{ datos_json | safe }}</script>
    <script>
        """ + CACHE_JS + """
        """ + ZOOM_JS + """

        function cerrarTodosLosConf() {
            document.querySelectorAll('.conf-panel.abierto').forEach(p => p.classList.remove('abierto'));
            document.querySelectorAll('.btn-conf.activo').forEach(b => b.classList.remove('activo'));
        }
        function toggleConf(event, uid) {
            event.stopPropagation();
            const panel = document.getElementById('conf-panel-' + uid);
            const boton = document.getElementById('conf-btn-' + uid);
            const abierto = panel.classList.contains('abierto');
            cerrarTodosLosConf();
            if (!abierto) { panel.classList.add('abierto'); boton.classList.add('activo'); }
        }
        function abrirConfParaHora(uid) {
            cerrarTodosLosConf();
            const panel = document.getElementById('conf-panel-' + uid);
            const boton = document.getElementById('conf-btn-' + uid);
            if (!panel) return;
            panel.classList.add('abierto');
            if (boton) boton.classList.add('activo');
            const input = document.getElementById('hora-input-' + uid);
            if (input) setTimeout(() => input.focus(), 30);
        }
        document.addEventListener('click', e => { if (!e.target.closest('.conf-menu')) cerrarTodosLosConf(); });
        document.addEventListener('keydown', e => { if (e.key === 'Escape') cerrarTodosLosConf(); });

        function actualizarCountdowns() {
            document.querySelectorAll('.countdown').forEach(function(el) {
                const target = new Date(el.dataset.target);
                const diffMs = target - new Date();
                if (diffMs <= 0) { el.textContent = 'llegando...'; return; }
                const mins = Math.floor(diffMs / 60000);
                const secs = Math.floor((diffMs % 60000) / 1000);
                el.textContent = 'faltan ' + mins + 'm ' + secs.toString().padStart(2, '0') + 's';
            });
        }
        setInterval(actualizarCountdowns, 1000);
        actualizarCountdowns();

        // Refresco automático, pero sin interrumpir un menú Conf abierto
        setInterval(function () {
            if (!document.querySelector('.conf-panel.abierto')) window.location.reload();
        }, 30000);

        // Copia local de todos los datos
        (function () {
            try {
                const datos = JSON.parse(document.getElementById('datos-json').textContent);
                guardarCacheLocal(datos);
                const cache = leerCacheLocal();
                if (cache) {
                    document.getElementById('cacheNote').textContent =
                        '💾 Copia local guardada: ' + new Date(cache.guardado).toLocaleString('es-AR');
                }
            } catch (e) { console.warn(e); }
        })();
    </script>
</body>
</html>
"""


HTML_LISTA = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lista de Locales</title>
    <style>""" + BASE_CSS + """

        .dia-card{ background:var(--surface); border:1px solid var(--line); border-radius:var(--radius-lg);
            box-shadow:var(--shadow-card); margin-bottom:12px; overflow:hidden; }

        .dia-header{ display:flex; align-items:center; justify-content:space-between; gap:12px;
            padding:15px 18px; cursor:pointer; user-select:none; background:var(--surface);
            border:none; width:100%; font-family:inherit; text-align:left; }
        .dia-header:hover{ background:#FAFBFB; }
        .dia-titulo{ display:flex; align-items:center; gap:10px; }
        .dia-nombre{ font-size:15px; font-weight:700; color:var(--ink-900); }
        .dia-meta{ display:flex; align-items:center; gap:8px; }
        .dia-count{ background:var(--paper); color:var(--ink-600); font-size:11.5px; font-weight:700;
            padding:3px 10px; border-radius:99px; }
        .flecha{ font-size:12px; color:var(--ink-600); transition:transform .22s ease; display:inline-block; }
        .dia-card.abierto .flecha{ transform:rotate(180deg); }

        .dia-body{ display:none; border-top:1px solid var(--line); padding:6px 14px 14px; }
        .dia-card.abierto .dia-body{ display:block; }

        .local-row{ display:flex; gap:14px; align-items:flex-start; padding:14px 4px;
            border-bottom:1px solid var(--line); }
        .local-row:last-child{ border-bottom:none; }
        .local-foto{ width:62px; height:62px; object-fit:cover; border-radius:10px; border:1px solid var(--line);
            cursor:zoom-in; flex-shrink:0; }
        .local-datos{ flex:1; min-width:0; }
        .local-nombre{ font-size:14.5px; font-weight:700; color:var(--ink-900); margin-bottom:3px; }
        .local-linea{ font-size:12.5px; color:var(--ink-600); margin-bottom:2px; }
        .local-linea strong{ color:var(--ink-700); font-weight:600; }
        .local-tags{ display:flex; gap:6px; flex-wrap:wrap; margin-top:7px; align-items:center; }
        .local-acciones{ flex-shrink:0; display:flex; align-items:flex-start; }
        .btn-reenviar{ background:var(--brand-600); color:#fff; }
        .btn-reenviar:hover{ background:var(--brand-700); }

        @media (max-width: 620px){
            .local-row{ flex-wrap:wrap; }
            .local-acciones{ width:100%; justify-content:flex-end; }
        }
    </style>
</head>
<body>
<div class="page-wide">
    <div class="topbar">
        <h2>🗂️ Lista de locales</h2>
        <div class="navlinks">
            <a href="{{ url_for('index') }}">➕ Nuevo registro</a>
            <a href="{{ url_for('dashboard') }}">📊 Dashboard</a>
        </div>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="alert">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% if dias %}
        {% for dia in dias %}
        <div class="dia-card {% if loop.first %}abierto{% endif %}" id="dia-{{ dia.fecha }}">
            <button type="button" class="dia-header" onclick="toggleDia('{{ dia.fecha }}')">
                <div class="dia-titulo">
                    <span class="dia-nombre">{{ dia.fecha_larga }}</span>
                </div>
                <div class="dia-meta">
                    <span class="dia-count">{{ dia.locales|length }} local{{ 'es' if dia.locales|length != 1 else '' }}</span>
                    <span class="flecha">▼</span>
                </div>
            </button>

            <div class="dia-body">
                {% for r in dia.locales %}
                <div class="local-row">
                    <img class="local-foto" src="{{ url_for('uploaded_file', filename=r.foto) }}"
                         alt="Local {{ r.numero }}" onclick="abrirZoom(this.src)">
                    <div class="local-datos">
                        <div class="local-nombre">Local N° {{ r.numero }} — {{ r.nombre }}</div>
                        <div class="local-linea"><strong>Dirección:</strong> {{ r.direccion }}</div>
                        <div class="local-linea"><strong>Objeción:</strong> {{ r.objecion if r.objecion else 'Sin objeción registrada.' }}</div>
                        <div class="local-linea"><strong>Registrado:</strong> {{ r.hora_registro }}</div>
                        <div class="local-linea">
                            <strong>Hora de entrega:</strong>
                            {{ r.hora_envio_real if r.hora_envio_real else r.hora_programada }}
                        </div>
                        <div class="local-tags">
                            {% if r.estado == 'enviado' %}
                                <span class="badge badge-enviado">✅ Enviado</span>
                            {% else %}
                                <span class="badge badge-pendiente">⏳ En proceso</span>
                            {% endif %}
                            {% if r.hora_manual %}<span class="badge-manual">🔒 Manual</span>{% endif %}
                        </div>
                    </div>
                    <div class="local-acciones">
                        <form method="POST" action="{{ url_for('reenviar', uid=r.uid) }}"
                              onsubmit="return confirm('¿Re-enviar el Local N° {{ r.numero }} del {{ dia.fecha_larga }} al chat?');">
                            <button type="submit" class="btn-pill btn-reenviar">🔁 Re-enviar</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div class="empty">Todavía no hay locales registrados.</div>
    {% endif %}

    <div class="cache-note" id="cacheNote"></div>
</div>
""" + ZOOM_HTML + """
    <script id="datos-json" type="application/json">{{ datos_json | safe }}</script>
    <script>
        """ + CACHE_JS + """
        """ + ZOOM_JS + """

        // Acordeón: abrir/cerrar el día. Se recuerda qué días quedaron
        // abiertos usando el localStorage del navegador.
        const DIAS_KEY = 'dias_abiertos_v1';

        function diasAbiertos() {
            try { return JSON.parse(localStorage.getItem(DIAS_KEY)) || []; }
            catch (e) { return []; }
        }
        function guardarDiasAbiertos(lista) {
            try { localStorage.setItem(DIAS_KEY, JSON.stringify(lista)); } catch (e) {}
        }
        function toggleDia(fecha) {
            const card = document.getElementById('dia-' + fecha);
            if (!card) return;
            card.classList.toggle('abierto');
            let abiertos = diasAbiertos();
            if (card.classList.contains('abierto')) {
                if (!abiertos.includes(fecha)) abiertos.push(fecha);
            } else {
                abiertos = abiertos.filter(f => f !== fecha);
            }
            guardarDiasAbiertos(abiertos);
        }

        // Restaurar los días que el usuario había dejado abiertos
        (function () {
            const abiertos = diasAbiertos();
            if (abiertos.length) {
                document.querySelectorAll('.dia-card').forEach(c => c.classList.remove('abierto'));
                abiertos.forEach(function (f) {
                    const card = document.getElementById('dia-' + f);
                    if (card) card.classList.add('abierto');
                });
            }
        })();

        // Copia local de todos los datos
        (function () {
            try {
                const datos = JSON.parse(document.getElementById('datos-json').textContent);
                guardarCacheLocal(datos);
                const cache = leerCacheLocal();
                if (cache) {
                    document.getElementById('cacheNote').textContent =
                        '💾 Copia local guardada: ' + new Date(cache.guardado).toLocaleString('es-AR');
                }
            } catch (e) { console.warn(e); }
        })();
    </script>
</body>
</html>
"""


HTML_EDIT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Local N° {{ registro.numero }}</title>
    <style>""" + BASE_CSS + """
    </style>
</head>
<body>
<div class="page">
    <div class="topbar">
        <h2>✏️ Editar local N° {{ registro.numero }}</h2>
        <div class="navlinks"><a href="{{ url_for('dashboard') }}">📊 Volver</a></div>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="alert">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <div class="card">
        <form method="POST" enctype="multipart/form-data">
            <div class="field">
                <label>Local</label>
                <input type="text" name="local" required value="{{ registro.nombre }}">
            </div>

            <div class="field">
                <label>Calle</label>
                <input type="text" name="calle" list="calles_registradas" required value="{{ calle_actual }}" autocomplete="off">
                <datalist id="calles_registradas">
                    {% for calle in calles %}
                        <option value="{{ calle }}"></option>
                    {% endfor %}
                </datalist>
            </div>

            <div class="field">
                <label>Altura</label>
                <input type="text" name="altura" required value="{{ altura_actual }}">
            </div>

            <div class="field">
                <label>Objeción (si aplica)</label>
                <select name="objecion">
                    <option value="" {% if not registro.objecion %}selected{% endif %}>Sin objeción / venta realizada</option>
                    <option value="{{ objecion_random }}">🎲 Random — elige una al azar</option>
                    {% for obj in objeciones %}
                        <option value="{{ obj }}" {% if registro.objecion == obj %}selected{% endif %}>{{ obj }}</option>
                    {% endfor %}
                </select>
            </div>

            <div class="field">
                <label>Foto actual</label>
                <img class="foto-actual" src="{{ url_for('uploaded_file', filename=registro.foto) }}"
                     alt="Foto actual" onclick="abrirZoom(this.src)">
                <div class="foto-hint">Click para hacer zoom. Subí una nueva más abajo solo si querés reemplazarla.</div>

                <label style="margin-top:14px;">Reemplazar foto (opcional)</label>
                <input type="file" name="foto" id="fotoInput" accept="image/*" onchange="mostrarPreview(event)">
                <div class="preview-box" id="previewBox">
                    <img class="preview-thumb" id="previewImg" alt="Vista previa" onclick="abrirZoom(this.src)">
                    <div class="preview-hint">Click en la imagen para hacer zoom</div>
                </div>
            </div>

            <button type="submit" class="btn-primary">Guardar cambios</button>
        </form>
    </div>
</div>
""" + ZOOM_HTML + """
    <script>
        function mostrarPreview(event) {
            const file = event.target.files[0];
            const box = document.getElementById('previewBox');
            const img = document.getElementById('previewImg');
            if (!file) { box.style.display = 'none'; img.src = ''; return; }
            const reader = new FileReader();
            reader.onload = function(e) { img.src = e.target.result; box.style.display = 'block'; };
            reader.readAsDataURL(file);
        }
        """ + ZOOM_JS + """
    </script>
</body>
</html>
"""


def datos_para_cache():
    """Snapshot JSON del historial completo, para espejar en localStorage."""
    with lock:
        items = []
        for r in registros.values():
            item = {k: v for k, v in r.items() if k != "filepath"}
            item["fecha_larga"] = fecha_larga(r.get("fecha", ""))
            items.append(item)
    items.sort(key=lambda r: r["uid"], reverse=True)
    return json.dumps({"registros": items}, ensure_ascii=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    global uid_counter
    calles_actuales = obtener_calles_actualizadas()

    if request.method == 'POST':
        nombre_local = request.form.get('local')
        calle = request.form.get('calle', '').strip()
        altura = request.form.get('altura', '').strip()
        objecion = request.form.get('objecion', '').strip()
        if objecion == OBJECION_RANDOM:
            objecion = random.choice(OBJECIONES)
        foto = request.files.get('foto')

        if calle:
            with lock:
                estado_calles["calles"].add(calle)

        direccion_completa = f"{calle} {altura}"

        if foto:
            numero_dia = proximo_numero_del_dia()
            with lock:
                uid = uid_counter
                uid_counter += 1

            filename = f"local_{uid}_{foto.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            foto.save(filepath)

            hora_registro = datetime.now(ARG_TZ)

            # Se guarda primero con un horario provisorio: el cálculo
            # definitivo (repartido entre TODOS los pendientes de hoy,
            # incluido este) lo hace recalcular_horarios_pendientes().
            with lock:
                registros[uid] = {
                    "uid": uid,
                    "numero": numero_dia,
                    "fecha": hora_registro.strftime("%Y-%m-%d"),
                    "nombre": nombre_local,
                    "direccion": direccion_completa,
                    "objecion": objecion,
                    "hora_registro": hora_registro.strftime("%H:%M:%S"),
                    "hora_programada": "",
                    "hora_programada_iso": "",
                    "hora_envio_real": "",
                    "estado": "pendiente",
                    "foto": filename,
                    "filepath": filepath,
                    "hora_manual": False,
                }

            recalcular_horarios_pendientes()

            with lock:
                hora_envio_str = registros[uid]["hora_programada"]

            flash(f"✅ Registro guardado. Notificación programada para las {hora_envio_str} (Local N° {numero_dia}).")
            return redirect(url_for('index'))

    return render_template_string(
        HTML_FORM,
        calles=calles_actuales,
        objeciones=OBJECIONES,
        total_locales=contar_locales_hoy(),
        objetivo=TOTAL_LOCALES_OBJETIVO,
        objecion_random=OBJECION_RANDOM,
        datos_json=datos_para_cache(),
    )


@app.route('/dashboard')
def dashboard():
    verificar_dia()
    lista_hoy = sorted(registros_de_hoy(), key=lambda r: r["uid"], reverse=True)
    lista_con_url = []
    for r in lista_hoy:
        item = dict(r)
        item["direccion_url"] = quote(r["direccion"])
        lista_con_url.append(item)
    return render_template_string(
        HTML_DASHBOARD,
        registros=lista_con_url,
        total_locales=contar_locales_hoy(),
        objetivo=TOTAL_LOCALES_OBJETIVO,
        datos_json=datos_para_cache(),
    )


@app.route('/lista')
def lista():
    """
    Historial completo agrupado por fecha, en menús desplegables:
    "Jueves 19 de Septiembre ▼". Acá sólo se puede re-enviar la info.
    """
    verificar_dia()
    with lock:
        todos = list(registros.values())

    agrupado = {}
    for r in todos:
        agrupado.setdefault(r.get("fecha", ""), []).append(r)

    dias = []
    for fecha in sorted(agrupado.keys(), reverse=True):   # más reciente primero
        locales = sorted(agrupado[fecha], key=lambda r: r["numero"])
        dias.append({
            "fecha": fecha,
            "fecha_larga": fecha_larga(fecha),
            "locales": locales,
        })

    return render_template_string(HTML_LISTA, dias=dias, datos_json=datos_para_cache())


@app.route('/reenviar/<int:uid>', methods=['POST'])
def reenviar(uid):
    """
    Re-envía la info de un local al chat, con un encabezado arriba de todo:
        R.E FECHA: Jueves 19 de Septiembre
    No cambia el estado del local ni su horario programado.
    """
    with lock:
        registro = registros.get(uid)

    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('lista'))

    encabezado = f"R.E FECHA: {fecha_larga(registro.get('fecha', ''))}"

    enviar_reporte_telegram(
        uid,
        registro["nombre"],
        registro["direccion"],
        registro.get("filepath"),
        registro["objecion"],
        encabezado=encabezado,
        numero_mostrado=registro["numero"],
    )

    flash(f"🔁 Local N° {registro['numero']} re-enviado al chat ({fecha_larga(registro.get('fecha', ''))}).")
    return redirect(url_for('lista'))


@app.route('/enviar_ahora/<int:uid>', methods=['POST'])
def enviar_ahora(uid):
    """Envía el reporte de un local de inmediato, sin esperar su turno programado."""
    with lock:
        registro = registros.get(uid)

    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('dashboard'))

    if registro["estado"] == "enviado":
        flash(f"ℹ️ El Local N° {registro['numero']} ya fue enviado.")
        return redirect(url_for('dashboard'))

    try:
        scheduler.remove_job(f"job_{uid}")
    except JobLookupError:
        pass

    enviar_reporte_telegram(
        uid, registro["nombre"], registro["direccion"],
        registro["filepath"], registro["objecion"],
    )

    flash(f"📤 Local N° {registro['numero']} enviado manualmente.")
    return redirect(url_for('dashboard'))


@app.route('/editar/<int:uid>', methods=['GET', 'POST'])
def editar(uid):
    """Permite corregir los datos de un local ya registrado (pendiente o enviado)."""
    with lock:
        registro = registros.get(uid)

    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nombre = request.form.get('local', '').strip()
        calle = request.form.get('calle', '').strip()
        altura = request.form.get('altura', '').strip()
        objecion = request.form.get('objecion', '').strip()
        if objecion == OBJECION_RANDOM:
            objecion = random.choice(OBJECIONES)
        foto = request.files.get('foto')

        if calle:
            with lock:
                estado_calles["calles"].add(calle)

        with lock:
            registro["nombre"] = nombre
            registro["direccion"] = f"{calle} {altura}".strip()
            registro["objecion"] = objecion

            if foto and foto.filename:
                filename = f"local_{uid}_{foto.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                foto.save(filepath)

                foto_anterior = registro.get("filepath")
                if foto_anterior and foto_anterior != filepath and os.path.exists(foto_anterior):
                    try:
                        os.remove(foto_anterior)
                    except OSError:
                        pass

                registro["foto"] = filename
                registro["filepath"] = filepath

        guardar_estado()
        flash(f"✏️ Local N° {registro['numero']} actualizado correctamente.")
        return redirect(url_for('dashboard'))

    partes = registro["direccion"].rsplit(" ", 1)
    if len(partes) == 2:
        calle_actual, altura_actual = partes
    else:
        calle_actual, altura_actual = registro["direccion"], ""

    return render_template_string(
        HTML_EDIT,
        registro=registro,
        calle_actual=calle_actual,
        altura_actual=altura_actual,
        calles=obtener_calles_actualizadas(),
        objeciones=OBJECIONES,
        objecion_random=OBJECION_RANDOM,
    )


@app.route('/eliminar/<int:uid>', methods=['POST'])
def eliminar(uid):
    """Elimina un local de la lista (pendiente o ya enviado) y su foto."""
    with lock:
        registro = registros.pop(uid, None)

    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('dashboard'))

    try:
        scheduler.remove_job(f"job_{uid}")
    except JobLookupError:
        pass

    filepath = registro.get("filepath")
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass

    if registro["estado"] == "pendiente":
        recalcular_horarios_pendientes()

    guardar_estado()
    flash(f"🗑️ Local N° {registro['numero']} eliminado.")
    return redirect(url_for('dashboard'))


@app.route('/ajustar_hora/<int:uid>', methods=['POST'])
def ajustar_hora(uid):
    """
    Fija manualmente el horario de envío de un local pendiente. A partir de
    ahí queda excluido del reparto automático hasta que se envíe o se lo
    vuelva a poner en automático.
    """
    with lock:
        registro = registros.get(uid)

    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('dashboard'))

    if registro["estado"] == "enviado":
        flash(f"ℹ️ El Local N° {registro['numero']} ya fue enviado, no se puede reprogramar.")
        return redirect(url_for('dashboard'))

    nueva_hora_str = request.form.get('nueva_hora', '').strip()
    try:
        hh, mm = map(int, nueva_hora_str.split(':')[:2])
        hora_elegida = dtime(hh, mm)
    except (ValueError, AttributeError):
        flash("⚠️ Formato de hora inválido.")
        return redirect(url_for('dashboard'))

    ahora = datetime.now(ARG_TZ)
    nueva_dt = ARG_TZ.localize(datetime.combine(ahora.date(), hora_elegida))

    if nueva_dt < ahora + timedelta(minutes=INTERVALO_MINIMO_MINUTOS):
        flash(f"⚠️ La hora tiene que ser al menos {INTERVALO_MINIMO_MINUTOS} minutos después de ahora.")
        return redirect(url_for('dashboard'))

    job_id = f"job_{uid}"
    try:
        scheduler.reschedule_job(job_id, trigger='date', run_date=nueva_dt)
    except JobLookupError:
        scheduler.add_job(
            func=enviar_reporte_telegram, trigger='date', run_date=nueva_dt, id=job_id,
            args=[uid, registro["nombre"], registro["direccion"],
                  registro["filepath"], registro["objecion"]]
        )

    with lock:
        registro["hora_programada"] = nueva_dt.strftime("%H:%M:%S")
        registro["hora_programada_iso"] = nueva_dt.isoformat()
        registro["hora_manual"] = True

    recalcular_horarios_pendientes()
    guardar_estado()

    flash(f"🕒 Hora del Local N° {registro['numero']} fijada manualmente a las {nueva_dt.strftime('%H:%M')}.")
    return redirect(url_for('dashboard'))


@app.route('/auto_hora/<int:uid>', methods=['POST'])
def auto_hora(uid):
    """Devuelve un local con hora fijada manualmente al reparto automático."""
    with lock:
        registro = registros.get(uid)

    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('dashboard'))

    if registro["estado"] == "enviado":
        flash(f"ℹ️ El Local N° {registro['numero']} ya fue enviado.")
        return redirect(url_for('dashboard'))

    with lock:
        registro["hora_manual"] = False

    recalcular_horarios_pendientes()
    guardar_estado()

    flash(f"🔄 Local N° {registro['numero']} vuelve al reparto automático.")
    return redirect(url_for('dashboard'))


@app.route('/api/objeciones')
def api_objeciones():
    """Lista de objeciones disponibles, en formato JSON."""
    return jsonify(OBJECIONES)


@app.route('/api/datos')
def api_datos():
    """Historial completo en JSON (lo mismo que se espeja en localStorage)."""
    return app.response_class(datos_para_cache(), mimetype='application/json')


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


cargar_estado()
reprogramar_jobs_pendientes()


if __name__ == '__main__':
    # use_reloader=False: con el reloader, Flask levanta 2 procesos y se
    # duplicarían los envíos programados del scheduler.
    app.run(debug=True, port=5000, use_reloader=False)