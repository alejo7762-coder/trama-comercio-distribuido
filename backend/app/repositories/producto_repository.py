from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.exceptions import NoEncontradoError
from app.models import Categoria, Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate

# Campo del esquema -> columna del modelo
_COLUMNAS = {
    "nombre": "Nombre",
    "descripcion": "Descripcion",
    "precio": "Precio",
    "stock": "Stock",
    "categoria_id": "CategoriaID",
}


def obtener_por_id(db: Session, producto_id: int) -> Optional[Producto]:
    stmt = select(Producto).options(joinedload(Producto.categoria)).where(
        Producto.ProductoID == producto_id
    )
    return db.scalar(stmt)

def contar(db: Session, categoria_id: Optional[int] = None, buscar: Optional[str] = None) -> int:
    """Total de productos que cumplen los mismos filtros que listar() (sin paginar)."""
    stmt = select(func.count()).select_from(Producto)
    if categoria_id is not None:
        stmt = stmt.where(Producto.CategoriaID == categoria_id)
    if buscar and buscar.strip():
        stmt = stmt.where(Producto.Nombre.contains(buscar.strip(), autoescape=True))
    return db.scalar(stmt) or 0

def listar(db: Session, skip: int = 0, limit: int = 50,
           categoria_id: Optional[int] = None, buscar: Optional[str] = None) -> list[Producto]:
    stmt = select(Producto).options(joinedload(Producto.categoria)).order_by(Producto.ProductoID)
    if categoria_id is not None:
        stmt = stmt.where(Producto.CategoriaID == categoria_id)
    if buscar and buscar.strip():
        # autoescape: un % o _ escrito por el usuario se trata como texto, no como comodín
        stmt = stmt.where(Producto.Nombre.contains(buscar.strip(), autoescape=True))
    return list(db.scalars(stmt.offset(skip).limit(limit)))


def _exigir_categoria(db: Session, categoria_id: int) -> None:
    if db.get(Categoria, categoria_id) is None:
        raise NoEncontradoError(f"La categoría {categoria_id} no existe")


def crear(db: Session, datos: ProductoCreate) -> Producto:
    _exigir_categoria(db, datos.categoria_id)
    producto = Producto(
        Nombre=datos.nombre,
        Descripcion=datos.descripcion,
        Precio=datos.precio,
        Stock=datos.stock,
        CategoriaID=datos.categoria_id,
    )
    db.add(producto)
    db.flush()
    db.refresh(producto)
    return producto


def actualizar(db: Session, producto_id: int, datos: ProductoUpdate) -> Producto:
    producto = obtener_por_id(db, producto_id)
    if producto is None:
        raise NoEncontradoError(f"El producto {producto_id} no existe")
    cambios = datos.model_dump(exclude_unset=True)
    if "categoria_id" in cambios:
        _exigir_categoria(db, cambios["categoria_id"])
    for campo, valor in cambios.items():
        setattr(producto, _COLUMNAS[campo], valor)
    db.flush()
    db.refresh(producto)
    return producto
