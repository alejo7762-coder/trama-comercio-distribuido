"""Esquemas Pydantic de entrada y salida para productos."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class CategoriaEnProducto(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    categoria_id: int = Field(validation_alias="CategoriaID")
    nombre: str = Field(validation_alias="Nombre")

class ProductoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    categoria_id: int = Field(gt=0)
    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v):
        v = v.strip()
        if not v: raise ValueError("El nombre no puede estar vacío")
        return v
    @field_validator("descripcion")
    @classmethod
    def limpiar_descripcion(cls, v): return v.strip() if v is not None else None

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    precio: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: Optional[int] = Field(default=None, ge=0)
    categoria_id: Optional[int] = Field(default=None, gt=0)
    @model_validator(mode="after")
    def debe_tener_campos(self):
        if not self.model_fields_set:
            raise ValueError("Debe proporcionar al menos un campo para actualizar")
        return self
    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v):
        if v is None: raise ValueError("El nombre no puede ser null")
        v = v.strip()
        if not v: raise ValueError("El nombre no puede estar vacío")
        return v
    @field_validator("precio", "stock", "categoria_id")
    @classmethod
    def obligatorios_no_null(cls, v):
        if v is None: raise ValueError("Este campo no puede ser null")
        return v
    @field_validator("descripcion")
    @classmethod
    def limpiar_descripcion(cls, v): return v.strip() if v is not None else None

class ProductoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    producto_id: int = Field(validation_alias="ProductoID")
    nombre: str = Field(validation_alias="Nombre")
    descripcion: Optional[str] = Field(validation_alias="Descripcion")
    precio: Decimal = Field(validation_alias="Precio")
    stock: int = Field(validation_alias="Stock")
    categoria_id: int = Field(validation_alias="CategoriaID")
    fecha_creacion: Optional[datetime] = Field(default=None, validation_alias="FechaCreacion")
    activo: bool = Field(default=True, validation_alias="Activo")
    categoria: Optional[CategoriaEnProducto] = None
