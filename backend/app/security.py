"""Autenticación JWT y hash seguro de contraseñas."""
import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()
_ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return _password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return _password_hash.verify(password, hashed)
    except Exception:
        return False

def create_access_token(usuario_id: int, rol: str) -> str:
    secret = os.getenv("JWT_SECRET_KEY", "")
    if len(secret) < 32 or "REEMPLAZAR" in secret.upper() or "CAMBIAR" in secret.upper():
        raise RuntimeError("Configura JWT_SECRET_KEY con un secreto aleatorio de al menos 32 caracteres en backend/.env")
    now = datetime.now(timezone.utc)
    payload = {"sub": str(usuario_id), "role": rol, "iat": now, "exp": now + timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "30")))}
    return jwt.encode(payload, secret, algorithm=_ALGORITHM)

def decode_access_token(token: str):
    secret = os.getenv("JWT_SECRET_KEY", "")
    if len(secret) < 32 or "REEMPLAZAR" in secret.upper() or "CAMBIAR" in secret.upper():
        raise JWTError("JWT_SECRET_KEY no está configurada correctamente")
    return jwt.decode(token, secret, algorithms=[_ALGORITHM])
