import time
from datetime import date

import pymysql
from werkzeug.security import generate_password_hash

from .config import DB_CONFIG
from .logging_utils import log

CAMPOS = ("id AS uid, usuario, nombre, direccion, objecion, fecha, numero, estado, "
          "hora_registro, hora_programada, hora_programada_iso, hora_envio_real, hora_manual")


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
    log("DB", f"✍️  {_sql_corto(sql)} | args={_resumen_args(args)}")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            filas = cur.execute(sql, args)
            conn.commit()
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


def probar_conexion():
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
