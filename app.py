import os
import sys

from app import create_app
from app.database import crear_usuario, init_db
from app.logging_utils import log
from app.services.scheduler_service import reprogramar_jobs_pendientes

app = create_app()

init_db()
reprogramar_jobs_pendientes()

if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "crear_usuario":
        crear_usuario(sys.argv[2], sys.argv[3], sys.argv[4])
        log("USUARIOS", f"✅ Usuario '{sys.argv[3]}' creado.")
        sys.exit(0)

    log("ARRANQUE", "🌐 Servidor listo")
    app.run(debug=False, port=int(os.environ.get("PORT", 5000)), use_reloader=False)
