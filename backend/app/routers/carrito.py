"""Operaciones del carrito autenticado."""
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import confirmar, get_db
from app.dependencies import usuario_actual
from app.models import Carrito, CarritoItem, Producto, Usuario
from app.schemas.commerce import CarritoItemCreate, CarritoItemUpdate, CarritoRead

router = APIRouter(prefix="/carrito", tags=["Carrito"])

def _carrito(db, usuario):
    carrito = db.query(Carrito).filter(Carrito.UsuarioID == usuario.UsuarioID).first()
    if carrito is None:
        carrito = Carrito(UsuarioID=usuario.UsuarioID); db.add(carrito); db.flush()
    return carrito

def _serializar(db, carrito):
    items=[]; total=Decimal("0.00")
    for ci in db.query(CarritoItem).filter(CarritoItem.CarritoID == carrito.CarritoID).all():
        p=db.query(Producto).filter(Producto.ProductoID == ci.ProductoID).first()
        if p is None: continue
        subtotal=Decimal(str(p.Precio))*ci.Cantidad; total += subtotal
        items.append({"producto_id":p.ProductoID,"nombre":p.Nombre,"precio_unitario":p.Precio,"cantidad":ci.Cantidad,"stock_disponible":p.Stock,"subtotal":subtotal})
    return {"items":items,"total":total}

@router.get("", response_model=CarritoRead)
def ver_carrito(usuario: Usuario=Depends(usuario_actual), db: Session=Depends(get_db)):
    carrito=_carrito(db,usuario); resultado=_serializar(db,carrito); db.commit(); return resultado

@router.post("/items", response_model=CarritoRead, status_code=201)
def agregar_item(datos: CarritoItemCreate, usuario: Usuario=Depends(usuario_actual), db: Session=Depends(get_db)):
    p=db.query(Producto).filter(Producto.ProductoID==datos.producto_id).first()
    if not p: raise HTTPException(404,"Producto no encontrado")
    if p.Stock < datos.cantidad: raise HTTPException(409,"No hay existencias suficientes")
    carrito=_carrito(db,usuario); item=db.query(CarritoItem).filter_by(CarritoID=carrito.CarritoID,ProductoID=p.ProductoID).first()
    nueva=datos.cantidad+(item.Cantidad if item else 0)
    if nueva>p.Stock: raise HTTPException(409,"La cantidad supera el stock disponible")
    if item: item.Cantidad=nueva
    else: db.add(CarritoItem(CarritoID=carrito.CarritoID,ProductoID=p.ProductoID,Cantidad=datos.cantidad,PrecioUnitario=p.Precio))
    confirmar(db); return _serializar(db,carrito)

@router.patch("/items/{producto_id}", response_model=CarritoRead)
def cambiar_cantidad(producto_id:int, datos:CarritoItemUpdate, usuario:Usuario=Depends(usuario_actual), db:Session=Depends(get_db)):
    carrito=_carrito(db,usuario); item=db.query(CarritoItem).filter_by(CarritoID=carrito.CarritoID,ProductoID=producto_id).first()
    p=db.query(Producto).filter(Producto.ProductoID==producto_id).first()
    if not item or not p: raise HTTPException(404,"Producto no encontrado en el carrito")
    if datos.cantidad>p.Stock: raise HTTPException(409,"La cantidad supera el stock disponible")
    item.Cantidad=datos.cantidad; confirmar(db); return _serializar(db,carrito)

@router.delete("/items/{producto_id}", response_model=CarritoRead)
def quitar_item(producto_id:int, usuario:Usuario=Depends(usuario_actual), db:Session=Depends(get_db)):
    carrito=_carrito(db,usuario); item=db.query(CarritoItem).filter_by(CarritoID=carrito.CarritoID,ProductoID=producto_id).first()
    if item: db.delete(item); confirmar(db)
    return _serializar(db,carrito)
