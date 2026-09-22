"""
Punto de entrada del backend de Trama.

Fase 3: solo se establece la estructura inicial (conexión a la base
de datos y un router de verificación). Las rutas de negocio del
sistema transaccional se implementarán en la siguiente fase.
"""

from fastapi import FastAPI
from app.routers import health

app = FastAPI(
    title="Trama API",
    description="Backend del sistema transaccional de comercio electrónico Trama.",
    version="0.1.0",
)

app.include_router(health.router, tags=["Estado del sistema"])


@app.get("/")
def root():
    return {"mensaje": "API de Trama en construcción — Fase 3"}
