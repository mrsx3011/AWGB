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
.input-action-row{ display:flex; gap:8px; align-items:stretch; }
.input-action-row input{ flex:1; min-width:0; }
.icon-action{
    border:1px solid var(--line); background:var(--surface); color:var(--ink-700);
    border-radius:var(--radius-sm); padding:0 11px; min-width:42px; cursor:pointer;
    display:inline-flex; align-items:center; justify-content:center; gap:6px; font-weight:600;
}
.icon-action:hover{ background:var(--paper); }
.icon-action:disabled{ opacity:.68; cursor:wait; }
.field-status{ margin-top:6px; font-size:12px; color:var(--ink-600); min-height:16px; }
.photo-actions{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.photo-action{
    border:1px solid var(--line); background:var(--surface); color:var(--ink-700);
    border-radius:var(--radius-sm); padding:11px 10px; cursor:pointer; font-size:13.5px; font-weight:700;
}
.photo-action:hover{ background:var(--paper); border-color:var(--ink-300); }
.file-hidden{ position:absolute; width:1px; height:1px; opacity:0; pointer-events:none; }
@media (max-width: 420px){ .photo-actions{ grid-template-columns:1fr; } }
.btn-primary{ background:var(--brand-600); color:#fff; border:none; padding:12px 16px; border-radius:var(--radius-sm);
    cursor:pointer; font-size:14.5px; font-weight:600; width:100%; }
.btn-primary:hover{ background:var(--brand-700); }
.btn-primary:disabled, .btn-pill:disabled{ opacity:.72; cursor:wait; pointer-events:none; }
.btn-loading{ display:inline-flex; align-items:center; justify-content:center; gap:8px; }
.btn-loading::before{
    content:""; width:13px; height:13px; border:2px solid currentColor; border-right-color:transparent;
    border-radius:50%; animation:spin .75s linear infinite; flex-shrink:0;
}
@keyframes spin{ to{ transform:rotate(360deg); } }
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
        <form method="POST" enctype="multipart/form-data" id="registroForm">
            <div class="field">
                <label>Local</label>
                <input type="text" name="local" list="tipos_locales" required placeholder="Ej: Verduleria">
                <datalist id="tipos_locales">
                    {% for tipo in tipos_locales %}<option value="{{ tipo }}"></option>{% endfor %}
                </datalist>
            </div>
            <div class="field">
                <label>Calle</label>
                <div class="input-action-row">
                    <input type="text" name="calle" id="calleInput" list="calles_registradas" required placeholder="Ej: Av. Corrientes" autocomplete="off">
                    <button type="button" class="icon-action" id="btnUbicacion"
                            title="Usar mi ubicación actual" aria-label="Usar mi ubicación actual"
                            onclick="detectarCalleActual()">📍</button>
                </div>
                <div class="field-status" id="ubicacionStatus"></div>
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
                <div class="photo-actions">
                    <button type="button" class="photo-action" onclick="abrirSelectorFoto('archivo')">🖼️ Seleccionar foto</button>
                    <button type="button" class="photo-action" onclick="abrirSelectorFoto('camara')">📷 Sacar foto</button>
                </div>
                <input type="file" name="foto" id="fotoInput" class="file-hidden" accept="image/*" required onchange="mostrarPreview(event)">
                <div class="field-status" id="fotoStatus">Elegí una foto guardada o sacá una nueva.</div>
                <div class="preview-box" id="previewBox">
                    <img class="preview-thumb" id="previewImg" alt="Vista previa" onclick="abrirZoom(this.src)">
                    <div class="preview-hint">Click en la imagen para hacer zoom</div>
                </div>
            </div>
            <button type="submit" class="btn-primary" id="btnRegistro">Enviar registro</button>
        </form>
    </div>
</div>
""" + ZOOM_HTML + """
    <script>
        """ + ZOOM_JS + """
        function abrirSelectorFoto(modo) {
            const input = document.getElementById('fotoInput');
            const status = document.getElementById('fotoStatus');
            input.value = '';
            if (modo === 'camara') {
                input.setAttribute('capture', 'environment');
                status.textContent = 'Abriendo cámara...';
            } else {
                input.removeAttribute('capture');
                status.textContent = 'Seleccioná una foto del dispositivo.';
            }
            input.click();
        }

        function mostrarPreview(event) {
            const file = event.target.files[0];
            const box = document.getElementById('previewBox');
            const img = document.getElementById('previewImg');
            const status = document.getElementById('fotoStatus');
            if (!file) {
                box.style.display = 'none';
                img.src = '';
                status.textContent = 'Elegí una foto guardada o sacá una nueva.';
                return;
            }
            const reader = new FileReader();
            reader.onload = function(e) { img.src = e.target.result; box.style.display = 'block'; };
            reader.readAsDataURL(file);
            status.textContent = file.name || 'Foto lista para enviar.';
        }

        function calleDesdeDireccion(address) {
            return address.road || address.pedestrian || address.footway || address.cycleway ||
                   address.path || address.residential || '';
        }

        function detectarCalleActual() {
            const btn = document.getElementById('btnUbicacion');
            const input = document.getElementById('calleInput');
            const status = document.getElementById('ubicacionStatus');
            if (!navigator.geolocation) {
                status.textContent = 'Tu navegador no permite detectar ubicación.';
                return;
            }

            btn.disabled = true;
            btn.classList.add('btn-loading');
            status.textContent = 'Detectando ubicación...';

            navigator.geolocation.getCurrentPosition(function(pos) {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                const url = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&addressdetails=1&lat=' +
                            encodeURIComponent(lat) + '&lon=' + encodeURIComponent(lon);

                fetch(url, { headers: { 'Accept': 'application/json' } })
                    .then(resp => {
                        if (!resp.ok) throw new Error('No se pudo consultar la dirección');
                        return resp.json();
                    })
                    .then(data => {
                        const calle = calleDesdeDireccion(data.address || {});
                        if (!calle) {
                            status.textContent = 'No pude identificar el nombre de la calle.';
                            return;
                        }
                        input.value = calle;
                        status.textContent = 'Calle detectada: ' + calle;
                    })
                    .catch(() => {
                        status.textContent = 'No pude obtener el nombre de la calle.';
                    })
                    .finally(() => {
                        btn.disabled = false;
                        btn.classList.remove('btn-loading');
                    });
            }, function() {
                status.textContent = 'Permiso de ubicación denegado o no disponible.';
                btn.disabled = false;
                btn.classList.remove('btn-loading');
            }, {
                enableHighAccuracy: true,
                timeout: 12000,
                maximumAge: 60000
            });
        }
        const registroForm = document.getElementById('registroForm');
        const btnRegistro = document.getElementById('btnRegistro');
        registroForm.addEventListener('submit', function () {
            btnRegistro.disabled = true;
            btnRegistro.classList.add('btn-loading');
            btnRegistro.textContent = 'Enviando...';
        });
        window.addEventListener('pageshow', function () {
            btnRegistro.disabled = false;
            btnRegistro.classList.remove('btn-loading');
            btnRegistro.textContent = 'Enviar registro';
        });
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
                              onsubmit="return confirmarEnvioManual(this, '¿Enviar el Local N° {{ r.numero }} ahora mismo?');">
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

        function bloquearSubmit(form, texto) {
            const btn = form.querySelector('button[type="submit"]');
            if (!btn) return;
            btn.disabled = true;
            btn.classList.add('btn-loading');
            btn.textContent = texto;
        }

        function confirmarEnvioManual(form, mensaje) {
            if (!confirm(mensaje)) return false;
            bloquearSubmit(form, 'Enviando...');
            return true;
        }

        function formatearDuracion(totalSegundos) {
            const horas = Math.floor(totalSegundos / 3600);
            const mins = Math.floor((totalSegundos % 3600) / 60);
            const secs = totalSegundos % 60;
            if (horas > 0) {
                return horas + 'h' + (mins > 0 ? ' ' + mins.toString().padStart(2, '0') + 'm' : '');
            }
            return mins + 'm ' + secs.toString().padStart(2, '0') + 's';
        }

        function actualizarCountdowns() {
            document.querySelectorAll('.countdown').forEach(function(el) {
                const target = new Date(el.dataset.target);
                const diffMs = target - new Date();
                if (diffMs <= 0) { el.textContent = 'llegando...'; return; }
                el.textContent = 'faltan ' + formatearDuracion(Math.floor(diffMs / 1000));
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
                <input type="text" name="local" list="tipos_locales" required value="{{ registro.nombre }}">
                <datalist id="tipos_locales">
                    {% for tipo in tipos_locales %}<option value="{{ tipo }}"></option>{% endfor %}
                </datalist>
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
