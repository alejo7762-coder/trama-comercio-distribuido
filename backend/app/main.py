"""
Punto de entrada del backend de Trama.

Estado actual: estructura base (conexión a SQL Server y verificación de
estado). Las rutas de negocio se agregan fase por fase.
"""

import logging

from fastapi import FastAPI

from app.routers import health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(
    title="Trama API",
    description="Backend del sistema transaccional de comercio electrónico Trama.",
    version="0.1.0",
)

app.include_router(health.router, tags=["Estado del sistema"])


@app.get("/", tags=["Estado del sistema"])
def root():
    return {"mensaje": "API de Trama en construcción", "documentacion": "/docs"}
