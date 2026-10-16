"""
Diagnóstico del entorno local de Trama.

Uso (desde la carpeta backend, con el entorno virtual activado):
    python scripts/check_env.py

Comprueba: versión de Python, archivo .env, pyodbc, driver ODBC,
conexión al servidor SQL Server y existencia de la base TramaDB.
Termina con código 1 si alguna comprobación obligatoria falla.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

fallos = 0


def ok(msg):
    print(f"[OK]    {msg}")


def aviso(msg):
    print(f"[AVISO] {msg}")


def fallo(msg):
    global fallos
    fallos += 1
    print(f"[FALLO] {msg}")


# 1. Python
v = sys.version_info
if v >= (3, 10):
    ok(f"Python {v.major}.{v.minor}.{v.micro}")
else:
    fallo(f"Python {v.major}.{v.minor} es muy antiguo; se requiere 3.10 o superior.")

# 2. .env
from app.database import (  # noqa: E402
    DB_DRIVER, DB_NAME, DB_SERVER, DB_TRUSTED_CONNECTION, DB_USER,
    ENV_PATH, build_odbc_connection_string,
)

if ENV_PATH.exists():
    ok(f"Archivo .env encontrado: {ENV_PATH}")
else:
    fallo(f"No existe {ENV_PATH}. Copie .env.example como .env y complételo.")

# 3. pyodbc y drivers
try:
    import pyodbc
except ImportError as e:
    fallo(f"No se pudo importar pyodbc: {e}")
    sys.exit(1)

ok(f"pyodbc {pyodbc.version}")
drivers = [d for d in pyodbc.drivers() if "SQL Server" in d]
print("        Drivers de SQL Server instalados:", drivers or "ninguno")
if DB_DRIVER in pyodbc.drivers():
    ok(f"Driver configurado disponible: {DB_DRIVER}")
else:
    fallo(f"El driver '{DB_DRIVER}' no está instalado. "
          f"Ajuste DB_DRIVER en .env a uno de los listados arriba.")

# 4. Conexión al servidor (base master, que siempre existe)
modo = "autenticación de Windows" if DB_TRUSTED_CONNECTION else f"usuario '{DB_USER}'"
print(f"        Servidor: {DB_SERVER} | modo: {modo}")
try:
    conn = pyodbc.connect(build_odbc_connection_string("master"), timeout=5)
    ok("Conexión al servidor SQL Server establecida")
    fila = conn.cursor().execute("SELECT @@VERSION").fetchone()
    print("        " + fila[0].splitlines()[0])
    existe = conn.cursor().execute("SELECT DB_ID(?)", DB_NAME).fetchone()[0]
    if existe:
        ok(f"La base de datos {DB_NAME} existe")
    else:
        aviso(f"La base de datos {DB_NAME} aún no existe (se crea en la Fase 2 con schema.sql)")
    conn.close()
except pyodbc.Error as e:
    fallo(f"No se pudo conectar al servidor: {e}")

print()
if fallos:
    print(f"Resultado: {fallos} comprobación(es) fallida(s). Corrija y vuelva a ejecutar.")
    sys.exit(1)
print("Resultado: entorno listo.")
