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
    --ink-900:#17212B; --ink-700:#344352; --ink-600:#667482; --ink-300:#A8B2BC;
    --paper:#F3F5F7; --surface:#FFFFFF; --line:#DCE3E8;
    --nav-bg:#07090C; --nav-line:#202932; --nav-muted:#AAB4BF;
    --brand-600:#1F5F8B; --brand-700:#17496C; --brand-100:#E9F2F8;
    --amber-600:#A66A08; --amber-700:#805207; --amber-100:#FBF0D7; --amber-200:#E9C982;
    --green-600:#21855A; --green-700:#176443; --green-100:#E2F3E9;
    --red-600:#C0392F; --red-700:#962D26; --red-100:#FBE5E2;
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
.topbar{ display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; gap:18px; flex-wrap:wrap;
    background:var(--nav-bg); color:#fff; padding:14px 16px; border:1px solid var(--nav-line); border-radius:12px;
    box-shadow:0 8px 18px rgba(13,17,23,.12); }
.topbar h2{ color:#fff; font-size:17px; letter-spacing:0; }
.navlinks{ display:flex; gap:7px; flex-wrap:wrap; align-items:center; }
.navlinks a{ text-decoration:none; font-weight:650; font-size:12.5px; display:inline-flex; align-items:center; gap:6px;
    color:var(--brand-600); border-radius:7px; padding:8px 10px; transition:background .16s ease, color .16s ease, transform .16s ease; }
.navlinks a:hover{ background:var(--brand-100); color:var(--brand-700); transform:translateY(-1px); }
.topbar .navlinks a{ color:#fff; border:1px solid transparent; }
.topbar .navlinks a:hover{ background:#1A2530; color:#fff; border-color:#334554; }
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

/* Corporate system: restrained contrast, clear hierarchy and dense work surfaces. */
body{
    background-color:#0B0E12;
    background-image:
        linear-gradient(116deg, rgba(255,255,255,.035) 0%, rgba(255,255,255,0) 30%),
        repeating-linear-gradient(135deg, rgba(255,255,255,.026) 0, rgba(255,255,255,.026) 1px, transparent 1px, transparent 5px),
        repeating-linear-gradient(45deg, rgba(255,255,255,.014) 0, rgba(255,255,255,.014) 1px, transparent 1px, transparent 5px);
    background-attachment:fixed;
    padding:28px 22px 72px;
}
.login-head h2{ color:#F4F7FA; }
.login-head .login-sub{ color:#AAB4BF; }
.login-foot{ color:#8C98A5; }
.page,.page-wide{ width:100%; }
.page-wide{ max-width:1180px; }
.page{ max-width:640px; }
.topbar{ min-height:58px; padding:12px 14px 12px 18px; border-radius:10px; }
.topbar h2{ font-weight:700; letter-spacing:-.01em; }
.navlinks a{ font-size:12px; letter-spacing:.01em; }
.contador-wrap,.card{ border-radius:10px; box-shadow:0 1px 2px rgba(16,24,40,.04), 0 8px 24px rgba(16,24,40,.05); }
.contador-wrap{ padding:16px 18px; }
.card{ padding:24px; }
.field{ margin-bottom:20px; }
label{ color:var(--ink-900); font-size:12px; letter-spacing:.015em; text-transform:uppercase; }
input[type="text"], input[type="password"], input[type="number"], input[type="file"], input[type="time"], select{
    min-height:42px; border-color:#CBD5DE; border-radius:7px; box-shadow:inset 0 1px 1px rgba(16,24,40,.02); }
input:focus, select:focus{ border-color:var(--brand-600); box-shadow:0 0 0 3px rgba(31,95,139,.14); }
.btn-primary{ min-height:44px; border-radius:7px; box-shadow:0 4px 10px rgba(31,95,139,.16); }
.btn-primary:hover{ transform:translateY(-1px); box-shadow:0 7px 16px rgba(31,95,139,.2); }
.photo-action,.icon-action{ border-radius:7px; min-height:42px; transition:background .16s ease, border-color .16s ease, transform .16s ease; }
.photo-action:hover,.icon-action:hover{ border-color:var(--brand-600); color:var(--brand-700); transform:translateY(-1px); }
.alert{ border-radius:7px; box-shadow:0 2px 8px rgba(16,24,40,.04); }
.empty{ border-radius:10px; background:#fff; }
@media (max-width:760px){ body{ padding:16px 12px 48px; } .topbar{ align-items:flex-start; } .topbar .navlinks{ width:100%; } .topbar .navlinks a{ flex:1 1 auto; justify-content:center; } .card{ padding:18px; } }
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
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('estadisticas') }}">Estadísticas</a>
            <a href="{{ url_for('lista') }}">Lista</a>
            <a href="{{ url_for('perfil') }}">Perfil</a>
            <a href="{{ url_for('logout') }}">Cerrar sesión</a>
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
                    <button type="button" class="photo-action" onclick="abrirSelectorFoto('archivo')">Seleccionar foto</button>
                    <button type="button" class="photo-action" onclick="abrirSelectorFoto('camara')">Usar cámara</button>
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
        .table-card{ background:var(--surface); border:1px solid var(--line); border-radius:10px;
            overflow:visible; box-shadow:0 1px 2px rgba(16,24,40,.04), 0 10px 26px rgba(16,24,40,.06); }
        table{ width:100%; border-collapse:collapse; }
        th{ background:#F6F8FA; color:var(--ink-600); text-align:left; font-size:11px; font-weight:700; letter-spacing:.04em; text-transform:uppercase;
            padding:12px 14px; border-bottom:1px solid var(--line); }
        th:first-child{ border-top-left-radius:var(--radius-lg); }
        th:last-child{ border-top-right-radius:var(--radius-lg); }
        td{ padding:11px 14px; font-size:13.5px; border-bottom:1px solid var(--line); color:var(--ink-700);
            vertical-align:middle; position:relative; }
        tr:last-child td{ border-bottom:none; }
        tr:hover td{ background:#F7FAFC; }
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
        <h2>Dashboard de locales</h2>
        <div class="navlinks">
            <a href="{{ url_for('index') }}">Nuevo registro</a>
            <a href="{{ url_for('lista') }}">Lista de locales</a>
            <a href="{{ url_for('estadisticas') }}">Estadísticas</a>
            <a href="{{ url_for('perfil') }}">Perfil</a>
            <a href="{{ url_for('logout') }}">Cerrar sesión</a>
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
                            <button type="submit" class="btn-pill btn-enviar">Enviar</button>
                        </form>
                        {% else %}
                        <span class="btn-pill chip-enviado">✅ Enviado</span>
                        {% endif %}

                        <div class="conf-menu">
                            <button type="button" class="btn-pill btn-conf" id="conf-btn-{{ r.uid }}"
                                    onclick="toggleConf(event, {{ r.uid }})">Configuración</button>
                            <div class="conf-panel" id="conf-panel-{{ r.uid }}">
                                <a class="conf-item" href="{{ url_for('editar', uid=r.uid) }}">Editar datos</a>
                                <a class="conf-item" target="_blank" rel="noopener"
                                   href="https://www.google.com/maps/search/?api=1&query={{ r.direccion_url }}">Ver ubicación</a>
                                {% if r.estado == 'pendiente' %}
                                <div class="conf-divider"></div>
                                <div class="conf-label">Reprogramar envío</div>
                                <form method="POST" action="{{ url_for('ajustar_hora', uid=r.uid) }}" class="conf-time-row">
                                    <input type="time" id="hora-input-{{ r.uid }}" name="nueva_hora"
                                           value="{{ r.hora_programada[:5] }}" required>
                                    <button type="submit">Guardar hora</button>
                                </form>
                                {% endif %}
                                <div class="conf-divider"></div>
                                <form method="POST" action="{{ url_for('eliminar', uid=r.uid) }}"
                                      onsubmit="return confirm('¿Eliminar el Local N° {{ r.numero }}? Esta acción no se puede deshacer.');">
                                    <button type="submit" class="conf-item danger">Eliminar local</button>
                                </form>
                            </div>
                        </div>

                        {% if r.estado == 'pendiente' %}
                            {% if r.hora_manual %}
                            <form method="POST" action="{{ url_for('auto_hora', uid=r.uid) }}">
                                <button type="submit" class="btn-pill btn-manual" title="Volver al reparto automático">Manual</button>
                            </form>
                            {% else %}
                            <button type="button" class="btn-pill btn-auto" title="Fijar hora manual"
                                    onclick="abrirConfParaHora({{ r.uid }})">Automático</button>
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
        .dia-card{ background:var(--surface); border:1px solid var(--line); border-radius:10px;
            box-shadow:0 1px 2px rgba(16,24,40,.04), 0 8px 22px rgba(16,24,40,.05); margin-bottom:12px; overflow:hidden; }
        .dia-header{ display:flex; align-items:center; justify-content:space-between; gap:12px;
            padding:16px 18px; cursor:pointer; user-select:none; background:var(--surface);
            border:none; width:100%; font-family:inherit; text-align:left; }
        .dia-header:hover{ background:#F7FAFC; }
        .dia-titulo{ display:flex; align-items:center; gap:10px; }
        .dia-nombre{ font-size:15px; font-weight:700; color:var(--ink-900); }
        .dia-meta{ display:flex; align-items:center; gap:8px; }
        .dia-count{ background:var(--paper); color:var(--ink-600); font-size:11.5px; font-weight:700;
            padding:3px 10px; border-radius:99px; }
        .flecha{ font-size:12px; color:var(--ink-600); transition:transform .22s ease; display:inline-block; }
        .dia-card.abierto .flecha{ transform:rotate(180deg); }
        .dia-body{ display:none; border-top:1px solid var(--line); padding:6px 14px 14px; }
        .dia-card.abierto .dia-body{ display:block; }
        .local-row{ display:flex; gap:16px; align-items:flex-start; padding:16px 4px;
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
        .stats-history-card{ background:var(--surface); border:1px solid var(--line); border-radius:var(--radius-lg);
            box-shadow:var(--shadow-card); margin-bottom:18px; padding:20px; }
        .stats-history-head{ display:flex; justify-content:space-between; align-items:flex-start; gap:14px; flex-wrap:wrap; }
        .stats-history-head h3{ margin:0 0 4px; font-size:17px; }
        .stats-history-head p{ margin:0; color:var(--ink-600); font-size:12.5px; }
        .stats-save-button{ border:0; border-radius:8px; background:var(--brand-600); color:#fff; padding:10px 14px;
            cursor:pointer; font:inherit; font-size:13px; font-weight:700; transition:transform .16s ease, background .16s ease, opacity .16s ease; }
        .stats-save-button:hover{ background:var(--brand-700); transform:translateY(-2px); }
        .stats-save-button:disabled{ opacity:.62; cursor:wait; transform:none; }
        .stats-history-message{ min-height:18px; margin-top:12px; font-size:12.5px; font-weight:600; }
        .stats-history-message.success{ color:var(--green-700); }
        .stats-history-message.error{ color:var(--red-700); }
        .stats-history-message.loading{ color:var(--brand-700); }
        .stats-month-list{ display:grid; gap:10px; margin-top:16px; }
        .stats-month-card{ border:1px solid var(--line); border-radius:10px; padding:14px; background:#fff; animation:cardIn .25s ease both; }
        .stats-month-title{ display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap; }
        .stats-month-title h4{ margin:0; font-size:14px; color:var(--ink-900); }
        .stats-month-title span{ color:var(--ink-600); font-size:11.5px; }
        .stats-month-metrics{ display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:8px; margin-top:12px; }
        .stats-month-metric{ background:var(--paper); border-radius:8px; padding:9px 10px; }
        .stats-month-metric strong{ display:block; font-size:17px; color:var(--ink-900); }
        .stats-month-metric span{ color:var(--ink-600); font-size:11px; }
        .stats-month-objections{ display:flex; gap:6px; flex-wrap:wrap; margin-top:12px; }
        .stats-objection-chip{ background:var(--brand-100); color:var(--brand-700); border-radius:99px; padding:5px 9px; font-size:11.5px; font-weight:600; }
        .stats-history-empty{ color:var(--ink-600); font-size:12.5px; padding-top:16px; }
        @keyframes cardIn{ from{ opacity:0; transform:translateY(5px); } to{ opacity:1; transform:translateY(0); } }
        @media (max-width: 620px){
            .local-row{ flex-wrap:wrap; }
            .local-acciones{ width:100%; justify-content:flex-end; }
        }
    </style>
</head>
<body>
<div class="page-wide">
    <div class="topbar">
        <h2>Lista de locales</h2>
        <div class="navlinks">
            <a href="{{ url_for('index') }}">Nuevo registro</a>
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('estadisticas') }}">Estadísticas</a>
            <a href="{{ url_for('perfil') }}">Perfil</a>
            <a href="{{ url_for('logout') }}">Cerrar sesión</a>
        </div>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}{% for message in messages %}<div class="alert">{{ message }}</div>{% endfor %}{% endif %}
    {% endwith %}

    <section class="stats-history-card">
        <div class="stats-history-head">
            <div>
                <h3>Estadísticas mensuales</h3>
                <p>Guardá el período actual o consultá los resultados archivados por mes.</p>
            </div>
            <button type="button" class="stats-save-button" id="saveStatsMonth">Guardar estadísticas</button>
        </div>
        <div id="statsHistoryMessage" class="stats-history-message" role="status" aria-live="polite"></div>
        <div id="statsMonthList" class="stats-month-list"></div>
    </section>

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
                            <button type="submit" class="btn-pill btn-reenviar">Re-enviar</button>
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
        const statsStorageKey = 'gednet-estadisticas-v1-' + {{ session['usuario']|tojson }};
        const statsHistoryKey = 'gednet-estadisticas-historial-v1-' + {{ session['usuario']|tojson }};
        const emptyMonthlyStats = { yes: 0, no: 0, sales: 0, objections: [], periodMonth: '' };

        function monthKey(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            return year + '-' + month;
        }
        function monthLabel(key) {
            const parts = key.split('-');
            const date = new Date(Number(parts[0]), Number(parts[1]) - 1, 1);
            return new Intl.DateTimeFormat('es-AR', { month: 'long', year: 'numeric' }).format(date);
        }
        function readStats() {
            try {
                const saved = JSON.parse(localStorage.getItem(statsStorageKey));
                return { ...emptyMonthlyStats, ...(saved || {}), objections: Array.isArray(saved && saved.objections) ? saved.objections : [] };
            } catch (error) { return { ...emptyMonthlyStats, objections: [] }; }
        }
        function readHistory() {
            try { const saved = JSON.parse(localStorage.getItem(statsHistoryKey)); return Array.isArray(saved) ? saved : []; }
            catch (error) { return []; }
        }
        function writeStats(stats) { localStorage.setItem(statsStorageKey, JSON.stringify(stats)); }
        function writeHistory(history) { localStorage.setItem(statsHistoryKey, JSON.stringify(history)); }
        function snapshotStats(stats) { return { yes: Number(stats.yes || 0), no: Number(stats.no || 0), sales: Number(stats.sales || 0), objections: (stats.objections || []).map(item => ({ text: item.text, count: Number(item.count || 0) })) }; }
        function ensureMonthlyRollover() {
            const currentMonth = monthKey(new Date());
            const stats = readStats();
            if (!stats.periodMonth) { stats.periodMonth = currentMonth; writeStats(stats); return stats; }
            if (stats.periodMonth === currentMonth) return stats;
            const history = readHistory().filter(item => item.month !== stats.periodMonth);
            history.unshift({ month: stats.periodMonth, stats: snapshotStats(stats), savedAt: new Date().toISOString() });
            writeHistory(history);
            const reset = { ...emptyMonthlyStats, periodMonth: currentMonth };
            writeStats(reset);
            return reset;
        }
        function setHistoryMessage(text, type) { const box = document.getElementById('statsHistoryMessage'); box.textContent = text; box.className = 'stats-history-message ' + (type || ''); }
        function renderStatsHistory() {
            const list = document.getElementById('statsMonthList');
            const current = ensureMonthlyRollover();
            const history = readHistory();
            const records = [{ month: current.periodMonth || monthKey(new Date()), stats: snapshotStats(current), current: true }, ...history].filter((item, index, array) => array.findIndex(other => other.month === item.month) === index);
            if (!records.length) { list.innerHTML = '<div class="stats-history-empty">Todavía no hay estadísticas mensuales guardadas.</div>'; return; }
            list.innerHTML = records.map(record => {
                const stats = record.stats || {};
                const objections = (stats.objections || []).sort((a, b) => Number(b.count || 0) - Number(a.count || 0)).slice(0, 8);
                const chips = objections.length ? objections.map(item => '<span class="stats-objection-chip">' + String(item.text || '') + ' · ' + Number(item.count || 0) + '</span>').join('') : '<span class="stats-month-title"><span>Sin objeciones registradas</span></span>';
                return '<article class="stats-month-card"><div class="stats-month-title"><h4>Estadísticas de ' + monthLabel(record.month) + (record.current ? ' · actual' : '') + '</h4><span>Guardado localmente</span></div><div class="stats-month-metrics"><div class="stats-month-metric"><strong>' + Number(stats.yes || 0) + ' / ' + Number(stats.no || 0) + '</strong><span>SI / NO</span></div><div class="stats-month-metric"><strong>' + Number(stats.sales || 0) + '</strong><span>Ventas obtenidas</span></div><div class="stats-month-metric"><strong>' + (Number(stats.yes || 0) + Number(stats.no || 0)) + '</strong><span>Locales visitados</span></div></div><div class="stats-month-objections">' + chips + '</div></article>';
            }).join('');
        }
        document.getElementById('saveStatsMonth').addEventListener('click', function() {
            const button = this;
            button.disabled = true;
            setHistoryMessage('Guardando estadísticas del mes...', 'loading');
            try {
                const stats = ensureMonthlyRollover();
                const history = readHistory().filter(item => item.month !== stats.periodMonth);
                history.unshift({ month: stats.periodMonth || monthKey(new Date()), stats: snapshotStats(stats), savedAt: new Date().toISOString() });
                writeHistory(history);
                renderStatsHistory();
                setHistoryMessage('Estadísticas guardadas correctamente.', 'success');
            } catch (error) {
                console.error(error);
                setHistoryMessage('No se pudieron guardar las estadísticas.', 'error');
            }
            setTimeout(() => { button.disabled = false; }, 350);
        });
        try { renderStatsHistory(); } catch (error) { console.error(error); setHistoryMessage('No se pudieron cargar las estadísticas mensuales.', 'error'); }
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
        <h2>Editar local N° {{ registro.numero }}</h2>
        <div class="navlinks"><a href="{{ url_for('dashboard') }}">Volver al dashboard</a><a href="{{ url_for('estadisticas') }}">Estadísticas</a><a href="{{ url_for('perfil') }}">Perfil</a><a href="{{ url_for('logout') }}">Cerrar sesión</a></div>
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


HTML_STATS = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estadísticas</title>
    <style>""" + BASE_CSS + """
        .stats-shell{ max-width:1140px; margin:0 auto; }
        .stats-heading{ display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:18px; }
        .stats-heading h1{ font-size:24px; margin:0 0 5px; letter-spacing:-.02em; color:#F4F7FA; }
        .stats-heading p{ margin:0; color:#AAB4BF; font-size:13.5px; }
        .stats-heading .navlinks{ background:var(--nav-bg); border:1px solid var(--nav-line); border-radius:10px; padding:6px; box-shadow:0 8px 18px rgba(13,17,23,.12); }
        .stats-heading .navlinks a{ color:#fff; }
        .stats-heading .navlinks a:hover{ background:#1A2530; color:#fff; }
        .stats-form-card{ margin-bottom:18px; }
        .section-toggle{ width:100%; display:flex; justify-content:space-between; align-items:center; gap:12px;
            border:0; background:none; padding:0; cursor:pointer; color:var(--ink-900); font:inherit; text-align:left; }
        .section-toggle h2{ font-size:17px; }
        .toggle-mark{ width:30px; height:30px; border:1px solid var(--line); border-radius:8px; display:inline-flex;
            align-items:center; justify-content:center; color:var(--ink-600); font-size:16px; }
        .stats-form{ border-top:1px solid var(--line); margin-top:16px; padding-top:18px; }
        .hear-question{ font-size:15px; font-weight:700; color:var(--ink-900); margin:0 0 10px; }
        .hear-actions{ display:flex; gap:8px; flex-wrap:wrap; }
        .hear-btn{ border:1px solid var(--line); background:var(--surface); color:var(--ink-700); border-radius:8px;
            padding:10px 20px; cursor:pointer; font-size:14px; font-weight:700; min-width:90px; transition:transform .16s ease, box-shadow .16s ease, background .16s ease; }
        .hear-btn:hover{ background:var(--paper); transform:translateY(-2px); box-shadow:0 7px 14px rgba(20,25,30,.08); }
        .hear-btn:active,.counter-btn:active,.add-btn:active,.small-action:active,.score-btn:active{ transform:scale(.95); }
        .hear-btn.yes:hover, .hear-btn.yes.active{ background:var(--green-100); border-color:#b8dfc8; color:var(--green-700); }
        .hear-btn.no:hover, .hear-btn.no.active{ background:var(--red-100); border-color:#efc7c2; color:var(--red-700); }
        .stats-form-grid{ display:grid; grid-template-columns:minmax(220px,.7fr) minmax(260px,1.3fr); gap:18px; margin-top:18px; }
        .counter-control{ display:flex; align-items:center; gap:10px; }
        .counter-value{ min-width:58px; text-align:center; font-size:22px; font-weight:800; color:var(--ink-900); }
        .counter-btn{ width:36px; height:36px; border:1px solid var(--line); background:var(--surface); border-radius:8px;
            cursor:pointer; font-size:20px; line-height:1; color:var(--ink-700); transition:transform .16s ease, background .16s ease, box-shadow .16s ease; }
        .counter-btn:hover{ background:var(--paper); transform:translateY(-2px); box-shadow:0 5px 10px rgba(20,25,30,.08); }
        .objection-input{ display:flex; gap:8px; }
        .objection-input input{ flex:1; min-width:0; }
        .add-btn{ border:0; border-radius:8px; background:var(--brand-600); color:#fff; padding:0 15px; cursor:pointer; font-weight:700; transition:transform .16s ease, background .16s ease, box-shadow .16s ease; }
        .add-btn:hover{ background:var(--brand-700); transform:translateY(-2px); box-shadow:0 7px 14px rgba(11,110,153,.2); }
        .form-hint{ color:var(--ink-600); font-size:12px; margin:6px 0 0; }
        .action-message{ min-height:20px; margin-top:14px; padding:0; font-size:12.5px; font-weight:600; transition:opacity .2s ease, transform .2s ease; }
        .action-message.success{ color:var(--green-700); }
        .action-message.error{ color:var(--red-700); }
        .action-message.loading{ color:var(--brand-700); }
        .is-loading{ opacity:.62; cursor:wait !important; pointer-events:none; }
        .stats-grid{ display:grid; grid-template-columns:repeat(12, 1fr); gap:18px; }
        .stats-card{ background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:22px; box-shadow:0 1px 2px rgba(16,24,40,.04), 0 8px 22px rgba(16,24,40,.05); transition:transform .2s ease, box-shadow .2s ease; }
        .stats-card:hover{ transform:translateY(-2px); box-shadow:0 12px 26px rgba(20,25,30,.09); }
        .overview-card{ grid-column:span 4; text-align:center; }
        .wide-card{ grid-column:span 8; }
        .full-card{ grid-column:1 / -1; }
        .stats-card h2{ font-size:16px; margin-bottom:4px; }
        .stats-card-subtitle{ color:var(--ink-600); font-size:12.5px; margin:0 0 16px; }
        .donut{ width:172px; height:172px; margin:6px auto 15px; border-radius:50%; display:grid; place-items:center;
            --ratio:var(--yes, 0%); --donut-primary:var(--green-600); --donut-secondary:var(--red-600);
            background:conic-gradient(var(--donut-primary) 0 var(--ratio), var(--donut-secondary) var(--ratio) 100%); position:relative; transition:background .5s ease; }
        .donut::after{ content:""; position:absolute; inset:19px; border-radius:50%; background:var(--surface); }
        .donut-value{ position:relative; z-index:1; font-size:29px; font-weight:800; color:var(--ink-900); }
        .donut-legend{ display:flex; justify-content:center; gap:16px; color:var(--ink-700); font-size:13px; font-weight:700; }
        .legend-dot{ width:9px; height:9px; display:inline-block; border-radius:50%; margin-right:5px; }
        .legend-yes{ background:var(--green-600); } .legend-no{ background:var(--red-600); }
        .sales-card{ grid-column:span 8; }
        .sales-chart-grid{ display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:18px; }
        .sales-chart{ min-width:0; text-align:center; padding:4px 8px 0; }
        .sales-chart h3{ margin:0; font-size:13.5px; color:var(--ink-900); }
        .sales-donut{ width:142px; height:142px; margin:14px auto 12px; --ratio:0%; }
        .sales-donut::after{ inset:16px; }
        .sales-donut .donut-value{ font-size:24px; }
        .sales-chart-note{ margin:0; font-size:12px; line-height:1.45; color:var(--ink-600); }
        .chart-note{ margin:0; font-size:12px; color:var(--ink-600); }
        .section-head{ display:flex; justify-content:space-between; align-items:center; gap:14px; flex-wrap:wrap; margin-bottom:14px; }
        .sort-control{ display:flex; align-items:center; gap:8px; color:var(--ink-600); font-size:12.5px; }
        .sort-control select{ width:auto; min-width:165px; padding:8px 28px 8px 10px; font-size:12.5px; }
        .objection-grid{ display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:12px; }
        .objection-card{ border:1px solid var(--line); border-radius:10px; padding:14px; min-width:0; background:#fff; animation:cardIn .25s ease both; transition:transform .16s ease, box-shadow .16s ease; }
        .objection-card:hover{ transform:translateY(-2px); box-shadow:0 7px 16px rgba(20,25,30,.07); }
        .objection-title{ min-height:38px; color:var(--ink-900); font-size:13.5px; font-weight:700; line-height:1.35; overflow-wrap:anywhere; }
        .objection-score{ display:flex; align-items:center; gap:8px; margin:13px 0 12px; }
        .score-btn{ width:28px; height:28px; border:1px solid var(--line); border-radius:7px; background:var(--surface); cursor:pointer; font-size:17px; color:var(--ink-700); }
        .score-btn:hover{ background:var(--paper); }
        .score-number{ min-width:28px; text-align:center; font-weight:800; }
        .objection-actions{ display:flex; gap:6px; }
        .small-action{ flex:1; border:1px solid var(--line); background:var(--surface); color:var(--ink-600); border-radius:7px; padding:7px 5px; cursor:pointer; font-size:11.5px; font-weight:700; }
        .small-action:hover{ background:var(--paper); }
        .small-action.delete{ color:var(--red-600); }
        .edit-objection{ width:100%; margin-bottom:8px; }
        .empty-stats{ grid-column:1 / -1; color:var(--ink-600); font-size:13px; padding:12px 0 2px; }
        .value-pulse{ animation:valuePulse .34s ease; }
        @keyframes valuePulse{ 0%{ transform:scale(1); } 45%{ transform:scale(1.12); color:var(--brand-700); } 100%{ transform:scale(1); } }
        @keyframes cardIn{ from{ opacity:0; transform:translateY(5px); } to{ opacity:1; transform:translateY(0); } }
        @media (max-width: 900px){ .overview-card{ grid-column:span 5; } .sales-card{ grid-column:span 7; } .objection-grid{ grid-template-columns:repeat(3, minmax(0,1fr)); } }
        @media (max-width: 680px){ .stats-heading{ display:block; } .stats-heading .navlinks{ margin-top:12px; } .stats-form-grid{ grid-template-columns:1fr; } .overview-card,.sales-card{ grid-column:1 / -1; } .objection-grid{ grid-template-columns:repeat(2, minmax(0,1fr)); } }
        @media (max-width: 430px){ .sales-chart-grid{ grid-template-columns:1fr; } }
        @media (max-width: 430px){ .objection-grid{ grid-template-columns:1fr; } .objection-input{ display:grid; grid-template-columns:1fr auto; } }
    </style>
</head>
<body>
<main class="stats-shell">
    <div class="stats-heading">
        <div>
            <h1>Estadísticas</h1>
            <p>Registrá cada visita y convertí tus datos en decisiones.</p>
        </div>
        <div class="navlinks">
            <a href="{{ url_for('index') }}">Nuevo registro</a>
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('lista') }}">Lista</a>
            <a href="{{ url_for('perfil') }}">Perfil</a>
            <a href="{{ url_for('logout') }}">Cerrar sesión</a>
        </div>
    </div>

    <section class="card stats-form-card">
        <button type="button" class="section-toggle" id="formToggle" aria-expanded="true">
            <h2>Registrar visita</h2><span class="toggle-mark" id="toggleMark">⌃</span>
        </button>
        <div class="stats-form" id="statsForm">
            <p class="hear-question">¿El cliente te escuchó?</p>
            <div class="hear-actions">
                <button type="button" class="hear-btn yes stats-action" onclick="registrarRespuesta('yes')">Sí</button>
                <button type="button" class="hear-btn no stats-action" onclick="registrarRespuesta('no')">No</button>
            </div>
            <div class="stats-form-grid">
                <div>
                    <label>Ventas obtenidas</label>
                    <div class="counter-control">
                        <button type="button" class="counter-btn stats-action" onclick="cambiarVentas(-1)" aria-label="Restar venta">−</button>
                        <span class="counter-value" id="salesValue">0</span>
                        <button type="button" class="counter-btn stats-action" onclick="cambiarVentas(1)" aria-label="Sumar venta">+</button>
                    </div>
                    <p class="form-hint">Este total se usa en los dos gráficos de ventas.</p>
                </div>
                <div>
                    <label for="objectionInput">Lista de objeciones</label>
                    <div class="objection-input">
                        <input type="text" id="objectionInput" placeholder="Ej: Lo tengo que consultar" maxlength="120">
                        <button type="button" class="add-btn stats-action" onclick="agregarObjecion()">Agregar</button>
                    </div>
                    <p class="form-hint">Es opcional. Si repetís una objeción, suma un punto en la misma tarjeta.</p>
                </div>
            </div>
            <div id="actionMessage" class="action-message" role="status" aria-live="polite"></div>
        </div>
    </section>

    <section class="stats-grid">
        <article class="stats-card overview-card">
            <h2>Clientes que escucharon</h2>
            <p class="stats-card-subtitle">Porcentaje de respuestas Sí sobre el total</p>
            <div class="donut" id="heardDonut" style="--yes:0%;"><span class="donut-value" id="heardPercent">0%</span></div>
            <div class="donut-legend"><span><i class="legend-dot legend-yes"></i>SI: <b id="yesCount">0</b></span><span><i class="legend-dot legend-no"></i>NO: <b id="noCount">0</b></span></div>
        </article>
        <article class="stats-card sales-card">
            <h2>Ventas obtenidas</h2>
            <p class="stats-card-subtitle">Rendimiento según las visitas registradas</p>
            <div class="sales-chart-grid">
                <div class="sales-chart">
                    <h3>Potencial de venta</h3>
                    <div class="donut sales-donut" id="potentialDonut" style="--ratio:0%;--donut-primary:var(--brand-600);--donut-secondary:var(--brand-100);"><span class="donut-value" id="potentialValue">0%</span></div>
                    <p class="sales-chart-note" id="potentialNote">0 ventas / 0 clientes escucharon</p>
                </div>
                <div class="sales-chart">
                    <h3>Estadística en bruto de venta</h3>
                    <div class="donut sales-donut" id="rawDonut" style="--ratio:0%;--donut-primary:var(--amber-600);--donut-secondary:var(--amber-100);"><span class="donut-value" id="rawValue">0%</span></div>
                    <p class="sales-chart-note" id="rawNote">0 ventas / 0 locales visitados</p>
                </div>
            </div>
        </article>
        <article class="stats-card full-card">
            <div class="section-head"><div><h2>Lista de objeciones</h2><p class="stats-card-subtitle">Puntualas para conocer las más frecuentes.</p></div><label class="sort-control" for="sortSelect">Ordenar por <select id="sortSelect"><option value="common">Más común</option><option value="least">Menos común</option><option value="newest">Más reciente</option><option value="oldest">Más antigua</option></select></label></div>
            <div class="objection-grid" id="objectionGrid"></div>
        </article>
    </section>
</main>
<script>
const storageKey = 'gednet-estadisticas-v1-' + {{ usuario|tojson }};
const historyKey = 'gednet-estadisticas-historial-v1-' + {{ usuario|tojson }};
const defaultStats = { yes: 0, no: 0, sales: 0, objections: [], periodMonth: '' };
let stats = cargarStats();
let sortMode = 'common';
let editingId = null;

function cargarStats() {
    try {
        const saved = JSON.parse(localStorage.getItem(storageKey));
        return prepararPeriodo({ ...defaultStats, ...(saved || {}), objections: Array.isArray(saved && saved.objections) ? saved.objections : [] });
    } catch (error) { return { ...defaultStats, objections: [] }; }
}
function periodoActual() { const now = new Date(); return now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0'); }
function prepararPeriodo(current) {
    const month = periodoActual();
    if (!current.periodMonth) { current.periodMonth = month; localStorage.setItem(storageKey, JSON.stringify(current)); return current; }
    if (current.periodMonth === month) return current;
    let history = [];
    try { const savedHistory = JSON.parse(localStorage.getItem(historyKey)); history = Array.isArray(savedHistory) ? savedHistory : []; } catch (error) {}
    history = history.filter(item => item.month !== current.periodMonth);
    history.unshift({ month: current.periodMonth, stats: { yes: Number(current.yes || 0), no: Number(current.no || 0), sales: Number(current.sales || 0), objections: current.objections || [] }, savedAt: new Date().toISOString() });
    localStorage.setItem(historyKey, JSON.stringify(history));
    const reset = { ...defaultStats, periodMonth: month };
    localStorage.setItem(storageKey, JSON.stringify(reset));
    return reset;
}
let busyTimer = null;
function setMessage(text, type) { const box = document.getElementById('actionMessage'); if (!box) return; box.textContent = text; box.className = 'action-message ' + (type || ''); }
function setBusy(isBusy) {
    document.querySelectorAll('.stats-action, #objectionGrid button').forEach(button => {
        button.disabled = isBusy;
        button.classList.toggle('is-loading', isBusy);
    });
}
function guardarStats() {
    try { localStorage.setItem(storageKey, JSON.stringify(stats)); return true; }
    catch (error) { setMessage('No se pudo guardar. Revisá el almacenamiento del navegador.', 'error'); return false; }
}
function guardarCambio(cambio, mensaje) {
    setBusy(true); setMessage('Guardando cambios...', 'loading');
    try {
        cambio();
        if (!guardarStats()) throw new Error('localStorage no disponible');
        render();
        setMessage(mensaje, 'success');
    } catch (error) { console.error(error); setMessage('Ocurrió un error y el cambio no se pudo guardar.', 'error'); }
    setBusy(true);
    clearTimeout(busyTimer);
    busyTimer = setTimeout(() => setBusy(false), 260);
}
function normalizar(texto) { return String(texto || '').trim().toLocaleLowerCase(); }
function pulso(...ids) { ids.forEach(id => { const element = document.getElementById(id); if (!element) return; element.classList.remove('value-pulse'); void element.offsetWidth; element.classList.add('value-pulse'); }); }
function cambiarVentas(delta) { guardarCambio(() => { stats.sales = Math.max(0, Number(stats.sales || 0) + delta); }, 'Ventas actualizadas correctamente.'); pulso('salesValue', 'potentialValue', 'rawValue'); }
function registrarRespuesta(respuesta) { guardarCambio(() => { stats[respuesta] = Number(stats[respuesta] || 0) + 1; }, 'Respuesta registrada correctamente.'); pulso('heardPercent', 'yesCount', 'noCount', 'potentialValue', 'rawValue'); }
function agregarObjecion() {
    const input = document.getElementById('objectionInput');
    const texto = input.value.trim();
    if (!texto) { setMessage('Escribí una objeción antes de agregarla.', 'error'); input.focus(); return; }
    guardarCambio(() => {
        const existente = stats.objections.find(item => normalizar(item.text) === normalizar(texto));
        if (existente) existente.count = Number(existente.count || 0) + 1;
        else stats.objections.push({ id: Date.now().toString(36) + Math.random().toString(36).slice(2), text: texto, count: 1, createdAt: Date.now() });
        input.value = '';
    }, 'Objeción guardada correctamente.');
    input.focus();
}
function cambiarPuntos(id, delta) { const item = stats.objections.find(item => item.id === id); if (!item) return; guardarCambio(() => { item.count = Math.max(0, Number(item.count || 0) + delta); }, 'Puntaje actualizado.'); }
function borrarObjecion(id) { if (!confirm('¿Eliminar esta objeción?')) return; guardarCambio(() => { stats.objections = stats.objections.filter(item => item.id !== id); }, 'Objeción eliminada.'); }
function iniciarEdicion(id) { editingId = id; render(); const input = document.querySelector('[data-edit-id="' + id + '"]'); if (input) { input.focus(); input.select(); } }
function cancelarEdicion() { editingId = null; render(); }
function guardarEdicion(id) {
    const input = document.querySelector('[data-edit-id="' + id + '"]');
    const item = stats.objections.find(entry => entry.id === id);
    if (!input || !item || !input.value.trim()) return;
    const duplicada = stats.objections.find(entry => entry.id !== id && normalizar(entry.text) === normalizar(input.value));
    if (duplicada) { duplicada.count = Number(duplicada.count || 0) + Number(item.count || 0); stats.objections = stats.objections.filter(entry => entry.id !== id); }
    else item.text = input.value.trim();
    editingId = null; guardarCambio(() => {}, 'Objeción actualizada correctamente.');
}
function alternarFormulario() { const form = document.getElementById('statsForm'), open = form.hidden; form.hidden = !open; document.getElementById('formToggle').setAttribute('aria-expanded', String(open)); document.getElementById('toggleMark').textContent = open ? '⌃' : '⌄'; }
function ordenar(items) {
    return [...items].sort((a, b) => {
        if (sortMode === 'least') return Number(a.count) - Number(b.count) || b.createdAt - a.createdAt;
        if (sortMode === 'newest') return b.createdAt - a.createdAt;
        if (sortMode === 'oldest') return a.createdAt - b.createdAt;
        return Number(b.count) - Number(a.count) || b.createdAt - a.createdAt;
    });
}
function renderObjections() {
    const grid = document.getElementById('objectionGrid');
    const items = ordenar(stats.objections);
    grid.innerHTML = '';
    if (!items.length) {
        grid.innerHTML = '<div class="empty-stats">Todavía no hay objeciones guardadas.</div>';
        return;
    }
    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'objection-card';

        if (editingId === item.id) {
            const input = document.createElement('input');
            input.className = 'edit-objection';
            input.value = item.text;
            input.maxLength = 120;
            input.dataset.editId = item.id;

            const actions = document.createElement('div');
            actions.className = 'objection-actions';

            const saveBtn = document.createElement('button');
            saveBtn.className = 'small-action';
            saveBtn.textContent = 'Guardar';
            saveBtn.addEventListener('click', () => guardarEdicion(item.id));

            const cancelBtn = document.createElement('button');
            cancelBtn.className = 'small-action';
            cancelBtn.textContent = 'Cancelar';
            cancelBtn.addEventListener('click', cancelarEdicion);

            actions.append(saveBtn, cancelBtn);
            card.append(input, actions);
        } else {
            const title = document.createElement('div');
            title.className = 'objection-title';
            title.textContent = item.text;

            const score = document.createElement('div');
            score.className = 'objection-score';

            const minusBtn = document.createElement('button');
            minusBtn.className = 'score-btn';
            minusBtn.textContent = '−';
            minusBtn.setAttribute('aria-label', 'Restar punto');
            minusBtn.addEventListener('click', () => cambiarPuntos(item.id, -1));

            const scoreNum = document.createElement('span');
            scoreNum.className = 'score-number';
            scoreNum.textContent = Number(item.count || 0);

            const plusBtn = document.createElement('button');
            plusBtn.className = 'score-btn';
            plusBtn.textContent = '+';
            plusBtn.setAttribute('aria-label', 'Sumar punto');
            plusBtn.addEventListener('click', () => cambiarPuntos(item.id, 1));

            score.append(minusBtn, scoreNum, plusBtn);

            const actions = document.createElement('div');
            actions.className = 'objection-actions';

            const editBtn = document.createElement('button');
            editBtn.className = 'small-action';
            editBtn.textContent = 'Editar';
            editBtn.addEventListener('click', () => iniciarEdicion(item.id));

            const delBtn = document.createElement('button');
            delBtn.className = 'small-action delete';
            delBtn.textContent = 'Eliminar';
            delBtn.addEventListener('click', () => borrarObjecion(item.id));

            actions.append(editBtn, delBtn);
            card.append(title, score, actions);
        }
        grid.appendChild(card);
    });
}
function escapar(texto) { return String(texto).replace(/[&<>'"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char])); }
function render() {
    const yes = Number(stats.yes || 0), no = Number(stats.no || 0), total = yes + no, sales = Number(stats.sales || 0);
    const yesPct = total ? Math.round((yes / total) * 100) : 0;
    const potential = yes ? (sales / yes) * 100 : 0, raw = total ? (sales / total) * 100 : 0;
    document.getElementById('salesValue').textContent = sales;
    document.getElementById('yesCount').textContent = yes; document.getElementById('noCount').textContent = no;
    document.getElementById('heardPercent').textContent = yesPct + '%';
    const donut = document.getElementById('heardDonut'); donut.style.setProperty('--yes', yesPct + '%'); donut.style.background = total ? '' : 'conic-gradient(#d9dfdd 0 100%)';
    document.getElementById('potentialValue').textContent = Math.round(potential) + '%'; document.getElementById('rawValue').textContent = Math.round(raw) + '%';
    document.getElementById('potentialDonut').style.setProperty('--ratio', Math.min(100, potential) + '%'); document.getElementById('rawDonut').style.setProperty('--ratio', Math.min(100, raw) + '%');
    document.getElementById('potentialNote').textContent = sales + ' ventas / ' + yes + ' clientes escucharon'; document.getElementById('rawNote').textContent = sales + ' ventas / ' + total + ' locales visitados';
    renderObjections();
}
document.getElementById('sortSelect').addEventListener('change', event => { sortMode = event.target.value; renderObjections(); });
document.getElementById('objectionInput').addEventListener('keydown', event => { if (event.key === 'Enter') agregarObjecion(); });
window.cambiarVentas = cambiarVentas;
window.registrarRespuesta = registrarRespuesta;
window.agregarObjecion = agregarObjecion;
window.cambiarPuntos = cambiarPuntos;
window.borrarObjecion = borrarObjecion;
window.iniciarEdicion = iniciarEdicion;
window.cancelarEdicion = cancelarEdicion;
window.guardarEdicion = guardarEdicion;
document.getElementById('formToggle').addEventListener('click', alternarFormulario);
window.addEventListener('error', event => { console.error(event.error || event.message); setMessage('La herramienta encontró un error. Recargá la página e intentá nuevamente.', 'error'); setBusy(false); });
try { render(); } catch (error) { console.error(error); setMessage('No se pudieron cargar las estadísticas guardadas.', 'error'); }
</script>
</body>
</html>
"""


HTML_PROFILE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perfil</title>
    <style>""" + BASE_CSS + """
        .profile-shell{ max-width:1180px; margin:0 auto; }
        .profile-layout{ display:grid; grid-template-columns:minmax(280px, .8fr) minmax(0, 1.7fr); gap:18px; align-items:start; }
        .profile-card,.profile-panel{ background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:24px;
            box-shadow:0 1px 2px rgba(16,24,40,.04), 0 10px 26px rgba(16,24,40,.06); }
        .profile-card{ text-align:center; }
        .profile-avatar{ width:116px; height:116px; margin:4px auto 18px; border-radius:50%; display:grid; place-items:center;
            background:var(--nav-bg); color:#fff; font-size:36px; font-weight:750; overflow:hidden; border:4px solid #E9F2F8; }
        .profile-avatar img{ width:100%; height:100%; object-fit:cover; display:none; }
        .profile-card h1{ margin:0; color:var(--ink-900); font-size:23px; letter-spacing:-.02em; }
        .profile-email{ margin:6px 0 20px; color:var(--ink-600); font-size:13px; overflow-wrap:anywhere; }
        .profile-upload{ display:inline-flex; align-items:center; justify-content:center; min-height:40px; padding:0 14px;
            border:1px solid var(--line); border-radius:7px; color:var(--brand-700); background:var(--surface); cursor:pointer;
            font-size:12.5px; font-weight:700; transition:background .16s ease, border-color .16s ease, transform .16s ease; }
        .profile-upload:hover{ background:var(--brand-100); border-color:var(--brand-600); transform:translateY(-1px); }
        .profile-upload input{ display:none; }
        .profile-status{ min-height:18px; margin-top:10px; color:var(--green-700); font-size:12px; font-weight:600; }
        .profile-panel h2{ margin:0 0 4px; font-size:17px; }
        .profile-panel-subtitle{ color:var(--ink-600); margin:0 0 18px; font-size:13px; }
        .profile-metrics{ display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:10px; }
        .profile-metric{ background:#F6F8FA; border:1px solid #E5EBF0; border-radius:8px; padding:14px; }
        .profile-metric strong{ display:block; color:var(--ink-900); font-size:24px; line-height:1; }
        .profile-metric span{ display:block; margin-top:7px; color:var(--ink-600); font-size:11.5px; }
        .profile-section{ margin-top:20px; padding-top:20px; border-top:1px solid var(--line); }
        .profile-section h3{ margin:0 0 12px; font-size:14px; }
        .profile-objections{ display:grid; gap:8px; }
        .profile-objection{ display:flex; justify-content:space-between; align-items:center; gap:12px; padding:10px 12px;
            border:1px solid var(--line); border-radius:7px; color:var(--ink-700); font-size:13px; }
        .profile-objection strong{ color:var(--brand-700); font-size:12px; }
        .profile-empty{ color:var(--ink-600); font-size:12.5px; }
        @media (max-width:760px){ .profile-layout{ grid-template-columns:1fr; } .profile-metrics{ grid-template-columns:repeat(3, minmax(0,1fr)); } }
        @media (max-width:430px){ .profile-metrics{ grid-template-columns:1fr; } .profile-metric{ display:flex; justify-content:space-between; align-items:center; } .profile-metric span{ margin-top:0; } }
    </style>
</head>
<body>
<main class="profile-shell">
    <div class="topbar">
        <h2>Perfil</h2>
        <div class="navlinks">
            <a href="{{ url_for('index') }}">Nuevo registro</a>
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('estadisticas') }}">Estadísticas</a>
            <a href="{{ url_for('lista') }}">Lista</a>
            <a href="{{ url_for('logout') }}">Cerrar sesión</a>
        </div>
    </div>

    <div class="profile-layout">
        <section class="profile-card">
            <div class="profile-avatar" id="profileAvatar"><span id="profileInitials"></span><img id="profilePhoto" alt="Foto de perfil"></div>
            <h1>{{ usuario }}</h1>
            <p class="profile-email">{{ email }}</p>
            <label class="profile-upload">Cambiar foto<input type="file" id="profilePhotoInput" accept="image/*"></label>
            <div class="profile-status" id="profileStatus" role="status" aria-live="polite"></div>
        </section>

        <section class="profile-panel">
            <h2>Resumen de actividad</h2>
            <p class="profile-panel-subtitle">Tus principales indicadores del período actual.</p>
            <div class="profile-metrics">
                <div class="profile-metric"><strong id="profileProspects">{{ total_prospectos }}</strong><span>Total de prospectos</span></div>
                <div class="profile-metric"><strong id="profileHeard">0</strong><span>Clientes escucharon</span></div>
                <div class="profile-metric"><strong id="profileSales">0</strong><span>Ventas obtenidas</span></div>
            </div>
            <div class="profile-section">
                <h3>Objeciones frecuentes</h3>
                <div class="profile-objections" id="profileObjections"></div>
            </div>
        </section>
    </div>
</main>
<script>
const profileStorageKey = 'gednet-perfil-v1-' + {{ usuario|tojson }};
const profileStatsKey = 'gednet-estadisticas-v1-' + {{ usuario|tojson }};
const profileInitials = {{ usuario|tojson }}.split(/\s+/).map(part => part[0]).join('').slice(0, 2).toUpperCase();
document.getElementById('profileInitials').textContent = profileInitials;

function loadProfilePhoto() {
    const saved = localStorage.getItem(profileStorageKey);
    if (!saved) return;
    const image = document.getElementById('profilePhoto');
    image.src = saved;
    image.style.display = 'block';
    document.getElementById('profileInitials').style.display = 'none';
}
function renderProfileStats() {
    let stats = {};
    try { stats = JSON.parse(localStorage.getItem(profileStatsKey)) || {}; } catch (error) {}
    document.getElementById('profileHeard').textContent = Number(stats.yes || 0) + Number(stats.no || 0);
    document.getElementById('profileSales').textContent = Number(stats.sales || 0);
    const list = document.getElementById('profileObjections');
    const objections = Array.isArray(stats.objections) ? [...stats.objections].sort((a, b) => Number(b.count || 0) - Number(a.count || 0)).slice(0, 6) : [];
    list.innerHTML = '';
    if (!objections.length) { list.innerHTML = '<div class="profile-empty">Todavía no hay objeciones registradas.</div>'; return; }
    objections.forEach(item => {
        const row = document.createElement('div'); row.className = 'profile-objection';
        const text = document.createElement('span'); text.textContent = item.text || 'Sin descripción';
        const count = document.createElement('strong'); count.textContent = Number(item.count || 0) + ' casos';
        row.append(text, count); list.appendChild(row);
    });
}
document.getElementById('profilePhotoInput').addEventListener('change', event => {
    const file = event.target.files[0];
    const status = document.getElementById('profileStatus');
    if (!file) return;
    if (!file.type.startsWith('image/')) { status.textContent = 'Elegí un archivo de imagen válido.'; status.style.color = 'var(--red-700)'; return; }
    const reader = new FileReader();
    reader.onload = () => {
        try {
            localStorage.setItem(profileStorageKey, reader.result);
            const image = document.getElementById('profilePhoto'); image.src = reader.result; image.style.display = 'block';
            document.getElementById('profileInitials').style.display = 'none';
            status.textContent = 'Foto guardada en este dispositivo.'; status.style.color = 'var(--green-700)';
        } catch (error) { status.textContent = 'No se pudo guardar la foto.'; status.style.color = 'var(--red-700)'; }
    };
    reader.readAsDataURL(file);
});
loadProfilePhoto();
renderProfileStats();
</script>
</body>
</html>
"""
