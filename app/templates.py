HTML_LOGIN = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar sesión</title>
    <style>
        :root{
            --bg:#08090B;
            --grid-line:rgba(255,255,255,.05);
            --panel:rgba(20,22,26,.62);
            --panel-border:rgba(255,255,255,.09);
            --ink-900:#F5F6F7;
            --ink-600:#9AA3AD;
            --ink-400:#6B747E;
            --accent:#39FF9E;
            --accent-dim:rgba(57,255,158,.14);
            --danger:#FF5C5C;
            --danger-bg:rgba(255,92,92,.12);
            --radius:14px;
        }
        *{ box-sizing:border-box; }
        html,body{ height:100%; }
        body{
            margin:0;
            font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, Helvetica, Arial, sans-serif;
            background:
                radial-gradient(1100px 550px at 15% -10%, rgba(57,255,158,.10), transparent 55%),
                radial-gradient(900px 500px at 100% 110%, rgba(60,120,255,.10), transparent 55%),
                var(--bg);
            color:var(--ink-900);
            -webkit-font-smoothing:antialiased;
            position:relative;
            overflow-x:hidden;
        }
        body::before{
            content:"";
            position:fixed; inset:0;
            background-image:
                linear-gradient(var(--grid-line) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
            background-size:42px 42px;
            mask-image:radial-gradient(circle at 50% 30%, black 0%, transparent 72%);
            pointer-events:none;
        }
        .login-body{
            min-height:100vh; display:flex; align-items:center; justify-content:center;
            padding:24px 16px; position:relative; z-index:1;
        }
        .login-box{ width:100%; max-width:400px; }

        .login-head{ text-align:center; margin-bottom:28px; }
        .login-logo{
            width:52px; height:52px; margin:0 auto 20px; border-radius:13px;
            background:linear-gradient(155deg, rgba(57,255,158,.16), rgba(57,255,158,.02));
            border:1px solid rgba(57,255,158,.28);
            display:flex; align-items:center; justify-content:center; font-size:22px;
            box-shadow:0 0 0 1px rgba(255,255,255,.02), 0 12px 28px rgba(57,255,158,.08);
        }
        .login-head h2{
            font-size:24px; font-weight:700; letter-spacing:-0.03em; margin:0; color:var(--ink-900);
        }
        .login-sub{ font-size:13.5px; color:var(--ink-600); margin-top:8px; letter-spacing:-.01em; }

        .login-card{
            background:var(--panel);
            border:1px solid var(--panel-border);
            border-radius:var(--radius);
            padding:28px 24px;
            backdrop-filter:blur(18px);
            -webkit-backdrop-filter:blur(18px);
            box-shadow:0 1px 0 rgba(255,255,255,.04) inset, 0 20px 50px rgba(0,0,0,.45);
        }

        .alert-error{
            background:var(--danger-bg); color:var(--danger); border:1px solid rgba(255,92,92,.28);
            padding:11px 14px; margin-bottom:18px; border-radius:9px;
            font-size:13px; font-weight:600;
        }

        .field{ margin-bottom:16px; }
        label{
            display:block; margin-bottom:7px; font-weight:600; font-size:12px;
            color:var(--ink-600); letter-spacing:.03em; text-transform:uppercase;
        }
        input[type="text"], input[type="password"]{
            width:100%; padding:12px 14px; border:1px solid rgba(255,255,255,.10);
            border-radius:9px; font-size:14.5px; background:rgba(255,255,255,.03); color:var(--ink-900);
            font-family:inherit; transition:border-color .15s ease, background .15s ease, box-shadow .15s ease;
        }
        input::placeholder{ color:var(--ink-400); }
        input:focus{
            outline:none; border-color:var(--accent); background:rgba(255,255,255,.045);
            box-shadow:0 0 0 3px var(--accent-dim);
        }

        .input-wrap{ position:relative; }
        .input-wrap input{ padding-right:44px; }
        .toggle-pass{
            position:absolute; right:5px; top:50%; transform:translateY(-50%);
            width:34px; height:34px; border:none; background:none; cursor:pointer;
            border-radius:7px; font-size:15px; color:var(--ink-600);
            display:flex; align-items:center; justify-content:center;
            transition:background .15s ease, color .15s ease;
        }
        .toggle-pass:hover{ background:rgba(255,255,255,.06); color:var(--ink-900); }

        .btn-primary{
            width:100%; margin-top:6px; padding:13px 16px; border:none; border-radius:9px;
            background:var(--accent); color:#06110B; font-size:14.5px; font-weight:700;
            cursor:pointer; letter-spacing:-.01em;
            transition:transform .12s ease, box-shadow .12s ease, filter .12s ease;
            box-shadow:0 10px 24px rgba(57,255,158,.18);
        }
        .btn-primary:hover{ filter:brightness(1.06); transform:translateY(-1px); box-shadow:0 14px 30px rgba(57,255,158,.24); }
        .btn-primary:active{ transform:translateY(0); }
        .btn-primary:disabled{ opacity:.65; cursor:wait; transform:none; }

        .login-foot{ text-align:center; font-size:11.5px; color:var(--ink-400); margin-top:22px; letter-spacing:.02em; }
    </style>
</head>
<body class="login-body">
<div class="login-box">
    <div class="login-head">
        <div class="login-logo">📍</div>
        <h2>Iniciar sesión</h2>
        <div class="login-sub">Ingresá para registrar y enviar tus locales</div>
    </div>

    <div class="login-card">
        {% with messages = get_flashed_messages() %}
          {% if messages %}{% for message in messages %}<div class="alert-error">{{ message }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <form method="POST" id="loginForm">
            <div class="field">
                <label for="identificador">Usuario o email</label>
                <input type="text" id="identificador" name="identificador" required autofocus
                       autocomplete="username" placeholder="tuusuario">
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

    const form = document.getElementById('loginForm');
    const btn = document.getElementById('btnEntrar');
    form.addEventListener('submit', function () {
        btn.disabled = true;
        btn.textContent = 'Entrando...';
    });
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


HTML_STATS_REDESIGNED = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estadísticas</title>
    <style>""" + BASE_CSS + """
        .stats-v2-shell{ max-width:1240px; margin:0 auto; }
        .stats-workspace{ display:grid; grid-template-columns:270px minmax(0,1fr); gap:16px; align-items:start; }
        .stats-sidebar,.stats-panel{ background:#202832; border:1px solid #303B46; border-radius:10px; box-shadow:0 12px 30px rgba(0,0,0,.18); }
        .stats-sidebar{ overflow:visible; }
        .stats-profile{ padding:20px 18px; border-bottom:1px solid #303B46; border-radius:10px 10px 0 0; }
        .stats-profile h1{ color:#F4F7FA; font-size:22px; margin:0 0 4px; letter-spacing:-.02em; }
        .stats-profile p{ color:#93A2B0; font-size:12px; margin:0; }
        .stats-profile-line{ height:3px; width:54px; background:#2DDB8A; margin:14px 0 0; }
        .seller-badges{ display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 14px; }
        .seller-badge{ position:relative; display:inline-flex; align-items:center; min-height:22px; padding:0 9px; border:1px solid transparent; border-radius:3px; font-size:10px; font-weight:800; letter-spacing:0; cursor:help; }
        .seller-badge::after{ content:attr(data-tooltip); position:absolute; z-index:20; left:0; top:calc(100% + 8px); width:220px; padding:10px 11px; border-radius:6px; background:#11171D; color:#EFF4F7; box-shadow:0 12px 24px rgba(0,0,0,.28); font-size:11px; font-weight:500; line-height:1.4; letter-spacing:0; text-transform:none; opacity:0; pointer-events:none; transform:translateY(-3px); transition:opacity .16s ease, transform .16s ease; }
        .seller-badge:hover::after{ opacity:1; transform:translateY(0); }
        .seller-badge.yellow{ color:#FFD978; background:rgba(240,184,75,.16); border-color:rgba(240,184,75,.55); }
        .seller-badge.red{ color:#FF9B94; background:rgba(224,91,82,.16); border-color:rgba(224,91,82,.55); }
        .seller-badge.green{ color:#76F0B5; background:rgba(45,219,138,.14); border-color:rgba(45,219,138,.52); }
        .rank-stack{ display:grid; }
        .rank-card{ padding:18px; border-bottom:1px solid #303B46; }
        .rank-card:last-child{ border-bottom:0; }
        .rank-label{ color:#93A2B0; font-size:11px; text-transform:uppercase; letter-spacing:.08em; }
        .rank-value{ display:flex; justify-content:space-between; align-items:baseline; gap:8px; margin-top:8px; }
        .rank-value strong{ color:#F4F7FA; font-size:20px; }
        .rank-value span{ color:#D1D9E0; font-size:13px; font-weight:700; }
        .rank-meter{ height:5px; background:#11171D; border-radius:99px; overflow:hidden; margin-top:12px; }
        .rank-meter i{ display:block; height:100%; width:0; border-radius:99px; background:#2DDB8A; transition:width .45s ease; }
        .rank-card:nth-child(2) .rank-meter i{ background:#F0B84B; }
        .rank-card:nth-child(3) .rank-meter i{ background:#7CA7FF; }
        .lp-sidebar{ border-top:1px solid #303B46; padding:18px; border-radius:0 0 10px 10px; }
        .lp-sidebar h3{ color:#F4F7FA; font-size:12px; text-transform:uppercase; letter-spacing:.08em; margin:0 0 3px; }
        .lp-sidebar p{ color:#93A2B0; font-size:11px; margin:0 0 12px; }
        .lp-mini{ width:100%; height:90px; display:block; background:#171D24; border:1px solid #303B46; border-radius:7px; }
        .stats-main{ display:grid; gap:16px; min-width:0; }
        .stats-panel{ padding:20px; }
        .stats-panel.light{ background:var(--surface); border-color:var(--line); }
        .panel-header{ display:flex; justify-content:space-between; align-items:flex-start; gap:14px; margin-bottom:16px; }
        .panel-header h2{ color:#F4F7FA; font-size:15px; text-transform:uppercase; letter-spacing:.05em; }
        .light .panel-header h2{ color:var(--ink-900); }
        .panel-header p{ color:#93A2B0; font-size:12px; margin:5px 0 0; }
        .light .panel-header p{ color:var(--ink-600); }
        .gpi-overview{ display:grid; grid-template-columns:minmax(250px,.8fr) minmax(0,1.5fr); gap:20px; min-width:0; }
        .gpi-overview > *{ min-width:0; }
        .radar-wrap{ width:100%; min-height:290px; display:grid; place-items:center; overflow:hidden; background:#171D24; border:1px solid #303B46; border-radius:8px; }
        .radar{ display:block; width:min(100%,300px); max-width:300px; height:auto; margin:0 auto; }
        .radar-grid{ fill:none; stroke:#35424F; stroke-width:1; }
        .radar-axis{ stroke:#35424F; stroke-width:1; }
        .radar-shape{ fill:rgba(45,219,138,.2); stroke:#F0B84B; stroke-width:2; transition:all .4s ease; }
        .radar-label{ fill:#AAB7C3; font-size:10px; font-weight:600; }
        .daily-table{ width:100%; border-collapse:collapse; }
        .daily-table th{ background:transparent; color:#8293A3; border-bottom:1px solid #303B46; padding:8px 10px; font-size:10px; letter-spacing:.06em; text-transform:uppercase; text-align:left; }
        .daily-table td{ color:#E7EDF2; border-bottom:1px solid #2A353F; padding:12px 10px; font-size:12.5px; }
        .daily-table tr:last-child td{ border-bottom:0; }
        .daily-table .day-name{ color:#fff; font-weight:700; }
        .daily-table .number{ color:#2DDB8A; font-weight:800; }
        .daily-empty{ color:#93A2B0; font-size:12.5px; padding:20px 10px; }
        .performance-grid{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; }
        .performance-card{ background:#F6F8FA; border:1px solid #E3E9EE; border-radius:8px; padding:15px 12px; }
        .performance-card strong{ display:block; color:var(--ink-900); font-size:23px; line-height:1; }
        .performance-card span{ display:block; color:var(--ink-600); font-size:11px; margin-top:8px; line-height:1.3; }
        .lp-panel{ background:#202832; }
        .lp-chart-wrap{ background:#171D24; border:1px solid #303B46; border-radius:8px; padding:10px; }
        .lp-chart{ width:100%; height:230px; display:block; }
        .lp-grid-line{ stroke:#35424F; stroke-width:1; stroke-dasharray:3 4; }
        .lp-axis-label{ fill:#8293A3; font-size:10px; }
        .lp-line{ fill:none; stroke:#2DDB8A; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }
        .lp-point{ fill:#F0B84B; stroke:#171D24; stroke-width:2; }
        .search-panel{ position:relative; }
        .search-input{ width:100%; min-height:44px; padding:0 14px; border:1px solid #CBD5DE; border-radius:7px; font:inherit; color:var(--ink-900); }
        .search-input:focus{ outline:0; border-color:var(--brand-600); box-shadow:0 0 0 3px rgba(31,95,139,.14); }
        .suggestions{ position:absolute; z-index:20; left:0; right:0; top:72px; background:#fff; border:1px solid var(--line); border-radius:8px; box-shadow:0 15px 30px rgba(16,24,40,.16); overflow:hidden; display:none; }
        .suggestions.open{ display:block; }
        .suggestion{ display:block; width:100%; border:0; border-bottom:1px solid #EEF1F4; background:#fff; padding:11px 13px; text-align:left; cursor:pointer; }
        .suggestion:last-child{ border-bottom:0; }
        .suggestion:hover{ background:var(--brand-100); }
        .suggestion strong{ display:block; color:var(--ink-900); font-size:13px; }
        .suggestion small{ display:block; color:var(--ink-600); font-size:11px; margin-top:3px; }
        .stats-entry{ display:grid; grid-template-columns:1.3fr .6fr; gap:16px; align-items:end; }
        .heard-actions{ display:flex; gap:8px; }
        .heard-actions button{ flex:1; min-height:42px; border:1px solid var(--line); border-radius:7px; background:var(--surface); color:var(--ink-700); font-weight:750; cursor:pointer; transition:all .16s ease; }
        .heard-actions button:hover{ transform:translateY(-1px); }
        .heard-actions .yes:hover{ border-color:var(--green-600); color:var(--green-700); background:var(--green-100); }
        .heard-actions .no:hover{ border-color:var(--red-600); color:var(--red-700); background:var(--red-100); }
        .sales-stepper{ display:flex; align-items:center; justify-content:space-between; gap:9px; }
        .sales-stepper button{ width:35px; height:35px; border:1px solid var(--line); border-radius:7px; background:#fff; cursor:pointer; font-size:18px; color:var(--ink-700); }
        .sales-stepper strong{ font-size:22px; color:var(--ink-900); }
        .entry-status{ min-height:18px; margin-top:12px; font-size:12px; font-weight:650; }
        .entry-status.success{ color:var(--green-700); }.entry-status.error{ color:var(--red-700); }.entry-status.loading{ color:var(--brand-700); }
        .objection-tags{ display:flex; flex-wrap:wrap; gap:8px; }
        .objection-tag{ position:relative; display:inline-flex; align-items:center; gap:7px; padding:8px 10px; border:1px solid #D7E0E7; border-radius:7px; background:#F8FAFB; color:var(--ink-700); font-size:12px; cursor:help; }
        .objection-tag .tag-count{ color:var(--ink-600); font-weight:800; }
        .objection-tag.tag-warning{ border-color:#E4BD58; background:#FFF8E9; color:#765008; }.objection-tag.tag-danger{ border-color:#E6A19C; background:#FFF0EE; color:#8D2C25; }
        .objection-tooltip{ position:absolute; z-index:15; bottom:calc(100% + 8px); left:0; width:240px; padding:11px 12px; border-radius:7px; background:#11171D; color:#EFF4F7; box-shadow:0 12px 24px rgba(0,0,0,.18); opacity:0; pointer-events:none; transform:translateY(4px); transition:all .16s ease; }
        .objection-tag:hover .objection-tooltip{ opacity:1; transform:translateY(0); }
        .objection-tooltip strong{ display:block; color:#F0B84B; font-size:11px; margin-bottom:5px; }.objection-tooltip span{ display:block; font-size:11px; line-height:1.4; }
        @media(max-width:980px){ .stats-workspace{ grid-template-columns:1fr; }.stats-sidebar{ display:grid; grid-template-columns:1.1fr 1fr 1fr; }.stats-profile{ border-bottom:0; border-right:1px solid #303B46; }.rank-stack{ grid-column:2 / -1; grid-template-columns:repeat(3,1fr); }.rank-card{ border-bottom:0; border-right:1px solid #303B46; }.rank-card:last-child{ border-right:0; }.lp-sidebar{ grid-column:1 / -1; border-top:1px solid #303B46; } }
        @media(max-width:760px){ .gpi-overview{ grid-template-columns:minmax(0,1fr); gap:14px; }.radar-wrap{ min-height:270px; }.radar{ width:min(100%,300px); } }
        @media(max-width:700px){ body{ padding:16px 10px 50px; }.stats-sidebar{ display:block; }.stats-profile{ border-right:0; border-bottom:1px solid #303B46; }.rank-stack{ display:grid; grid-template-columns:1fr; }.rank-card{ border-right:0; border-bottom:1px solid #303B46; }.gpi-overview,.stats-entry{ grid-template-columns:1fr; }.performance-grid{ grid-template-columns:repeat(2,1fr); }.daily-table{ min-width:620px; }.stats-panel{ overflow:hidden; } }
    </style>
</head>
<body>
<main class="stats-v2-shell">
    <div class="topbar">
        <h2>Estadísticas</h2>
        <div class="navlinks">
            <a href="{{ url_for('index') }}">Nuevo registro</a><a href="{{ url_for('dashboard') }}">Dashboard</a><a href="{{ url_for('lista') }}">Lista</a><a href="{{ url_for('perfil') }}">Perfil</a><a href="{{ url_for('logout') }}">Cerrar sesión</a>
        </div>
    </div>
    <div class="stats-workspace">
        <aside class="stats-sidebar">
            <section class="stats-profile"><h1>{{ usuario }}</h1><div class="seller-badges" id="sellerBadges" aria-live="polite"></div><p>Panel de rendimiento comercial</p><div class="stats-profile-line"></div></section>
            <div class="rank-stack">
                <div class="rank-card"><div class="rank-label">Clientes que te escucharon</div><div class="rank-value"><strong id="soloValue">0%</strong><span>Atención</span></div><div class="rank-meter"><i id="soloMeter"></i></div></div>
                <div class="rank-card"><div class="rank-label">Porcentaje de ventas</div><div class="rank-value"><strong id="flexValue">0%</strong><span>Venta bruta</span></div><div class="rank-meter"><i id="flexMeter"></i></div></div>
                <div class="rank-card"><div class="rank-label">Probabilidad de venta actual</div><div class="rank-value"><strong id="draftValue">0%</strong><span>Próxima venta</span></div><div class="rank-meter"><i id="draftMeter"></i></div></div>
            </div>
            <section class="lp-sidebar"><h3>Gráfico de ventas</h3><p id="lpSidebarMeta">Mes actual</p><svg class="lp-mini" id="lpMiniChart" viewBox="0 0 240 90" role="img" aria-label="Progreso mensual"></svg></section>
        </aside>
        <div class="stats-main">
            <section class="stats-panel">
                <div class="panel-header"><div><h2>GPI</h2><p>Índice de rendimiento general del período actual</p></div><span class="badge badge-enviado">En seguimiento</span></div>
                <div class="gpi-overview">
                    <div class="radar-wrap"><svg class="radar" viewBox="0 0 300 300" role="img" aria-label="Gráfico GPI"><polygon class="radar-grid" points="150,35 259,114 217,246 83,246 41,114"></polygon><polygon class="radar-grid" points="150,68 232,127 201,221 99,221 68,127"></polygon><polygon class="radar-grid" points="150,101 204,140 185,196 115,196 96,140"></polygon><line class="radar-axis" x1="150" y1="35" x2="150" y2="150"></line><line class="radar-axis" x1="259" y1="114" x2="150" y2="150"></line><line class="radar-axis" x1="217" y1="246" x2="150" y2="150"></line><line class="radar-axis" x1="83" y1="246" x2="150" y2="150"></line><line class="radar-axis" x1="41" y1="114" x2="150" y2="150"></line><polygon id="gpiShape" class="radar-shape" points="150,150 150,150 150,150 150,150 150,150"></polygon><text class="radar-label" x="150" y="19" text-anchor="middle">Constancia</text><text class="radar-label" x="276" y="111">Ventas</text><text class="radar-label" x="224" y="268">Atención</text><text class="radar-label" x="51" y="268" text-anchor="end">Objeciones</text><text class="radar-label" x="24" y="111" text-anchor="end">Venta %</text></svg></div>
                    <div><div class="panel-header"><div><h2>Registro de estadísticas</h2><p>Rendimiento diario del mes</p></div></div><div style="overflow:auto"><table class="daily-table"><thead><tr><th>Día</th><th>Locales</th><th>Venta bruta</th><th>Atención</th><th>Ventas</th></tr></thead><tbody id="dailyRows"></tbody></table></div></div>
                </div>
            </section>
            <section class="stats-panel light"><div class="panel-header"><div><h2>Estadísticas del vendedor</h2><p>Resumen operativo del período y del día actual</p></div></div><div class="performance-grid"><div class="performance-card"><strong id="monthVisitors">0</strong><span>Locales visitados este mes</span></div><div class="performance-card"><strong id="todayVisitors">0</strong><span>Locales visitados hoy</span></div><div class="performance-card"><strong id="todaySales">0</strong><span>Ventas de hoy</span></div><div class="performance-card"><strong id="monthSales">0</strong><span>Ventas del mes</span></div><div class="performance-card"><strong id="todayRate">0%</strong><span>Venta de hoy</span></div></div></section>
            <section class="stats-panel lp-panel"><div class="panel-header"><div><h2>Gráfico de ventas</h2><p>Locales visitados versus ventas acumuladas</p></div><span class="badge badge-enviado" id="lpMeta">0 locales · 0 ventas</span></div><div class="lp-chart-wrap"><svg class="lp-chart" id="lpChart" viewBox="0 0 760 230" role="img" aria-label="Progreso de locales y ventas"><line class="lp-grid-line" x1="50" y1="25" x2="730" y2="25"></line><line class="lp-grid-line" x1="50" y1="75" x2="730" y2="75"></line><line class="lp-grid-line" x1="50" y1="125" x2="730" y2="125"></line><line class="lp-grid-line" x1="50" y1="175" x2="730" y2="175"></line><text class="lp-axis-label" x="4" y="29">ventas</text><text class="lp-axis-label" x="50" y="216">locales visitados</text><polyline id="lpLine" class="lp-line" points="50,175 730,175"></polyline><g id="lpPoints"></g></svg></div></section>
            <section class="stats-panel light"><div class="panel-header"><div><h2>Registrar visita</h2><p>Buscá una objeción del catálogo y seleccioná la sugerencia correspondiente.</p></div></div><div class="stats-entry"><div><label>¿El cliente te escuchó?</label><div class="heard-actions"><button type="button" class="yes" id="heardYes">Sí</button><button type="button" class="no" id="heardNo">No</button></div></div><div><label>Ventas obtenidas</label><div class="sales-stepper"><button type="button" id="salesDown" aria-label="Restar venta">−</button><strong id="salesValue">0</strong><button type="button" id="salesUp" aria-label="Sumar venta">+</button></div></div></div><div class="search-panel" style="margin-top:16px"><label for="objectionSearch">Buscar objeción</label><input id="objectionSearch" class="search-input" type="search" autocomplete="off" placeholder="Escribí lo que te respondió el cliente"><div class="suggestions" id="suggestions" role="listbox"></div></div><div class="entry-status" id="entryStatus" role="status" aria-live="polite"></div></section>
            <section class="stats-panel light"><div class="panel-header"><div><h2>Objeciones frecuentes</h2><p>Las etiquetas amarillas superan el 20% de los clientes que dijeron Sí; las rojas superan el 50%.</p></div></div><div class="objection-tags" id="objectionTags"></div></section>
        </div>
    </div>
</main>
<script>
const redesignedStorageKey = 'gednet-estadisticas-v1-' + {{ usuario|tojson }};
const redesignedHistoryKey = 'gednet-estadisticas-historial-v1-' + {{ usuario|tojson }};
const objectionCatalog = {{ catalogo|tojson }};
const defaultRedesignedStats = { yes:0, no:0, sales:0, objections:[], days:{}, currentStreak:0, periodMonth:'' };
function today() {
    const date = new Date();
    return date.getFullYear() + '-' + String(date.getMonth()+1).padStart(2,'0') + '-' + String(date.getDate()).padStart(2,'0');
}
function monthOf(date) { return date.slice(0,7); }
function currentMonth() { return monthOf(today()); }

let redesignedStats = loadRedesignedStats();
function normalize(value){ return String(value || '').trim().toLocaleLowerCase(); }
function emptyDay(){ return { yes:0, no:0, sales:0 }; }
function snapshotStats(value){ return { yes:Number(value.yes||0), no:Number(value.no||0), sales:Number(value.sales||0), objections:(value.objections||[]).map(item => ({text:item.text,count:Number(item.count||0),problema:item.problema||'',solucion:item.solucion||''})) }; }
function loadRedesignedStats(){
    let saved={}; try { saved=JSON.parse(localStorage.getItem(redesignedStorageKey)) || {}; } catch(error) {}
    const value={...defaultRedesignedStats,...saved,days:{...(saved.days||{})},objections:Array.isArray(saved.objections)?saved.objections:[]};
    value.objections=value.objections.map(item => { const catalog=objectionCatalog.find(entry => normalize(entry.objecion)===normalize(item.text||item.objecion)); return {...item,text:item.text||item.objecion||'',count:Number(item.count||item.cantidad||0),problema:item.problema||catalog?.problema||'',solucion:item.solucion||catalog?.solucion||'',createdAt:item.createdAt||Date.now()}; });
    if(!value.periodMonth) value.periodMonth=currentMonth();
    if(value.periodMonth!==currentMonth()){
        let history=[]; try{history=JSON.parse(localStorage.getItem(redesignedHistoryKey))||[];}catch(error){}
        history=[{month:value.periodMonth,stats:snapshotStats(value),savedAt:new Date().toISOString()},...history.filter(item=>item.month!==value.periodMonth)];
        localStorage.setItem(redesignedHistoryKey,JSON.stringify(history));
        const reset={...defaultRedesignedStats,periodMonth:currentMonth()};
        localStorage.setItem(redesignedStorageKey,JSON.stringify(reset));
        return reset;
    }
    return value;
}
function saveRedesignedStats(){ localStorage.setItem(redesignedStorageKey,JSON.stringify(redesignedStats)); }
function setStatus(text,type){ const node=document.getElementById('entryStatus'); node.textContent=text; node.className='entry-status '+(type||''); }
function dayStats(key=today()){ return redesignedStats.days[key] || emptyDay(); }
function changeResponse(kind){ const key=today(); const day={...dayStats(key)}; day[kind]++; redesignedStats[kind]++; redesignedStats.days[key]=day; redesignedStats.currentStreak=Number(redesignedStats.currentStreak||0)+1; saveRedesignedStats(); setStatus('Respuesta guardada.','success'); renderAll(); }
function changeSales(delta){ const key=today(); const day={...dayStats(key)}; const next=Math.max(0,Number(redesignedStats.sales||0)+delta); const actual=next-Number(redesignedStats.sales||0); redesignedStats.sales=next; day.sales=Math.max(0,Number(day.sales||0)+actual); redesignedStats.days[key]=day; if(delta>0) redesignedStats.currentStreak=0; saveRedesignedStats(); setStatus(delta>0?'Venta registrada.':'Venta actualizada.','success'); renderAll(); }
function scoreSuggestion(query,item){ const words=normalize(query).split(/\s+/).filter(Boolean); const hay=normalize(item.objecion+' '+item.problema+' '+item.solucion); return words.reduce((score,word)=>score+(hay.includes(word)?(normalize(item.objecion).includes(word)?4:1):0),0); }
function renderSuggestions(query){ const box=document.getElementById('suggestions'); const clean=normalize(query); if(!clean){box.classList.remove('open');box.innerHTML='';return;} const matches=objectionCatalog.map((item,index)=>({item,index,score:scoreSuggestion(clean,item)})).filter(result=>result.score>0).sort((a,b)=>b.score-a.score||a.item.objecion.localeCompare(b.item.objecion)).slice(0,7); box.innerHTML=''; if(!matches.length){box.classList.remove('open');return;} matches.forEach(result=>{const button=document.createElement('button');button.type='button';button.className='suggestion';button.innerHTML='<strong>'+escapeHtml(result.item.objecion)+'</strong><small>'+escapeHtml(result.item.problema)+'</small>';button.addEventListener('click',()=>selectObjection(result.item));box.appendChild(button);});box.classList.add('open');}
function selectObjection(item){ const existing=redesignedStats.objections.find(entry=>normalize(entry.text)===normalize(item.objecion)); if(existing){existing.count=Number(existing.count||0)+1;existing.problema=item.problema;existing.solucion=item.solucion;}else redesignedStats.objections.push({id:Date.now().toString(36),text:item.objecion,count:1,problema:item.problema,solucion:item.solucion,createdAt:Date.now()}); saveRedesignedStats(); document.getElementById('objectionSearch').value='';document.getElementById('suggestions').classList.remove('open');setStatus('Objeción guardada en tus estadísticas.','success');renderAll();}
function escapeHtml(value){const node=document.createElement('span');node.textContent=value;return node.innerHTML;}
function percentage(value,total){return total?Math.round(value/total*100):0;}
function formatDay(key){const date=new Date(key+'T12:00:00');return 'Día '+date.getDate()+' · '+date.toLocaleDateString('es-AR',{weekday:'long',month:'long'});}
function renderRanks(){ const total=Number(redesignedStats.yes||0)+Number(redesignedStats.no||0);const solo=percentage(redesignedStats.yes,total);const flex=total?Math.round(Number(redesignedStats.sales||0)/total*100):0;const next=total?Math.min(100,Math.round(flex+(Number(redesignedStats.currentStreak||0)*(100-flex)/Math.max(1,total)))):0;[['soloValue','soloMeter',solo],['flexValue','flexMeter',flex],['draftValue','draftMeter',next]].forEach(([value,meter,number])=>{document.getElementById(value).textContent=number+'%';document.getElementById(meter).style.width=Math.min(100,number)+'%';});}
function renderSellerBadges(){
    const container=document.getElementById('sellerBadges');
    const todayTotal=Number(dayStats().yes||0)+Number(dayStats().no||0);
    const monthTotal=Number(redesignedStats.yes||0)+Number(redesignedStats.no||0);
    const heardRate=percentage(Number(redesignedStats.yes||0),monthTotal);
    const closeRate=percentage(Number(redesignedStats.sales||0),monthTotal);
    const badges=[];
    if(todayTotal>50) badges.push({tone:'green',label:'Motivado',tooltip:'Este vendedor tiene muchísima motivación y no deja pasar ningún comercio'});
    else if(todayTotal<=20) badges.push({tone:'red',label:'Desmotivado',tooltip:'Este vendedor está desmotivado y no entra a suficientes comercios'});
    else if(todayTotal<=30) badges.push({tone:'yellow',label:'Desmotivado',tooltip:'Este vendedor está desmotivado y no entra a suficientes comercios'});
    if(heardRate>70) badges.push({tone:'green',label:'Llamativo',tooltip:'La mayoría de clientes escucha a este vendedor cuando habla con ellos'});
    if(closeRate>5) badges.push({tone:'green',label:'Buen cierre',tooltip:'Este vendedor no tiene problema en hacer el cierre de una venta'});
    container.innerHTML='';
    badges.forEach(item=>{const badge=document.createElement('span');badge.className='seller-badge '+item.tone;badge.textContent=item.label;badge.dataset.tooltip=item.tooltip;container.appendChild(badge);});
}
function renderDaily(){ const rows=document.getElementById('dailyRows');const entries=Object.entries(redesignedStats.days).filter(([key,value])=>monthOf(key)===currentMonth()&&(value.yes||value.no||value.sales)).sort((a,b)=>b[0].localeCompare(a[0]));rows.innerHTML='';if(!entries.length){rows.innerHTML='<tr><td colspan="5" class="daily-empty">Todavía no hay visitas registradas este mes.</td></tr>';return;}entries.forEach(([key,value])=>{const total=Number(value.yes||0)+Number(value.no||0);const row=document.createElement('tr');row.innerHTML='<td class="day-name">'+formatDay(key)+'</td><td>'+total+'</td><td class="number">'+percentage(Number(value.sales||0),total)+'%</td><td class="number">'+percentage(Number(value.yes||0),total)+'%</td><td class="number">'+Number(value.sales||0)+'</td>';rows.appendChild(row);});}
function renderPerformance(){const total=Number(redesignedStats.yes||0)+Number(redesignedStats.no||0);const todayData=dayStats();const todayTotal=Number(todayData.yes||0)+Number(todayData.no||0);document.getElementById('monthVisitors').textContent=total;document.getElementById('todayVisitors').textContent=todayTotal;document.getElementById('todaySales').textContent=Number(todayData.sales||0);document.getElementById('monthSales').textContent=Number(redesignedStats.sales||0);document.getElementById('todayRate').textContent=percentage(Number(todayData.sales||0),todayTotal)+'%';}
function renderObjections(){const list=document.getElementById('objectionTags');list.innerHTML='';const yes=Number(redesignedStats.yes||0);const items=[...redesignedStats.objections].sort((a,b)=>Number(b.count||0)-Number(a.count||0)).filter(item=>yes&&Number(item.count||0)/yes*100>=20);if(!items.length){list.innerHTML='<span class="profile-empty">Todavía no hay objeciones por encima del umbral del 20%.</span>';return;}items.forEach(item=>{const ratio=Number(item.count||0)/yes*100;const tag=document.createElement('div');tag.className='objection-tag '+(ratio>50?'tag-danger':'tag-warning');tag.innerHTML='<span>'+escapeHtml(item.text)+'</span><span class="tag-count">'+Number(item.count||0)+'</span><div class="objection-tooltip"><strong>'+escapeHtml(item.problema||'Respuesta sugerida')+'</strong><span>'+escapeHtml(item.solucion||'No hay solución cargada para esta objeción.')+'</span></div>';list.appendChild(tag);});}
function radarPoints(values){return values.map((value,index)=>{const angle=(-Math.PI/2)+(index*2*Math.PI/5);const radius=115*(value/100);return (150+Math.cos(angle)*radius)+','+(150+Math.sin(angle)*radius);}).join(' ');}
function renderGpi(){const todayTotal=Number(dayStats().yes||0)+Number(dayStats().no||0);const monthTotal=Number(redesignedStats.yes||0)+Number(redesignedStats.no||0);const objectionTotal=redesignedStats.objections.reduce((sum,item)=>sum+Number(item.count||0),0);const gross=percentage(Number(redesignedStats.sales||0),monthTotal);const sales=Number(redesignedStats.sales||0);const salesScore=sales>10?100:sales>=7?75:sales>=4?50:25;const values=[Math.min(100,todayTotal/50*100),salesScore,percentage(Number(redesignedStats.yes||0),monthTotal),Math.min(100,monthTotal?objectionTotal/monthTotal*100:0),Math.min(100,gross/20*100)];document.getElementById('gpiShape').setAttribute('points',radarPoints(values));}
function renderLine(){const chart=document.getElementById('lpChart');const mini=document.getElementById('lpMiniChart');const entries=Object.entries(redesignedStats.days).filter(([key,value])=>monthOf(key)===currentMonth()&&(value.yes||value.no||value.sales)).sort((a,b)=>a[0].localeCompare(b[0]));let cumulative=0;const points=entries.map(([,value])=>{const visitors=Number(value.yes||0)+Number(value.no||0);cumulative+=Number(value.sales||0);return {visitors,cumulative};});const totalVisitors=points.reduce((sum,item)=>sum+item.visitors,0);const maxVisitors=Math.max(1,...points.map(item=>item.visitors));const maxSales=Math.max(1,...points.map(item=>item.cumulative));const makePoints=(width,height,left,bottom)=>points.length?points.map((item,index)=>{const x=left+(index/Math.max(1,points.length-1))*(width-left-20);const y=height-bottom-(item.cumulative/maxSales)*(height-bottom-25);return [x,y];}):[[left,height-bottom],[width-20,height-bottom]];const full=makePoints(760,230,50,45);document.getElementById('lpLine').setAttribute('points',full.map(point=>point.join(',')).join(' '));document.getElementById('lpPoints').innerHTML=full.map(point=>'<circle class="lp-point" cx="'+point[0]+'" cy="'+point[1]+'" r="4"></circle>').join('');const miniPoints=makePoints(240,90,4,12);mini.innerHTML='<polyline class="lp-line" points="'+miniPoints.map(point=>point.join(',')).join(' ')+'"></polyline>';document.getElementById('lpMeta').textContent=totalVisitors+' locales · '+Number(redesignedStats.sales||0)+' ventas';document.getElementById('lpSidebarMeta').textContent=entries.length+' días con actividad';}
function renderAll(){renderRanks();renderSellerBadges();renderDaily();renderPerformance();renderObjections();renderGpi();renderLine();document.getElementById('salesValue').textContent=Number(redesignedStats.sales||0);}
document.getElementById('heardYes').addEventListener('click',()=>changeResponse('yes'));document.getElementById('heardNo').addEventListener('click',()=>changeResponse('no'));document.getElementById('salesUp').addEventListener('click',()=>changeSales(1));document.getElementById('salesDown').addEventListener('click',()=>changeSales(-1));document.getElementById('objectionSearch').addEventListener('input',event=>renderSuggestions(event.target.value));document.addEventListener('click',event=>{if(!event.target.closest('.search-panel'))document.getElementById('suggestions').classList.remove('open');});
renderAll();
</script>
</body>
</html>
"""
