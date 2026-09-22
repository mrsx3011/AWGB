from flask import Flask, request
from werkzeug.exceptions import HTTPException

from .config import Config
from .database import init_db
from .logging_utils import log
from .routes.auth import register_auth_routes
from .routes.main import register_main_routes
from .services.scheduler_service import reprogramar_jobs_pendientes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_auth_routes(app)
    register_main_routes(app)
    register_error_handlers(app)
    return app


def create_wsgi_app():
    app = create_app()
    init_db()
    reprogramar_jobs_pendientes()
    return app


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def error_global(e):
        import traceback

        if isinstance(e, HTTPException):
            return e
        log("ERROR", f"💥 Excepción en {request.method} {request.path}: {e!r}")
        log("ERROR", traceback.format_exc())
        return "Error interno. Revisá la consola del servidor.", 500


app = create_wsgi_app()
