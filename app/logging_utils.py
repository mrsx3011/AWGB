from datetime import datetime

from .constants import ARG_TZ


def log(tag, msg=""):
    hora = datetime.now(ARG_TZ).strftime("%H:%M:%S")
    print(f"[{hora}] [{tag:<9}] {msg}", flush=True)
