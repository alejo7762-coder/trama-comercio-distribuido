from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.exceptions import NoEncontradoError
from app.models import Categoria, Producto

def listar(db: Session, skip: int = 0, limit: int = 50, categoria_id=None, buscar=None):
    q = db.query(Producto).options(joinedload(Producto.categoria))
    if categoria_id is not None: q = q.filter(Producto.CategoriaID == categoria_id)
    if buscar and buscar.strip():
        termino = buscar.strip().replace("%", "\\%").replace("_", "\\_")
        q = q.filter(Producto.Nombre.ilike(f"%{termino}%", escape="\\"))
    return q.order_by(Producto.ProductoID).offset(skip).limit(limit).all()

def obtener_por_id(db: Session, producto_id: int):
    return db.query(Producto).options(joinedload(Producto.categoria)).filter(Producto.ProductoID == producto_id).first()

def crear(db: Session, datos):
    if db.query(Categoria).filter(Categoria.CategoriaID == datos.categoria_id).first() is None:
        from app.exceptions import NoEncontradoError
        raise NoEncontradoError(f"La categoría {datos.categoria_id} no existe")
    valores = datos.model_dump()
    obj = Producto(Nombre=valores["nombre"], Descripcion=valores.get("descripcion"), Precio=valores["precio"], Stock=valores["stock"], CategoriaID=valores["categoria_id"])
    db.add(obj); db.flush()
    return obtener_por_id(db, obj.ProductoID)

def actualizar(db: Session, producto_id: int, datos):
    obj = obtener_por_id(db, producto_id)
    if obj is None: raise NoEncontradoError(f"El producto {producto_id} no existe")
    valores = datos.model_dump(exclude_unset=True)
    if not valores: raise ValueError("Debe proporcionar al menos un campo")
    if "categoria_id" in valores and db.query(Categoria).filter(Categoria.CategoriaID == valores["categoria_id"]).first() is None:
        raise NoEncontradoError(f"La categoría {valores['categoria_id']} no existe")
    mapa = {"nombre":"Nombre", "descripcion":"Descripcion", "precio":"Precio", "stock":"Stock", "categoria_id":"CategoriaID"}
    for clave, valor in valores.items(): setattr(obj, mapa[clave], valor)
    db.flush()
    return obtener_por_id(db, producto_id)
