from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator

from app.enums import Rol
from app.schemas.base import LecturaORM

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class UsuarioCreate(BaseModel):
    """Datos para registrarse. La contraseña llega en claro y se convierte en hash en la Fase 4."""

    nombre: Nombre
    correo: EmailStr
    password: str = Field(min_length=8, max_length=128, repr=False)

    @field_validator("correo")
    @classmethod
    def _largo_correo(cls, v: str) -> str:
        if len(v) > 150:
            raise ValueError("El correo no puede superar 150 caracteres")
        return v


class UsuarioRead(LecturaORM):
    """Vista pública de un usuario. Nunca incluye el hash de la contraseña."""

    usuario_id: int = Field(validation_alias="UsuarioID")
    nombre: str = Field(validation_alias="Nombre")
    correo: str = Field(validation_alias="Correo")
    rol: Rol = Field(validation_alias="Rol")
    fecha_registro: datetime = Field(validation_alias="FechaRegistro")
