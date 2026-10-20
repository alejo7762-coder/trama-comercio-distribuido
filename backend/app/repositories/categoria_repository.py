from sqlalchemy.orm import Session
from app.exceptions import ConflictoError
from app.models import Categoria

def listar(db: Session):
    return db.query(Categoria).order_by(Categoria.Nombre).all()

def obtener_por_id(db: Session, categoria_id: int):
    return db.query(Categoria).filter(Categoria.CategoriaID == categoria_id).first()

def crear(db: Session, datos):
    nombre = datos.nombre.strip()
    if db.query(Categoria).filter(Categoria.Nombre == nombre).first():
        raise ConflictoError(f"La categoría '{nombre}' ya existe")
    obj = Categoria(Nombre=nombre)
    db.add(obj)
    db.flush()
    return obj
