import os
import threading
from urllib.parse import quote

import requests
from datetime import datetime, timedelta
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
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Zona horaria de Argentina
ARG_TZ = pytz.timezone('America/Argentina/Buenos_Aires')

# Margen mínimo entre un envío y el siguiente
INTERVALO_MINUTOS = 18

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

# Estado en memoria: almacena la fecha del 'día actual' y las calles registradas
estado_calles = {
    "fecha": datetime.now(ARG_TZ).strftime("%Y-%m-%d"),
    "calles": set()
}

# Lock para proteger el estado compartido entre requests y el scheduler
lock = threading.Lock()

local_counter = 1

# Próxima hora disponible para despachar un mensaje (se va acumulando +18 min)
proxima_hora_disponible = None

# Registro de todos los locales enviados/pendientes, para el dashboard
# clave: numero de local -> dict con info
registros = {}

scheduler = BackgroundScheduler()
scheduler.start()


def obtener_calles_actualizadas():
    """Limpia las calles si cambió el día según la hora de Argentina."""
    hoy = datetime.now(ARG_TZ).strftime("%Y-%m-%d")
    if estado_calles["fecha"] != hoy:
        estado_calles["fecha"] = hoy
        estado_calles["calles"].clear()
    return sorted(list(estado_calles["calles"]))


def calcular_hora_envio():
    """
    Calcula la hora en la que debe enviarse el próximo reporte, respetando
    un margen mínimo de INTERVALO_MINUTOS entre un envío y el siguiente.

    Ejemplo:
      - 10:00 se registra Local A -> se agenda para 10:18 (10:00 + 18)
      - 10:02 se registra Local B -> como el último agendado fue 10:18,
        se agenda para 10:36 (10:18 + 18), NO para 10:20.
      - Si pasó mucho tiempo desde el último envío (la cola "se vació"),
        se agenda simplemente 18 min después de ahora.
    """
    global proxima_hora_disponible
    ahora = datetime.now(ARG_TZ)

    with lock:
        if proxima_hora_disponible and proxima_hora_disponible > ahora:
            base = proxima_hora_disponible
        else:
            base = ahora

        hora_envio = base + timedelta(minutes=INTERVALO_MINUTOS)
        proxima_hora_disponible = hora_envio

    return hora_envio


def enviar_reporte_telegram(num_local, nombre_local, direccion, filepath, objecion):
    """
    Envía el reporte del local por Telegram, pero DESGLOSADO en varios
    mensajes en vez de uno solo:
      1) la foto del local
      2) el nombre del local
      3) la dirección (calle + altura)
      4) la objeción registrada (o aviso de que no hubo objeción)
    """
    url_text = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    url_photo = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    # 1) Foto del local
    if os.path.exists(filepath):
        with open(filepath, 'rb') as photo_file:
            requests.post(
                url_photo,
                data={"chat_id": CHAT_ID, "caption": f"📌 Local N° {num_local}"},
                files={"photo": photo_file}
            )

    # 2) Nombre del local
    requests.post(url_text, json={
        "chat_id": CHAT_ID,
        "text": f"{nombre_local}",
        "parse_mode": "Markdown"
    })

    # 3) Dirección y altura
    requests.post(url_text, json={
        "chat_id": CHAT_ID,
        "text": f"{direccion}",
        "parse_mode": "Markdown"
    })

    # 4) Objeción
    texto_objecion = objecion if objecion else "Sin objeción registrada."
    requests.post(url_text, json={
        "chat_id": CHAT_ID,
        "text": f" {texto_objecion}",
        "parse_mode": "Markdown"
    })

    # Actualizar estado en el registro para que el dashboard lo refleje
    with lock:
        if num_local in registros:
            registros[num_local]["estado"] = "enviado"
            registros[num_local]["hora_envio_real"] = datetime.now(ARG_TZ).strftime("%H:%M:%S")


HTML_FORM = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro de Local</title>
    <style>
        body { font-family: system-ui, sans-serif; padding: 20px; max-width: 500px; margin: 0 auto; }
        .field { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="number"], input[type="file"], select {
            width: 100%; padding: 8px; box-sizing: border-box;
        }
        button { background: #0088cc; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
        .alert { background: #d4edda; color: #155724; padding: 10px; margin-bottom: 15px; border-radius: 4px; }
        .grid { display: flex; gap: 10px; }
        .grid .field { flex: 1; }
        .topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .topbar a { color: #0088cc; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="topbar">
        <h2>Formulario de Registro</h2>
        <a href="{{ url_for('dashboard') }}">📊 Ver Dashboard</a>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="alert">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <form method="POST" enctype="multipart/form-data">
        <div class="field">
            <label>Local:</label>
            <input type="text" name="local" required placeholder="Ej: Sucursal Centro">
        </div>

        <div class="field">
            <label>Calle (Nombre):</label>
            <!-- Usa datalist: permite seleccionar una calle registrada o escribir una nueva -->
            <input type="text" name="calle" list="calles_registradas" required placeholder="Ej: Av. Corrientes" autocomplete="off">
            <datalist id="calles_registradas">
                {% for calle in calles %}
                    <option value="{{ calle }}"></option>
                {% endfor %}
            </datalist>
        </div>

        <div class="field">
            <label>Altura (Número):</label>
            <input type="text" name="altura" required placeholder="Ej: 1234">
        </div>

        <div class="field">
            <label>Objeción (si aplica):</label>
            <select name="objecion">
                <option value="">-- Sin objeción / Venta realizada --</option>
                {% for obj in objeciones %}
                    <option value="{{ obj }}">{{ obj }}</option>
                {% endfor %}
            </select>
        </div>

        <div class="field">
            <label>Foto del local:</label>
            <input type="file" name="foto" accept="image/*" required>
        </div>
        <button type="submit">Enviar Registro</button>
    </form>
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
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: system-ui, sans-serif; padding: 20px; max-width: 1000px; margin: 0 auto; background: #f7f8fa; }
        .topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .topbar a { color: #0088cc; text-decoration: none; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        th, td { padding: 12px 10px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }
        th { background: #0088cc; color: white; }
        tr:last-child td { border-bottom: none; }
        .badge { padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .badge-pendiente { background: #fff3cd; color: #856404; }
        .badge-enviado { background: #d4edda; color: #155724; }
        .btn-maps { background: #0088cc; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 13px; white-space: nowrap; }
        .btn-maps:hover { background: #006ba1; }
        .btn-enviar { background: #28a745; color: white; padding: 6px 12px; border-radius: 4px; font-size: 13px; white-space: nowrap; border: none; cursor: pointer; }
        .btn-enviar:hover { background: #1e7e34; }
        .actions { display: flex; gap: 6px; flex-wrap: wrap; }
        .empty { text-align: center; padding: 40px; color: #888; }
        .countdown { font-size: 12px; color: #888; }
        .objecion-cell { max-width: 200px; font-size: 12px; color: #555; }
    </style>
</head>
<body>
    <div class="topbar">
        <h2>📊 Dashboard de Locales</h2>
        <a href="{{ url_for('index') }}">➕ Nuevo Registro</a>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="alert" style="background:#d4edda;color:#155724;padding:10px;margin-bottom:15px;border-radius:4px;">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% if registros %}
    <table>
        <thead>
            <tr>
                <th>N° Local</th>
                <th>Nombre</th>
                <th>Dirección</th>
                <th>Objeción</th>
                <th>Hora registrado</th>
                <th>Hora estimada de llegada</th>
                <th>Estado</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {% for r in registros %}
            <tr>
                <td>{{ r.numero }}</td>
                <td>{{ r.nombre }}</td>
                <td>{{ r.direccion }}</td>
                <td class="objecion-cell">{{ r.objecion if r.objecion else '—' }}</td>
                <td>{{ r.hora_registro }}</td>
                <td>
                    {{ r.hora_programada }}
                    {% if r.estado == 'pendiente' %}
                        <div class="countdown" data-target="{{ r.hora_programada_iso }}"></div>
                    {% endif %}
                </td>
                <td>
                    {% if r.estado == 'enviado' %}
                        <span class="badge badge-enviado">✅ Enviado</span>
                    {% else %}
                        <span class="badge badge-pendiente">⏳ En proceso</span>
                    {% endif %}
                </td>
                <td>
                    <div class="actions">
                        <a class="btn-maps" target="_blank" rel="noopener"
                           href="https://www.google.com/maps/search/?api=1&query={{ r.direccion_url }}">
                           📍 Dirección
                        </a>
                        {% if r.estado == 'pendiente' %}
                        <form method="POST" action="{{ url_for('enviar_ahora', num_local=r.numero) }}"
                              onsubmit="return confirm('¿Enviar el Local N° {{ r.numero }} ahora mismo?');">
                            <button type="submit" class="btn-enviar">📤 Enviar ahora</button>
                        </form>
                        {% endif %}
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
        <div class="empty">Todavía no hay locales registrados hoy.</div>
    {% endif %}

    <script>
        // Cuenta regresiva en vivo para los locales pendientes
        function actualizarCountdowns() {
            document.querySelectorAll('.countdown').forEach(function(el) {
                const target = new Date(el.dataset.target);
                const diffMs = target - new Date();
                if (diffMs <= 0) {
                    el.textContent = 'llegando...';
                    return;
                }
                const mins = Math.floor(diffMs / 60000);
                const secs = Math.floor((diffMs % 60000) / 1000);
                el.textContent = 'faltan ' + mins + 'm ' + secs.toString().padStart(2, '0') + 's';
            });
        }
        setInterval(actualizarCountdowns, 1000);
        actualizarCountdowns();
    </script>
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    global local_counter
    calles_actuales = obtener_calles_actualizadas()

    if request.method == 'POST':
        nombre_local = request.form.get('local')
        calle = request.form.get('calle', '').strip()
        altura = request.form.get('altura', '').strip()
        objecion = request.form.get('objecion', '').strip()
        foto = request.files.get('foto')

        if calle:
            estado_calles["calles"].add(calle)

        direccion_completa = f"{calle} {altura}"

        if foto:
            with lock:
                num_local = local_counter
                local_counter += 1

            filename = f"local_{num_local}_{foto.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            foto.save(filepath)

            hora_registro = datetime.now(ARG_TZ)
            hora_envio = calcular_hora_envio()

            # Guardar el registro para el dashboard
            with lock:
                registros[num_local] = {
                    "numero": num_local,
                    "nombre": nombre_local,
                    "direccion": direccion_completa,
                    "objecion": objecion,
                    "hora_registro": hora_registro.strftime("%H:%M:%S"),
                    "hora_programada": hora_envio.strftime("%H:%M:%S"),
                    "hora_programada_iso": hora_envio.isoformat(),
                    "estado": "pendiente",
                    "foto": filename,
                    "filepath": filepath,
                }

            scheduler.add_job(
                func=enviar_reporte_telegram,
                trigger='date',
                run_date=hora_envio,
                id=f"job_{num_local}",
                args=[num_local, nombre_local, direccion_completa, filepath, objecion]
            )

            flash(f"✅ Registro enviado. Notificación programada para las {hora_envio.strftime('%H:%M')} (Local N° {num_local}).")
            return redirect(url_for('index'))

    return render_template_string(HTML_FORM, calles=calles_actuales, objeciones=OBJECIONES)


@app.route('/dashboard')
def dashboard():
    # Mostrar los más recientes primero
    lista = sorted(registros.values(), key=lambda r: r["numero"], reverse=True)
    lista_con_url = []
    for r in lista:
        item = dict(r)
        item["direccion_url"] = quote(r["direccion"])
        lista_con_url.append(item)
    return render_template_string(HTML_DASHBOARD, registros=lista_con_url)


@app.route('/enviar_ahora/<int:num_local>', methods=['POST'])
def enviar_ahora(num_local):
    """Envía el reporte de un local de inmediato, sin esperar su turno programado."""
    with lock:
        registro = registros.get(num_local)

    if not registro:
        flash(f"⚠️ No se encontró el Local N° {num_local}.")
        return redirect(url_for('dashboard'))

    if registro["estado"] == "enviado":
        flash(f"ℹ️ El Local N° {num_local} ya fue enviado.")
        return redirect(url_for('dashboard'))

    # Cancelar el job programado (si todavía no se disparó)
    try:
        scheduler.remove_job(f"job_{num_local}")
    except JobLookupError:
        pass

    enviar_reporte_telegram(
        num_local,
        registro["nombre"],
        registro["direccion"],
        registro["filepath"],
        registro["objecion"],
    )

    flash(f"📤 Local N° {num_local} enviado manualmente.")
    return redirect(url_for('dashboard'))


@app.route('/api/objeciones')
def api_objeciones():
    """Lista de objeciones disponibles, en formato JSON."""
    return jsonify(OBJECIONES)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)