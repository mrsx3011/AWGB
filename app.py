import os
import sys

from app import app
from app.database import crear_usuario
from app.logging_utils import log

if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "crear_usuario":
        crear_usuario(sys.argv[2], sys.argv[3], sys.argv[4])
        log("USUARIOS", f"✅ Usuario '{sys.argv[3]}' creado.")
        sys.exit(0)

    log("ARRANQUE", "🌐 Servidor listo")
    app.run(debug=False, port=int(os.environ.get("PORT", 5000)), use_reloader=False)
