from flask import flash, redirect, render_template_string, request, session, url_for
from werkzeug.security import check_password_hash

from ..database import uno
from ..logging_utils import log
from ..templates import HTML_LOGIN


def usuario_actual():
    return session["usuario"]


def register_auth_routes(app):

    @app.before_request
    def exigir_login():
        if request.endpoint != "foto":
            log("HTTP", f"{request.method} {request.path} | usuario={session.get('usuario')}")
        if request.endpoint in ("login", "static"):
            return
        if "usuario" not in session:
            log("LOGIN", f"🔒 Sin sesión, redirigiendo a /login (pedía {request.path})")
            return redirect(url_for("login"))


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
