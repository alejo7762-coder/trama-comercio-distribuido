"""
Punto de entrada del backend de Trama.

Estado actual: estructura base (conexión a SQL Server y verificación de
estado). Las rutas de negocio se agregan fase por fase.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.exceptions import ConflictoError, NoEncontradoError
from app.routers import categorias, health, productos

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(
    title="Trama API",
    description="Backend del sistema transaccional de comercio electrónico Trama.",
    version="0.2.0",
)

app.include_router(health.router, tags=["Estado del sistema"])
app.include_router(categorias.router)
app.include_router(productos.router)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="interfaz")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/app/")
