"""Esquemas para registro, login y perfil."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class RegistroCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    correo: EmailStr
    password: str = Field(min_length=10, max_length=128, repr=False)
    telefono: str = Field(min_length=7, max_length=30)
    direccion: str = Field(min_length=5, max_length=300)
    @field_validator("nombre", "telefono", "direccion")
    @classmethod
    def limpiar_texto(cls, v):
        v = v.strip()
        if not v: raise ValueError("Este campo es obligatorio")
        return v
    @field_validator("correo")
    @classmethod
    def normalizar_correo(cls, v): return str(v).strip().lower()

class LoginCreate(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=1, max_length=128, repr=False)
    @field_validator("correo")
    @classmethod
    def normalizar_correo(cls, v): return str(v).strip().lower()

class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    usuario_id: int = Field(validation_alias="UsuarioID")
    nombre: str = Field(validation_alias="Nombre")
    correo: EmailStr = Field(validation_alias="Correo")
    telefono: str = Field(validation_alias="Telefono")
    direccion: str = Field(validation_alias="Direccion")
    rol: str = Field(validation_alias="Rol")
    fecha_registro: datetime = Field(validation_alias="FechaRegistro")

class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRead

class PerfilUpdate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    telefono: str = Field(min_length=7, max_length=30)
    direccion: str = Field(min_length=5, max_length=300)
    @field_validator("nombre", "telefono", "direccion")
    @classmethod
    def limpiar_texto(cls, v):
        v = v.strip()
        if not v: raise ValueError("Este campo es obligatorio")
        return v
