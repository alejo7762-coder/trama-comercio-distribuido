"""Esquemas de carrito y pedidos."""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

class CarritoItemCreate(BaseModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(ge=1, le=99)

class CarritoItemUpdate(BaseModel):
    cantidad: int = Field(ge=1, le=99)

class CarritoItemRead(BaseModel):
    producto_id: int
    nombre: str
    precio_unitario: Decimal
    cantidad: int
    stock_disponible: int
    subtotal: Decimal

class CarritoRead(BaseModel):
    items: list[CarritoItemRead]
    total: Decimal

class CheckoutCreate(BaseModel):
    direccion_envio: str = Field(min_length=5, max_length=300)
    telefono_contacto: str = Field(min_length=7, max_length=30)
    metodo_pago: str = "CONTRAENTREGA"

class PedidoItemRead(BaseModel):
    producto_id: int
    nombre: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

class PedidoRead(BaseModel):
    pedido_id: int
    fecha_pedido: datetime | None
    estado: str
    total: Decimal
    direccion_envio: str
    telefono_contacto: str
    metodo_pago: str
    email_enviado: bool = False
    items: list[PedidoItemRead]
