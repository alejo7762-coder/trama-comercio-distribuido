from sqlalchemy.orm import Session
from app.exceptions import ConflictoError
from app.models import Usuario

def crear(db: Session, nombre: str, correo: str, password_hash: str):
    correo = correo.strip().lower()
    if obtener_por_correo(db, correo):
        raise ConflictoError(f"El correo '{correo}' ya está registrado")
    obj = Usuario(Nombre=nombre.strip(), Correo=correo, PasswordHash=password_hash, Rol="CLIENTE")
    db.add(obj); db.flush()
    return obj

def obtener_por_correo(db: Session, correo: str):
    return db.query(Usuario).filter(Usuario.Correo == correo.strip().lower()).first()

def listar(db: Session, skip: int = 0, limit: int = 50):
    return db.query(Usuario).order_by(Usuario.UsuarioID).offset(skip).limit(limit).all()
