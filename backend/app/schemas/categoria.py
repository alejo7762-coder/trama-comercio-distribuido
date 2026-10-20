"""Esquemas de validación y respuesta para categorías."""
from pydantic import BaseModel, ConfigDict, Field, field_validator

class CategoriaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        return v

class CategoriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    categoria_id: int = Field(validation_alias="CategoriaID")
    nombre: str = Field(validation_alias="Nombre")
