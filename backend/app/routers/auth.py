"""Registro, inicio de sesión y perfil del usuario."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import confirmar, get_db
from app.dependencies import usuario_actual
from app.exceptions import ConflictoError
from app.models import Usuario
from app.schemas.auth import RegistroCreate, LoginCreate, TokenRead, UsuarioRead, PerfilUpdate
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=TokenRead, status_code=201)
def registrar(datos: RegistroCreate, db: Session = Depends(get_db)):
    correo = str(datos.correo).lower()
    if db.query(Usuario).filter(Usuario.Correo == correo).first():
        raise ConflictoError("Ya existe una cuenta con ese correo")
    usuario = Usuario(Nombre=datos.nombre, Correo=correo, PasswordHash=hash_password(datos.password), Rol="CLIENTE", Telefono=datos.telefono, Direccion=datos.direccion)
    db.add(usuario)
    try:
        confirmar(db)
    except ConflictoError:
        raise ConflictoError("Ya existe una cuenta con ese correo")
    db.refresh(usuario)
    return {"access_token": create_access_token(usuario.UsuarioID, usuario.Rol), "usuario": usuario}

@router.post("/login", response_model=TokenRead)
def iniciar_sesion(datos: LoginCreate, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.Correo == str(datos.correo).lower()).first()
    if not usuario or not verify_password(datos.password, usuario.PasswordHash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos", headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": create_access_token(usuario.UsuarioID, usuario.Rol), "usuario": usuario}

@router.get("/me", response_model=UsuarioRead)
def mi_perfil(usuario: Usuario = Depends(usuario_actual)):
    return usuario

@router.patch("/me", response_model=UsuarioRead)
def actualizar_perfil(datos: PerfilUpdate, usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    usuario.Nombre, usuario.Telefono, usuario.Direccion = datos.nombre, datos.telefono, datos.direccion
    confirmar(db)
    db.refresh(usuario)
    return usuario
