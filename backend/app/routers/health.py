"""
Endpoint de verificación. No es una operación transaccional del
negocio: solo confirma que la API está viva y que la conexión a
TramaDB responde. Las rutas de negocio (catálogo, carrito, pedidos,
pagos) se agregarán en la siguiente fase.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "trama-backend"}


@router.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT COUNT(*) FROM Usuarios")).scalar()
    return {"status": "ok", "usuarios_registrados": result}
