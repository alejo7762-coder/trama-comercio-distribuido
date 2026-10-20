"""Punto de entrada de la API y del frontend de Trama."""
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.exceptions import ConflictoError, NoEncontradoError
from app.routers import categorias, health, productos, auth, carrito, pedidos

logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
FRONTEND_DIR=Path(__file__).resolve().parents[2]/"frontend"
app=FastAPI(title="Trama API",description="Comercio electrónico transaccional Trama",version="1.0.0")
app.include_router(health.router,tags=["Estado del sistema"])
app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(productos.router)
app.include_router(carrito.router)
app.include_router(pedidos.router)

@app.exception_handler(NoEncontradoError)
async def manejar_no_encontrado(request:Request,exc:NoEncontradoError):
    return JSONResponse(status_code=404,content={"detail":str(exc)})
@app.exception_handler(ConflictoError)
async def manejar_conflicto(request:Request,exc:ConflictoError):
    return JSONResponse(status_code=409,content={"detail":str(exc)})
if FRONTEND_DIR.is_dir():
    app.mount("/app",StaticFiles(directory=FRONTEND_DIR,html=True),name="frontend")
    @app.get("/",include_in_schema=False)
    def raiz(): return RedirectResponse("/app/")
else:
    @app.get("/",tags=["Estado del sistema"])
    def raiz_sin_frontend(): return {"mensaje":"API de Trama","documentacion":"/docs"}
