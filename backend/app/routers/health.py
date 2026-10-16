"""
Endpoints de verificación. No son operaciones de negocio: confirman que
la API está viva y que la conexión a TramaDB responde.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db

logger = logging.getLogger("trama.health")
router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "trama-backend"}


@router.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("No fue posible conectar con SQL Server")
        raise HTTPException(
            status_code=503,
            detail="No fue posible conectar con SQL Server. Revise backend/.env "
                   "y que el servicio esté activo (ejecute: python scripts/check_env.py).",
        )

    try:
        usuarios = db.execute(text("SELECT COUNT(*) FROM Usuarios")).scalar()
    except SQLAlchemyError:
        logger.exception("Conexión correcta, pero no se pudo consultar la tabla Usuarios")
        raise HTTPException(
            status_code=503,
            detail="Hay conexión con SQL Server, pero la tabla Usuarios no existe o no es "
                   "accesible. Ejecute database/schema.sql y database/seed.sql.",
        )

    return {"status": "ok", "usuarios_registrados": usuarios}
