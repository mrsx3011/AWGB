from datetime import time as dtime

import pytz

ARG_TZ = pytz.timezone("America/Argentina/Buenos_Aires")

HORA_APERTURA = dtime(10, 0)
HORA_CIERRE = dtime(15, 55)
BUFFER_INICIAL_MINUTOS = 18
INTERVALO_MINIMO_MINUTOS = 2
MARGEN_JITTER_MINUTOS = 20
TOTAL_LOCALES_OBJETIVO = 20
OBJECION_RANDOM = "Random"

OBJECIONES = [
    "El dueño no se encontraba en el local.",
    "Ya tenian mercado pago y no lo quieren cambiar.",
    "Acaban de pedir otra terminal hace poco.",
    "Lo tienen que pensar.",
    "Lo tiene que hablar con un familiar.",
    "No le gusta trabajar con bancos por problemas en el pasado.",
    "Tienen que hablarlo con un familiar.",
    "No estan interesados.",
]

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
