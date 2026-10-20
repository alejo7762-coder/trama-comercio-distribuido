"""Crea o promociona una cuenta administradora usando variables de entorno."""
import os
from getpass import getpass
from app.database import SessionLocal, confirmar
from app.models import Usuario
from app.security import hash_password

def main():
    correo=os.getenv("ADMIN_EMAIL", "").strip().lower()
    if not correo:
        correo=input("Correo del administrador: ").strip().lower()
    password=os.getenv("ADMIN_PASSWORD", "") or getpass("Contraseña (mínimo 12 caracteres): ")
    if len(password)<12:
        raise SystemExit("La contraseña de administrador debe tener al menos 12 caracteres")
    db=SessionLocal()
    try:
        usuario=db.query(Usuario).filter(Usuario.Correo==correo).first()
        if usuario:
            usuario.Rol="ADMIN"
            usuario.PasswordHash=hash_password(password)
            print("Cuenta existente actualizada como ADMIN.")
        else:
            nombre=os.getenv("ADMIN_NAME", "Administrador Trama")
            usuario=Usuario(Nombre=nombre,Correo=correo,PasswordHash=hash_password(password),Rol="ADMIN",Telefono="No registrado",Direccion="No aplica")
            db.add(usuario)
        confirmar(db)
        print("Administrador configurado. Inicia sesión desde la interfaz.")
    finally:
        db.close()
if __name__=="__main__": main()
