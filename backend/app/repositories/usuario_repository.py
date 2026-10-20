from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import Rol
from app.exceptions import ConflictoError
from app.models import Usuario


def normalizar_correo(correo: str) -> str:
    return correo.strip().lower()


def obtener_por_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    return db.get(Usuario, usuario_id)


def obtener_por_correo(db: Session, correo: str) -> Optional[Usuario]:
    return db.scalar(select(Usuario).where(Usuario.Correo == normalizar_correo(correo)))


def listar(db: Session, skip: int = 0, limit: int = 50) -> list[Usuario]:
    stmt = select(Usuario).order_by(Usuario.UsuarioID).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def crear(db: Session, nombre: str, correo: str, password_hash: str,
          rol: Rol = Rol.CLIENTE) -> Usuario:
    """Crea un usuario. Recibe el hash ya calculado: nunca la contraseña en claro."""
    if obtener_por_correo(db, correo):
        raise ConflictoError("El correo ya está registrado")
    usuario = Usuario(
        Nombre=nombre.strip(),
        Correo=normalizar_correo(correo),
        PasswordHash=password_hash,
        Rol=rol.value,
    )
    db.add(usuario)
    db.flush()
    db.refresh(usuario)
    return usuario
