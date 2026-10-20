"""Esquemas de usuario; las respuestas nunca exponen PasswordHash."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator
from app.enums import Rol

class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    correo: EmailStr
    password: SecretStr = Field(min_length=8, max_length=128, repr=False)
    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, v):
        v = v.strip()
        if not v: raise ValueError("El nombre es obligatorio")
        return v
    @field_validator("correo")
    @classmethod
    def normalizar_correo(cls, v): return str(v).strip().lower()

class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    usuario_id: int = Field(validation_alias="UsuarioID")
    nombre: str = Field(validation_alias="Nombre")
    correo: EmailStr = Field(validation_alias="Correo")
    rol: Rol = Field(validation_alias="Rol")
    fecha_registro: datetime = Field(validation_alias="FechaRegistro")
