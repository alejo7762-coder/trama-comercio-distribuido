"""
Configuración de conexión a la base de datos TramaDB (SQL Server).

Esta capa NO define lógica de negocio: expone un motor (engine), una
sesión por solicitud (get_db) y la clase Base de los modelos ORM.

La configuración se lee de backend/.env (ver .env.example). La ruta del
.env se calcula a partir de este archivo, por lo que funciona sin
importar desde qué carpeta se ejecute uvicorn.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(ENV_PATH)


def _env_bool(nombre: str, por_defecto: bool) -> bool:
    valor = os.getenv(nombre)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in ("1", "true", "yes", "si", "sí")


DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_NAME = os.getenv("DB_NAME", "TramaDB")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
DB_TRUSTED_CONNECTION = _env_bool("DB_TRUSTED_CONNECTION", False)
DB_TRUST_SERVER_CERTIFICATE = _env_bool("DB_TRUST_SERVER_CERTIFICATE", True)
DB_LOGIN_TIMEOUT = int(os.getenv("DB_LOGIN_TIMEOUT", "5"))


def _valor_odbc(valor: str) -> str:
    """Encierra un valor entre llaves para que caracteres como ; o } no rompan la cadena."""
    return "{" + valor.replace("}", "}}") + "}"


def build_odbc_connection_string(database: str | None = None) -> str:
    """Construye la cadena ODBC. `database` permite apuntar a otra BD (p. ej. master)."""
    partes = [
        f"DRIVER={_valor_odbc(DB_DRIVER)}",
        f"SERVER={DB_SERVER}",
        f"DATABASE={database or DB_NAME}",
        f"TrustServerCertificate={'yes' if DB_TRUST_SERVER_CERTIFICATE else 'no'}",
    ]
    if DB_TRUSTED_CONNECTION:
        partes.append("Trusted_Connection=yes")
    else:
        partes.append(f"UID={_valor_odbc(DB_USER)}")
        partes.append(f"PWD={_valor_odbc(DB_PASSWORD)}")
    return ";".join(partes) + ";"


SQLALCHEMY_DATABASE_URL = URL.create(
    "mssql+pyodbc",
    query={"odbc_connect": build_odbc_connection_string()},
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"timeout": DB_LOGIN_TIMEOUT},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: una sesión de base de datos por solicitud."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
