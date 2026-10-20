from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import ConflictoError
from app.models import Categoria
from app.schemas.categoria import CategoriaCreate


def obtener_por_id(db: Session, categoria_id: int) -> Optional[Categoria]:
    return db.get(Categoria, categoria_id)


def obtener_por_nombre(db: Session, nombre: str) -> Optional[Categoria]:
    return db.scalar(select(Categoria).where(Categoria.Nombre == nombre.strip()))


def listar(db: Session) -> list[Categoria]:
    return list(db.scalars(select(Categoria).order_by(Categoria.Nombre)))


def crear(db: Session, datos: CategoriaCreate) -> Categoria:
    if obtener_por_nombre(db, datos.nombre):
        raise ConflictoError("Ya existe una categoría con ese nombre")
    categoria = Categoria(Nombre=datos.nombre)
    db.add(categoria)
    db.flush()
    db.refresh(categoria)
    return categoria
