"""
Modelos ORM (SQLAlchemy) que reflejan la estructura definida en
database/schema.sql. En esta fase solo se declara la forma de las
entidades y sus relaciones — las operaciones CRUD se construirán
en la siguiente fase del proyecto.
"""

from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Usuario(Base):
    __tablename__ = "Usuarios"

    UsuarioID = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String(100), nullable=False)
    Correo = Column(String(150), nullable=False, unique=True)
    PasswordHash = Column(String(255), nullable=False)
    Rol = Column(String(20), nullable=False, default="CLIENTE")
    FechaRegistro = Column(DateTime, server_default=func.now())


class Categoria(Base):
    __tablename__ = "Categorias"

    CategoriaID = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String(80), nullable=False, unique=True)


class Producto(Base):
    __tablename__ = "Productos"

    ProductoID = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String(150), nullable=False)
    Descripcion = Column(String(500), nullable=True)
    Precio = Column(Numeric(10, 2), nullable=False)
    Stock = Column(Integer, nullable=False)
    CategoriaID = Column(Integer, ForeignKey("Categorias.CategoriaID"), nullable=False)
    FechaCreacion = Column(DateTime, server_default=func.now())

    categoria = relationship("Categoria")


class Carrito(Base):
    __tablename__ = "Carritos"

    CarritoID = Column(Integer, primary_key=True, index=True)
    UsuarioID = Column(Integer, ForeignKey("Usuarios.UsuarioID"), nullable=False, unique=True)
    FechaCreacion = Column(DateTime, server_default=func.now())

    usuario = relationship("Usuario")


class CarritoItem(Base):
    __tablename__ = "CarritoItems"

    CarritoItemID = Column(Integer, primary_key=True, index=True)
    CarritoID = Column(Integer, ForeignKey("Carritos.CarritoID"), nullable=False)
    ProductoID = Column(Integer, ForeignKey("Productos.ProductoID"), nullable=False)
    Cantidad = Column(Integer, nullable=False)
    PrecioUnitario = Column(Numeric(10, 2), nullable=False)


class Pedido(Base):
    __tablename__ = "Pedidos"

    PedidoID = Column(Integer, primary_key=True, index=True)
    UsuarioID = Column(Integer, ForeignKey("Usuarios.UsuarioID"), nullable=False)
    FechaPedido = Column(DateTime, server_default=func.now())
    Estado = Column(String(20), nullable=False, default="PENDIENTE")
    Total = Column(Numeric(10, 2), nullable=False)

    usuario = relationship("Usuario")


class PedidoItem(Base):
    __tablename__ = "PedidoItems"

    PedidoItemID = Column(Integer, primary_key=True, index=True)
    PedidoID = Column(Integer, ForeignKey("Pedidos.PedidoID"), nullable=False)
    ProductoID = Column(Integer, ForeignKey("Productos.ProductoID"), nullable=False)
    Cantidad = Column(Integer, nullable=False)
    PrecioUnitario = Column(Numeric(10, 2), nullable=False)


class Pago(Base):
    __tablename__ = "Pagos"

    PagoID = Column(Integer, primary_key=True, index=True)
    PedidoID = Column(Integer, ForeignKey("Pedidos.PedidoID"), nullable=False, unique=True)
    Monto = Column(Numeric(10, 2), nullable=False)
    MetodoPago = Column(String(30), nullable=False)
    Estado = Column(String(20), nullable=False, default="APROBADO")
    FechaPago = Column(DateTime, server_default=func.now())


class Factura(Base):
    __tablename__ = "Facturas"

    FacturaID = Column(Integer, primary_key=True, index=True)
    PedidoID = Column(Integer, ForeignKey("Pedidos.PedidoID"), nullable=False, unique=True)
    NumeroFactura = Column(String(30), nullable=False, unique=True)
    FechaEmision = Column(DateTime, server_default=func.now())


class Notificacion(Base):
    __tablename__ = "Notificaciones"

    NotificacionID = Column(Integer, primary_key=True, index=True)
    UsuarioID = Column(Integer, ForeignKey("Usuarios.UsuarioID"), nullable=False)
    PedidoID = Column(Integer, ForeignKey("Pedidos.PedidoID"), nullable=True)
    Mensaje = Column(String(300), nullable=False)
    Leida = Column(Boolean, nullable=False, default=False)
    FechaEnvio = Column(DateTime, server_default=func.now())
