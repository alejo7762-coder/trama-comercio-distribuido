"""Dependencias para obtener el usuario autenticado y autorizar administradores."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credenciales = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida o expirada", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_access_token(token)
        usuario_id = int(payload.get("sub", ""))
    except (JWTError, ValueError, TypeError):
        raise credenciales
    usuario = db.query(Usuario).filter(Usuario.UsuarioID == usuario_id).first()
    if usuario is None:
        raise credenciales
    return usuario

def administrador_actual(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
    if usuario.Rol != "ADMIN":
        raise HTTPException(status_code=403, detail="Se requiere el rol de administrador")
    return usuario
