from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.database import confirmar, get_db
from app.dependencies import administrador_actual
from app.exceptions import NoEncontradoError
from app.repositories import producto_repository
from app.schemas.producto import ProductoCreate, ProductoRead, ProductoUpdate

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("", response_model=list[ProductoRead], summary="Consultar el catálogo")
def listar_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    categoria_id: Optional[int] = Query(None, gt=0),
    buscar: Optional[str] = Query(None, max_length=100),
    db: Session = Depends(get_db),
):
    return producto_repository.listar(db, skip=skip, limit=limit, categoria_id=categoria_id, buscar=buscar)


@router.get("/{producto_id}", response_model=ProductoRead, summary="Consultar un producto")
def obtener_producto(producto_id: int = Path(gt=0), db: Session = Depends(get_db)):
    producto = producto_repository.obtener_por_id(db, producto_id)
    if producto is None:
        raise NoEncontradoError(f"El producto {producto_id} no existe")
    return producto


@router.post("", response_model=ProductoRead, status_code=201, summary="Registrar un producto")
def crear_producto(datos: ProductoCreate, _: object = Depends(administrador_actual), db: Session = Depends(get_db)):
    producto = producto_repository.crear(db, datos)
    confirmar(db)
    return producto


@router.patch("/{producto_id}", response_model=ProductoRead, summary="Actualizar un producto")
def actualizar_producto(datos: ProductoUpdate, producto_id: int = Path(gt=0), _: object = Depends(administrador_actual), db: Session = Depends(get_db)):
    producto = producto_repository.actualizar(db, producto_id, datos)
    confirmar(db)
    return producto


@router.delete("/{producto_id}", status_code=204, summary="Eliminar un producto")
def eliminar_producto(producto_id: int = Path(gt=0), _: object = Depends(administrador_actual), db: Session = Depends(get_db)):
    producto = producto_repository.obtener_por_id(db, producto_id)
    if producto is None:
        raise NoEncontradoError(f"El producto {producto_id} no existe")
    # Conserva el historial de pedidos: los productos ya vendidos no se borran físicamente.
    from app.models import PedidoItem, CarritoItem
    vendido = db.query(PedidoItem).filter(PedidoItem.ProductoID == producto_id).first()
    if vendido:
        producto.Activo = False
        producto.Stock = 0
        confirmar(db)
        return None
    db.query(CarritoItem).filter(CarritoItem.ProductoID == producto_id).delete(synchronize_session=False)
    db.delete(producto)
    confirmar(db)
    return None
