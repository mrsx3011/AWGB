import random
from datetime import datetime, timedelta, time as dtime
from urllib.parse import quote

from flask import Response, flash, jsonify, redirect, render_template_string, request, url_for

from ..constants import ARG_TZ, INTERVALO_MINIMO_MINUTOS, OBJECION_RANDOM, OBJECIONES, TOTAL_LOCALES_OBJETIVO
from ..database import CAMPOS, ejecutar, todos, uno
from ..logging_utils import log
from ..services.locales import (calles_de_hoy, contar_locales_hoy, fecha_larga, locales_de_hoy,
                                obtener_local, proximo_numero_del_dia)
from ..services.scheduler_service import agendar, recalcular_horarios_pendientes, reprogramar_jobs_pendientes, scheduler
from ..services.telegram_service import enviar_reporte_telegram
from ..templates import HTML_DASHBOARD, HTML_EDIT, HTML_FORM, HTML_LISTA
from .auth import usuario_actual


def register_main_routes(app):
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
        agendar(uid, nueva_dt)
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
