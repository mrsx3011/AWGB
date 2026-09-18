import os
import sys
import time
import random
import threading
import traceback
from datetime import datetime, timedelta, time as dtime, date
from urllib.parse import quote

import pymysql
import pymysql.cursors
import pytz
import requests
from flask import (
    Flask, render_template_string, request, flash, redirect, url_for,
    jsonify, session, Response
)
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED

ARG_TZ = pytz.timezone('America/Argentina/Buenos_Aires')


# ============================================================================
# LOG DE DEBUG (sale por la terminal)
# ============================================================================
def log(tag, msg=""):
    hora = datetime.now(ARG_TZ).strftime("%H:%M:%S")
    print(f"[{hora}] [{tag:<9}] {msg}", flush=True)


def _env(nombre, default=None):
    valor = os.environ.get(nombre, default)
    if valor in (None, ""):
        print(f"❌ Falta la variable de entorno: {nombre}", flush=True)
        sys.exit(1)
    return valor


app = Flask(__name__)
app.secret_key = _env("KEY_SECRET")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.permanent_session_lifetime = timedelta(days=30)

TELEGRAM_TOKEN = _env("TELEGRAM_TOKEN")
CHAT_ID = _env("CHAT_ID")

DB_CONFIG = dict(
    host=_env("DB_HOST"),
    port=int(os.environ.get("DB_PORT", 3306)),
    user=_env("DB_USER"),
    password=_env("DB_PASSWORD"),
    database=_env("DB_NAME"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,   # filas como dict  (¡faltaba!)
    autocommit=True,                          # confirma cada INSERT/UPDATE (¡faltaba!)
    connect_timeout=10,
)

HORA_APERTURA = dtime(10, 0)
HORA_CIERRE = dtime(15, 55)
BUFFER_INICIAL_MINUTOS = 18
INTERVALO_MINIMO_MINUTOS = 2
MARGEN_JITTER_MINUTOS = 20
TOTAL_LOCALES_OBJETIVO = 20
OBJECION_RANDOM = "Random"

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

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def fecha_larga(fecha_iso):
    try:
        d = datetime.strptime(str(fecha_iso), "%Y-%m-%d")
    except (ValueError, TypeError):
        return fecha_iso or ""
    return f"{DIAS_ES[d.weekday()]} {d.day} de {MESES_ES[d.month - 1]}"


lock = threading.Lock()
scheduler = BackgroundScheduler(timezone=ARG_TZ)


def _listener(event):
    """Muestra en consola el resultado de cada job (si no, los errores se tragan en silencio)."""
    if event.code == EVENT_JOB_ERROR:
        log("SCHEDULER", f"❌ El job {event.job_id} FALLÓ: {event.exception!r}")
        log("SCHEDULER", event.traceback or "")
    elif event.code == EVENT_JOB_MISSED:
        log("SCHEDULER", f"⚠️ El job {event.job_id} se perdió su horario (misfire)")
    else:
        log("SCHEDULER", f"✅ Job {event.job_id} ejecutado")


scheduler.add_listener(_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)
scheduler.start()


# ============================================================================
# BASE DE DATOS
# ============================================================================
def get_conn():
    t0 = time.time()
    try:
        conn = pymysql.connect(**DB_CONFIG)
    except Exception as e:
        log("DB", f"❌ No se pudo conectar a {DB_CONFIG['host']}:{DB_CONFIG['port']} "
                  f"(db={DB_CONFIG['database']}): {e!r}")
        raise
    log("DB", f"🔌 Conexión abierta ({(time.time() - t0) * 1000:.0f} ms)")
    return conn


def _resumen_args(args):
    """Resume los argumentos para el log (los BLOB de fotos se muestran como tamaño)."""
    out = []
    for a in args:
        if isinstance(a, (bytes, bytearray)):
            out.append(f"<{len(a)} bytes>")
        else:
            s = repr(a)
            out.append(s if len(s) < 60 else s[:57] + "...")
    return out


def _sql_corto(sql):
    return " ".join(sql.split())[:110]


def ejecutar(sql, args=()):
    """INSERT/UPDATE/DELETE. Devuelve lastrowid."""
    log("DB", f"✍️  {_sql_corto(sql)} | args={_resumen_args(args)}")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            filas = cur.execute(sql, args)
            conn.commit()   # explícito, por si autocommit falla
            log("DB", f"✅ OK -> filas afectadas={filas}, lastrowid={cur.lastrowid}")
            return cur.lastrowid
    except Exception as e:
        log("DB", f"❌ ERROR en escritura: {e!r}")
        raise
    finally:
        conn.close()


def _norm(r):
    if r is None:
        return None
    if isinstance(r.get("fecha"), date):
        r["fecha"] = r["fecha"].isoformat()
    if "hora_manual" in r:
        r["hora_manual"] = bool(r["hora_manual"])
    return r


def uno(sql, args=()):
    log("DB", f"🔎 {_sql_corto(sql)} | args={_resumen_args(args)}")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            fila = cur.fetchone()
            log("DB", f"   -> {'1 fila' if fila else 'sin resultados'}")
            return _norm(fila)
    except Exception as e:
        log("DB", f"❌ ERROR en lectura: {e!r}")
        raise
    finally:
        conn.close()


def todos(sql, args=()):
    log("DB", f"🔎 {_sql_corto(sql)} | args={_resumen_args(args)}")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            filas = cur.fetchall()
            log("DB", f"   -> {len(filas)} fila(s)")
            return [_norm(r) for r in filas]
    except Exception as e:
        log("DB", f"❌ ERROR en lectura: {e!r}")
        raise
    finally:
        conn.close()


CAMPOS = ("id AS uid, usuario, nombre, direccion, objecion, fecha, numero, estado, "
          "hora_registro, hora_programada, hora_programada_iso, hora_envio_real, hora_manual")


def probar_conexion():
    """Chequeo de arranque: si algo está mal con la BD, se ve ACÁ."""
    log("ARRANQUE", "=" * 60)
    log("ARRANQUE", "🚀 Versión con MySQL (Clever Cloud) — NO usa datos.json ni localStorage")
    log("ARRANQUE", f"🗄️  Host={DB_CONFIG['host']}:{DB_CONFIG['port']} "
                    f"| DB={DB_CONFIG['database']} | user={DB_CONFIG['user']}")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DATABASE() AS db, VERSION() AS v, @@autocommit AS ac")
            info = cur.fetchone()
            log("ARRANQUE", f"✅ Conectado a '{info['db']}' | MySQL {info['v']} | autocommit={info['ac']}")
    finally:
        conn.close()


def init_db():
    probar_conexion()
    ejecutar("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(150) NOT NULL UNIQUE,
            username VARCHAR(80) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        ) CHARACTER SET utf8mb4
    """)
    ejecutar("""
        CREATE TABLE IF NOT EXISTS locales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(80) NOT NULL,
            nombre VARCHAR(200) NOT NULL,
            direccion VARCHAR(255) NOT NULL,
            objecion VARCHAR(255) NOT NULL DEFAULT '',
            foto LONGBLOB,
            foto_mime VARCHAR(60),
            fecha DATE NOT NULL,
            numero INT NOT NULL,
            estado VARCHAR(12) NOT NULL DEFAULT 'pendiente',
            hora_registro VARCHAR(8) NOT NULL DEFAULT '',
            hora_programada VARCHAR(8) NOT NULL DEFAULT '',
            hora_programada_iso VARCHAR(40) NOT NULL DEFAULT '',
            hora_envio_real VARCHAR(8) NOT NULL DEFAULT '',
            hora_manual TINYINT(1) NOT NULL DEFAULT 0,
            INDEX idx_usuario_fecha (usuario, fecha)
        ) CHARACTER SET utf8mb4
    """)
    nu = uno("SELECT COUNT(*) AS n FROM usuarios")["n"]
    nl = uno("SELECT COUNT(*) AS n FROM locales")["n"]
    log("ARRANQUE", f"📊 Estado actual de la BD: {nu} usuario(s), {nl} local(es)")
    if nu == 0:
        log("ARRANQUE", "⚠️ No hay usuarios. Creá uno con: python app.py crear_usuario mail user pass")


def crear_usuario(email, username, password):
    ejecutar("INSERT INTO usuarios (email, username, password) VALUES (%s, %s, %s)",
             (email.strip().lower(), username.strip(), generate_password_hash(password)))


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


# ============================================================================
# PROGRAMACIÓN DE ENVÍOS
# ============================================================================
def _agendar(uid, run_date):
    scheduler.add_job(
        func=enviar_reporte_telegram, trigger='date', run_date=run_date,
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
        _agendar(r["uid"], run_date)
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
            _agendar(reg["uid"], h)


# ---------------------------- Telegram --------------------------------------
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
        # Un nombre con _ o * rompe el Markdown: se reintenta como texto plano
        log("TELEGRAM", "↩️ Reintentando sin Markdown")
        resp = _telegram("sendMessage", json={"chat_id": CHAT_ID, "text": texto})
    resp.raise_for_status()


def enviar_reporte_telegram(uid, encabezado=None):
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
        raise   # el local queda 'pendiente' (no se marca como enviado si Telegram falló)


# ============================================================================
# LOGIN
# ============================================================================
@app.before_request
def exigir_login():
    if request.endpoint != "foto":
        log("HTTP", f"{request.method} {request.path} | usuario={session.get('usuario')}")
    if request.endpoint in ("login", "static"):
        return
    if "usuario" not in session:
        log("LOGIN", f"🔒 Sin sesión, redirigiendo a /login (pedía {request.path})")
        return redirect(url_for("login"))


def usuario_actual():
    return session["usuario"]


HTML_LOGIN = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar sesión</title>
    <style>%%BASE_CSS%%

        body.login-body{
            min-height:100vh; display:flex; align-items:center; justify-content:center;
            padding:24px 16px;
        }
        .login-box{ width:100%; max-width:400px; }

        .login-head{ text-align:center; margin-bottom:22px; }
        .login-logo{
            width:56px; height:56px; margin:0 auto 14px; border-radius:16px;
            background:var(--brand-100); color:var(--brand-600);
            display:flex; align-items:center; justify-content:center; font-size:26px;
            border:1px solid #cfe5ee; box-shadow:var(--shadow-card);
        }
        .login-head h2{ font-size:22px; }
        .login-sub{ font-size:13.5px; color:var(--ink-600); margin-top:6px; }

        .login-card{ padding:24px 22px; }

        .alert-error{
            background:var(--red-100); color:var(--red-700); border:1px solid #efc7c2;
            padding:11px 14px; margin-bottom:16px; border-radius:var(--radius-sm);
            font-size:13.5px; font-weight:500;
        }

        .input-wrap{ position:relative; }
        .input-wrap input{ padding-right:44px; }
        .toggle-pass{
            position:absolute; right:6px; top:50%; transform:translateY(-50%);
            width:34px; height:34px; border:none; background:none; cursor:pointer;
            border-radius:8px; font-size:16px; color:var(--ink-600);
            display:flex; align-items:center; justify-content:center;
        }
        .toggle-pass:hover{ background:var(--paper); }

        .btn-primary:disabled{ opacity:.7; cursor:wait; }
        .login-foot{ text-align:center; font-size:11.5px; color:var(--ink-300); margin-top:18px; }
    </style>
</head>
<body class="login-body">
<div class="login-box">
    <div class="login-head">
        <div class="login-logo">📍</div>
        <h2>Iniciar sesión</h2>
        <div class="login-sub">Ingresá para registrar y enviar tus locales</div>
    </div>

    <div class="card login-card">
        {% with messages = get_flashed_messages() %}
          {% if messages %}{% for message in messages %}<div class="alert-error">{{ message }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <form method="POST" id="loginForm">
            <div class="field">
                <label for="identificador">Usuario o email</label>
                <input type="text" id="identificador" name="identificador" required autofocus
                       autocomplete="username" placeholder="Ej: tuusuario">
            </div>

            <div class="field">
                <label for="password">Contraseña</label>
                <div class="input-wrap">
                    <input type="password" id="password" name="password" required
                           autocomplete="current-password" placeholder="••••••••">
                    <button type="button" class="toggle-pass" id="togglePass"
                            aria-label="Mostrar u ocultar contraseña" onclick="verPassword()">👁️</button>
                </div>
            </div>

            <button type="submit" class="btn-primary" id="btnEntrar">Entrar</button>
        </form>
    </div>

    <div class="login-foot">Acceso restringido</div>
</div>

<script>
    function verPassword() {
        const input = document.getElementById('password');
        const btn = document.getElementById('togglePass');
        const oculto = input.type === 'password';
        input.type = oculto ? 'text' : 'password';
        btn.textContent = oculto ? '🙈' : '👁️';
    }

    // Evita el doble envío (en tu log aparecía POST /login dos veces)
    const form = document.getElementById('loginForm');
    const btn = document.getElementById('btnEntrar');
    form.addEventListener('submit', function () {
        btn.disabled = true;
        btn.textContent = 'Entrando...';
    });
    // Si el usuario vuelve con el botón "atrás", se rehabilita el botón
    window.addEventListener('pageshow', function () {
        btn.disabled = false;
        btn.textContent = 'Entrar';
    });
</script>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ident = request.form.get('identificador', '').strip()
        password = request.form.get('password', '')
        log("LOGIN", f"Intento de login con '{ident}'")
        u = uno("SELECT username, password FROM usuarios WHERE username=%s OR email=%s",
                (ident, ident.lower()))
        if not u:
            log("LOGIN", f"❌ No existe ningún usuario/email '{ident}' en la tabla usuarios")
        elif not check_password_hash(u["password"], password):
            log("LOGIN", f"❌ Contraseña incorrecta para '{u['username']}'")
        else:
            session.clear()
            session.permanent = True
            session["usuario"] = u["username"]
            log("LOGIN", f"✅ Sesión iniciada: {u['username']}")
            return redirect(url_for('index'))
        flash("⚠️ Usuario o contraseña incorrectos.")
    return render_template_string(HTML_LOGIN)


@app.route('/logout')
def logout():
    log("LOGIN", f"👋 Logout de {session.get('usuario')}")
    session.clear()
    return redirect(url_for('login'))


# ============================================================================
# DISEÑO
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
input[type="text"], input[type="password"], input[type="number"], input[type="file"], input[type="time"], select{
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

HTML_LOGIN = HTML_LOGIN.replace("%%BASE_CSS%%", BASE_CSS)

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
            <a href="{{ url_for('logout') }}">🚪 Salir ({{ session['usuario'] }})</a>
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
      {% if messages %}{% for message in messages %}<div class="alert">{{ message }}</div>{% endfor %}{% endif %}
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
                    {% for calle in calles %}<option value="{{ calle }}"></option>{% endfor %}
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
                    {% for obj in objeciones %}<option value="{{ obj }}">{{ obj }}</option>{% endfor %}
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
</div>
""" + ZOOM_HTML + """
    <script>
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
            <a href="{{ url_for('logout') }}">🚪 Salir ({{ session['usuario'] }})</a>
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
      {% if messages %}{% for message in messages %}<div class="alert">{{ message }}</div>{% endfor %}{% endif %}
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
                    <img class="thumb" src="{{ url_for('foto', uid=r.uid) }}"
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
                        {% if r.estado == 'pendiente' %}
                        <form method="POST" action="{{ url_for('enviar_ahora', uid=r.uid) }}"
                              onsubmit="return confirm('¿Enviar el Local N° {{ r.numero }} ahora mismo?');">
                            <button type="submit" class="btn-pill btn-enviar">📤 Enviar</button>
                        </form>
                        {% else %}
                        <span class="btn-pill chip-enviado">✅ Enviado</span>
                        {% endif %}

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
</div>
""" + ZOOM_HTML + """
    <script>
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

        setInterval(function () {
            if (!document.querySelector('.conf-panel.abierto')) window.location.reload();
        }, 30000);
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
            <a href="{{ url_for('logout') }}">🚪 Salir ({{ session['usuario'] }})</a>
        </div>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}{% for message in messages %}<div class="alert">{{ message }}</div>{% endfor %}{% endif %}
    {% endwith %}

    {% if dias %}
        {% for dia in dias %}
        <div class="dia-card {% if loop.first %}abierto{% endif %}" id="dia-{{ dia.fecha }}">
            <button type="button" class="dia-header" onclick="toggleDia('{{ dia.fecha }}')">
                <div class="dia-titulo"><span class="dia-nombre">{{ dia.fecha_larga }}</span></div>
                <div class="dia-meta">
                    <span class="dia-count">{{ dia.locales|length }} local{{ 'es' if dia.locales|length != 1 else '' }}</span>
                    <span class="flecha">▼</span>
                </div>
            </button>
            <div class="dia-body">
                {% for r in dia.locales %}
                <div class="local-row">
                    <img class="local-foto" src="{{ url_for('foto', uid=r.uid) }}"
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
</div>
""" + ZOOM_HTML + """
    <script>
        """ + ZOOM_JS + """
        function toggleDia(fecha) {
            const card = document.getElementById('dia-' + fecha);
            if (card) card.classList.toggle('abierto');
        }
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
      {% if messages %}{% for message in messages %}<div class="alert">{{ message }}</div>{% endfor %}{% endif %}
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
                    {% for calle in calles %}<option value="{{ calle }}"></option>{% endfor %}
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
                <img class="foto-actual" src="{{ url_for('foto', uid=registro.uid) }}"
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




# ============================================================================
# RUTAS
# ============================================================================
@app.route('/', methods=['GET', 'POST'])
def index():
    usuario = usuario_actual()

    if request.method == 'POST':
        nombre_local = request.form.get('local', '').strip()
        calle = request.form.get('calle', '').strip()
        altura = request.form.get('altura', '').strip()
        objecion = request.form.get('objecion', '').strip()
        if objecion == OBJECION_RANDOM:
            objecion = random.choice(OBJECIONES)
            log("REGISTRO", f"🎲 Objeción random elegida: {objecion}")
        foto = request.files.get('foto')

        log("REGISTRO", f"Formulario recibido: local='{nombre_local}', calle='{calle}', "
                        f"altura='{altura}', objecion='{objecion}', "
                        f"foto={'sí (' + foto.filename + ')' if foto and foto.filename else 'NO'}")

        if foto and foto.filename:
            contenido = foto.read()
            log("REGISTRO", f"📷 Foto leída: {len(contenido)} bytes, mime={foto.mimetype}")
            if not contenido:
                flash("⚠️ La foto llegó vacía, probá de nuevo.")
                return redirect(url_for('index'))

            numero_dia = proximo_numero_del_dia(usuario)
            ahora = datetime.now(ARG_TZ)
            try:
                uid = ejecutar(
                    "INSERT INTO locales (usuario, nombre, direccion, objecion, foto, foto_mime, fecha, numero, "
                    "estado, hora_registro) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'pendiente',%s)",
                    (usuario, nombre_local, f"{calle} {altura}".strip(), objecion,
                     contenido, foto.mimetype or "image/jpeg",
                     ahora.strftime("%Y-%m-%d"), numero_dia, ahora.strftime("%H:%M:%S")))
            except Exception as e:
                log("REGISTRO", f"❌ NO se pudo guardar en la BD: {e!r}")
                log("REGISTRO", traceback.format_exc())
                flash("❌ Error al guardar en la base de datos. Mirá la consola del servidor.")
                return redirect(url_for('index'))

            # Verificación: se relee con una conexión NUEVA para confirmar que quedó persistido
            verif = uno("SELECT id, usuario, nombre, LENGTH(foto) AS bytes_foto FROM locales WHERE id=%s", (uid,))
            if verif:
                log("REGISTRO", f"💾 VERIFICADO en BD: id={verif['id']}, usuario={verif['usuario']}, "
                                f"nombre={verif['nombre']}, foto={verif['bytes_foto']} bytes")
            else:
                log("REGISTRO", f"🚨 El INSERT devolvió id={uid} pero la fila NO está en la BD (¿commit?)")

            recalcular_horarios_pendientes(usuario)
            reg = obtener_local(uid)
            flash(f"✅ Registro guardado. Notificación programada para las {reg['hora_programada']} (Local N° {numero_dia}).")
            return redirect(url_for('index'))

    return render_template_string(
        HTML_FORM,
        calles=calles_de_hoy(usuario),
        objeciones=OBJECIONES,
        total_locales=contar_locales_hoy(usuario),
        objetivo=TOTAL_LOCALES_OBJETIVO,
        objecion_random=OBJECION_RANDOM,
    )


@app.route('/dashboard')
def dashboard():
    usuario = usuario_actual()
    lista_hoy = locales_de_hoy(usuario)
    log("DASHBOARD", f"{len(lista_hoy)} local(es) de hoy para '{usuario}'")
    for r in lista_hoy:
        r["direccion_url"] = quote(r["direccion"])
    return render_template_string(
        HTML_DASHBOARD,
        registros=lista_hoy,
        total_locales=len(lista_hoy),
        objetivo=TOTAL_LOCALES_OBJETIVO,
    )


@app.route('/lista')
def lista():
    usuario = usuario_actual()
    todos_ = todos(f"SELECT {CAMPOS} FROM locales WHERE usuario=%s ORDER BY fecha DESC, numero ASC", (usuario,))
    agrupado = {}
    for r in todos_:
        agrupado.setdefault(r["fecha"], []).append(r)
    dias = [{"fecha": f, "fecha_larga": fecha_larga(f), "locales": l} for f, l in agrupado.items()]
    log("LISTA", f"{len(todos_)} local(es) en {len(dias)} día(s)")
    return render_template_string(HTML_LISTA, dias=dias)


@app.route('/foto/<int:uid>')
def foto(uid):
    r = uno("SELECT usuario, foto, foto_mime FROM locales WHERE id=%s", (uid,))
    if not r or r["usuario"] != usuario_actual() or not r["foto"]:
        return Response(status=404)
    resp = Response(r["foto"], mimetype=r["foto_mime"] or "image/jpeg")
    resp.headers["Cache-Control"] = "private, max-age=3600"
    return resp


@app.route('/reenviar/<int:uid>', methods=['POST'])
def reenviar(uid):
    registro = obtener_local(uid, usuario_actual())
    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('lista'))
    try:
        enviar_reporte_telegram(uid, encabezado=f"R.E FECHA: {fecha_larga(registro['fecha'])}")
        flash(f"🔁 Local N° {registro['numero']} re-enviado al chat ({fecha_larga(registro['fecha'])}).")
    except Exception as e:
        flash(f"❌ No se pudo re-enviar: {e}")
    return redirect(url_for('lista'))


@app.route('/enviar_ahora/<int:uid>', methods=['POST'])
def enviar_ahora(uid):
    registro = obtener_local(uid, usuario_actual())
    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('dashboard'))
    if registro["estado"] == "enviado":
        flash(f"ℹ️ El Local N° {registro['numero']} ya fue enviado.")
        return redirect(url_for('dashboard'))

    if scheduler.get_job(f"job_{uid}"):
        scheduler.remove_job(f"job_{uid}")
        log("SCHEDULER", f"🗑️ Job job_{uid} removido (envío manual)")
    try:
        enviar_reporte_telegram(uid)
        flash(f"📤 Local N° {registro['numero']} enviado manualmente.")
    except Exception as e:
        reprogramar_jobs_pendientes()   # como falló, se vuelve a agendar
        flash(f"❌ No se pudo enviar (queda pendiente): {e}")
    return redirect(url_for('dashboard'))


@app.route('/editar/<int:uid>', methods=['GET', 'POST'])
def editar(uid):
    usuario = usuario_actual()
    registro = obtener_local(uid, usuario)
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
        foto_nueva = request.files.get('foto')
        log("EDITAR", f"Local id={uid}: nombre='{nombre}', dir='{calle} {altura}', objecion='{objecion}', "
                      f"foto_nueva={'sí' if foto_nueva and foto_nueva.filename else 'no'}")

        ejecutar("UPDATE locales SET nombre=%s, direccion=%s, objecion=%s WHERE id=%s",
                 (nombre, f"{calle} {altura}".strip(), objecion, uid))
        if foto_nueva and foto_nueva.filename:
            ejecutar("UPDATE locales SET foto=%s, foto_mime=%s WHERE id=%s",
                     (foto_nueva.read(), foto_nueva.mimetype or "image/jpeg", uid))

        flash(f"✏️ Local N° {registro['numero']} actualizado correctamente.")
        return redirect(url_for('dashboard'))

    partes = registro["direccion"].rsplit(" ", 1)
    calle_actual, altura_actual = (partes if len(partes) == 2 else (registro["direccion"], ""))
    return render_template_string(
        HTML_EDIT,
        registro=registro,
        calle_actual=calle_actual,
        altura_actual=altura_actual,
        calles=calles_de_hoy(usuario),
        objeciones=OBJECIONES,
        objecion_random=OBJECION_RANDOM,
    )


@app.route('/eliminar/<int:uid>', methods=['POST'])
def eliminar(uid):
    usuario = usuario_actual()
    registro = obtener_local(uid, usuario)
    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('dashboard'))

    if scheduler.get_job(f"job_{uid}"):
        scheduler.remove_job(f"job_{uid}")
    ejecutar("DELETE FROM locales WHERE id=%s", (uid,))
    log("ELIMINAR", f"🗑️ Local id={uid} (N° {registro['numero']}) eliminado de la BD")

    if registro["estado"] == "pendiente":
        recalcular_horarios_pendientes(usuario)

    flash(f"🗑️ Local N° {registro['numero']} eliminado.")
    return redirect(url_for('dashboard'))


@app.route('/ajustar_hora/<int:uid>', methods=['POST'])
def ajustar_hora(uid):
    usuario = usuario_actual()
    registro = obtener_local(uid, usuario)
    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('dashboard'))
    if registro["estado"] == "enviado":
        flash(f"ℹ️ El Local N° {registro['numero']} ya fue enviado, no se puede reprogramar.")
        return redirect(url_for('dashboard'))

    try:
        hh, mm = map(int, request.form.get('nueva_hora', '').strip().split(':')[:2])
        hora_elegida = dtime(hh, mm)
    except (ValueError, AttributeError):
        flash("⚠️ Formato de hora inválido.")
        return redirect(url_for('dashboard'))

    ahora = datetime.now(ARG_TZ)
    nueva_dt = ARG_TZ.localize(datetime.combine(ahora.date(), hora_elegida))
    if nueva_dt < ahora + timedelta(minutes=INTERVALO_MINIMO_MINUTOS):
        flash(f"⚠️ La hora tiene que ser al menos {INTERVALO_MINIMO_MINUTOS} minutos después de ahora.")
        return redirect(url_for('dashboard'))

    log("HORARIOS", f"🔒 Hora manual para local id={uid}: {nueva_dt.strftime('%H:%M')}")
    ejecutar("UPDATE locales SET hora_programada=%s, hora_programada_iso=%s, hora_manual=1 WHERE id=%s",
             (nueva_dt.strftime("%H:%M:%S"), nueva_dt.isoformat(), uid))
    _agendar(uid, nueva_dt)
    recalcular_horarios_pendientes(usuario)

    flash(f"🕒 Hora del Local N° {registro['numero']} fijada manualmente a las {nueva_dt.strftime('%H:%M')}.")
    return redirect(url_for('dashboard'))


@app.route('/auto_hora/<int:uid>', methods=['POST'])
def auto_hora(uid):
    usuario = usuario_actual()
    registro = obtener_local(uid, usuario)
    if not registro:
        flash("⚠️ No se encontró ese local.")
        return redirect(url_for('dashboard'))
    if registro["estado"] == "enviado":
        flash(f"ℹ️ El Local N° {registro['numero']} ya fue enviado.")
        return redirect(url_for('dashboard'))

    log("HORARIOS", f"🔄 Local id={uid} vuelve a modo automático")
    ejecutar("UPDATE locales SET hora_manual=0 WHERE id=%s", (uid,))
    recalcular_horarios_pendientes(usuario)
    flash(f"🔄 Local N° {registro['numero']} vuelve al reparto automático.")
    return redirect(url_for('dashboard'))


@app.route('/api/objeciones')
def api_objeciones():
    return jsonify(OBJECIONES)


@app.errorhandler(Exception)
def error_global(e):
    """Cualquier excepción no capturada se imprime completa en la terminal."""
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    log("ERROR", f"💥 Excepción en {request.method} {request.path}: {e!r}")
    log("ERROR", traceback.format_exc())
    return "Error interno. Revisá la consola del servidor.", 500


# ============================================================================
# ARRANQUE
# ============================================================================
init_db()
reprogramar_jobs_pendientes()

if __name__ == '__main__':
    # python app.py crear_usuario correo@ejemplo.com miusuario micontraseña
    if len(sys.argv) == 5 and sys.argv[1] == "crear_usuario":
        crear_usuario(sys.argv[2], sys.argv[3], sys.argv[4])
        log("USUARIOS", f"✅ Usuario '{sys.argv[3]}' creado.")
        sys.exit(0)

    log("ARRANQUE", "🌐 Servidor listo")
    app.run(debug=False, port=int(os.environ.get("PORT", 5000)), use_reloader=False)