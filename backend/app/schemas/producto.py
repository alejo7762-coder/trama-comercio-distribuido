from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, Field, StringConstraints, model_validator

from app.schemas.base import LecturaORM
from app.schemas.categoria import CategoriaRead

NombreProducto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
DescripcionProducto = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]
# Igual que DECIMAL(10,2) y CHECK (Precio > 0) en la base de datos.
PrecioProducto = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
StockProducto = Annotated[int, Field(ge=0)]


class ProductoCreate(BaseModel):
    nombre: NombreProducto
    descripcion: Optional[DescripcionProducto] = None
    precio: PrecioProducto
    stock: StockProducto
    categoria_id: int = Field(gt=0)


class ProductoUpdate(BaseModel):
    """Actualización parcial: solo se modifican los campos enviados."""

    nombre: Optional[NombreProducto] = None
    descripcion: Optional[DescripcionProducto] = None
    precio: Optional[PrecioProducto] = None
    stock: Optional[StockProducto] = None
    categoria_id: Optional[int] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def _validar_campos(self):
        if not self.model_fields_set:
            raise ValueError("Debe enviar al menos un campo para actualizar")
        # Estos campos son NOT NULL en la base: no se permite enviarlos como null.
        for campo in ("nombre", "precio", "stock", "categoria_id"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError(f"El campo '{campo}' no puede ser null")
        return self


class ProductoRead(LecturaORM):
    producto_id: int = Field(validation_alias="ProductoID")
    nombre: str = Field(validation_alias="Nombre")
    descripcion: Optional[str] = Field(default=None, validation_alias="Descripcion")
    precio: Decimal = Field(validation_alias="Precio")
    stock: int = Field(validation_alias="Stock")
    categoria_id: int = Field(validation_alias="CategoriaID")
    fecha_creacion: datetime = Field(validation_alias="FechaCreacion")
    categoria: Optional[CategoriaRead] = None
