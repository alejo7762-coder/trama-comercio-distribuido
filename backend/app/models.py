"""
Modelos ORM (SQLAlchemy) que reflejan la estructura definida en
database/schema.sql.

La base de datos es la fuente de verdad: estos modelos NO se usan para
crear tablas (no se llama a create_all sobre SQL Server). Las
restricciones CHECK y UNIQUE se declaran aquí con los mismos nombres que
en schema.sql para documentarlas y poder probar la lógica con SQLite.
"""

from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer,
    Numeric, String, Unicode, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Usuario(Base):
    __tablename__ = "Usuarios"
    __table_args__ = (
        CheckConstraint("Rol IN ('CLIENTE', 'ADMIN')", name="CK_Usuarios_Rol"),
    )

    UsuarioID = Column(Integer, primary_key=True, index=True)
    Nombre = Column(Unicode(100), nullable=False)
    Correo = Column(Unicode(150), nullable=False, unique=True)
    PasswordHash = Column(Unicode(255), nullable=False)
    Rol = Column(String(20), nullable=False, default="CLIENTE")
    FechaRegistro = Column(DateTime, nullable=False, server_default=func.now())

    carrito = relationship("Carrito", back_populates="usuario", uselist=False)


class Categoria(Base):
    __tablename__ = "Categorias"

    CategoriaID = Column(Integer, primary_key=True, index=True)
    Nombre = Column(Unicode(80), nullable=False, unique=True)

    productos = relationship("Producto", back_populates="categoria")


class Producto(Base):
    __tablename__ = "Productos"
    __table_args__ = (
        CheckConstraint("Precio > 0", name="CK_Productos_Precio"),
        CheckConstraint("Stock >= 0", name="CK_Productos_Stock"),
    )

    ProductoID = Column(Integer, primary_key=True, index=True)
    Nombre = Column(Unicode(150), nullable=False)
    Descripcion = Column(Unicode(500), nullable=True)
    Precio = Column(Numeric(10, 2), nullable=False)
    Stock = Column(Integer, nullable=False)
    CategoriaID = Column(Integer, ForeignKey("Categorias.CategoriaID"), nullable=False)
    FechaCreacion = Column(DateTime, nullable=False, server_default=func.now())

    categoria = relationship("Categoria", back_populates="productos")


class Carrito(Base):
    __tablename__ = "Carritos"

    CarritoID = Column(Integer, primary_key=True, index=True)
    UsuarioID = Column(Integer, ForeignKey("Usuarios.UsuarioID"), nullable=False, unique=True)
    FechaCreacion = Column(DateTime, nullable=False, server_default=func.now())

    usuario = relationship("Usuario", back_populates="carrito")
    items = relationship(
        "CarritoItem", back_populates="carrito",
        cascade="all, delete-orphan", passive_deletes=True,
    )


class CarritoItem(Base):
    __tablename__ = "CarritoItems"
    __table_args__ = (
        CheckConstraint("Cantidad > 0", name="CK_CarritoItems_Cantidad"),
        UniqueConstraint("CarritoID", "ProductoID", name="UQ_CarritoItems_Producto"),
    )

    CarritoItemID = Column(Integer, primary_key=True, index=True)
    CarritoID = Column(Integer, ForeignKey("Carritos.CarritoID"), nullable=False)
    ProductoID = Column(Integer, ForeignKey("Productos.ProductoID"), nullable=False)
    Cantidad = Column(Integer, nullable=False)
    PrecioUnitario = Column(Numeric(10, 2), nullable=False)

    carrito = relationship("Carrito", back_populates="items")
    producto = relationship("Producto")


class Pedido(Base):
    __tablename__ = "Pedidos"
    __table_args__ = (
        CheckConstraint(
            "Estado IN ('PENDIENTE', 'PAGADO', 'ENVIADO', 'CANCELADO')",
            name="CK_Pedidos_Estado",
        ),
        CheckConstraint("Total >= 0", name="CK_Pedidos_Total"),
    )

    PedidoID = Column(Integer, primary_key=True, index=True)
    UsuarioID = Column(Integer, ForeignKey("Usuarios.UsuarioID"), nullable=False)
    FechaPedido = Column(DateTime, nullable=False, server_default=func.now())
    Estado = Column(String(20), nullable=False, default="PENDIENTE")
    Total = Column(Numeric(10, 2), nullable=False)

    usuario = relationship("Usuario")
    items = relationship(
        "PedidoItem", back_populates="pedido",
        cascade="all, delete-orphan", passive_deletes=True,
    )
    pago = relationship("Pago", back_populates="pedido", uselist=False)
    factura = relationship("Factura", back_populates="pedido", uselist=False)
    notificaciones = relationship("Notificacion", back_populates="pedido")


class PedidoItem(Base):
    __tablename__ = "PedidoItems"
    __table_args__ = (
        CheckConstraint("Cantidad > 0", name="CK_PedidoItems_Cantidad"),
    )

    PedidoItemID = Column(Integer, primary_key=True, index=True)
    PedidoID = Column(Integer, ForeignKey("Pedidos.PedidoID"), nullable=False)
    ProductoID = Column(Integer, ForeignKey("Productos.ProductoID"), nullable=False)
    Cantidad = Column(Integer, nullable=False)
    PrecioUnitario = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")


class Pago(Base):
    __tablename__ = "Pagos"
    __table_args__ = (
        CheckConstraint("Monto > 0", name="CK_Pagos_Monto"),
        CheckConstraint(
            "MetodoPago IN ('TARJETA', 'PSE', 'CONTRAENTREGA')", name="CK_Pagos_Metodo"
        ),
        CheckConstraint(
            "Estado IN ('APROBADO', 'RECHAZADO', 'PENDIENTE')", name="CK_Pagos_Estado"
        ),
    )

    PagoID = Column(Integer, primary_key=True, index=True)
    PedidoID = Column(Integer, ForeignKey("Pedidos.PedidoID"), nullable=False, unique=True)
    Monto = Column(Numeric(10, 2), nullable=False)
    MetodoPago = Column(String(30), nullable=False)
    Estado = Column(String(20), nullable=False, default="APROBADO")
    FechaPago = Column(DateTime, nullable=False, server_default=func.now())

    pedido = relationship("Pedido", back_populates="pago")


class Factura(Base):
    __tablename__ = "Facturas"

    FacturaID = Column(Integer, primary_key=True, index=True)
    PedidoID = Column(Integer, ForeignKey("Pedidos.PedidoID"), nullable=False, unique=True)
    NumeroFactura = Column(String(30), nullable=False, unique=True)
    FechaEmision = Column(DateTime, nullable=False, server_default=func.now())

    pedido = relationship("Pedido", back_populates="factura")


class Notificacion(Base):
    __tablename__ = "Notificaciones"

    NotificacionID = Column(Integer, primary_key=True, index=True)
    UsuarioID = Column(Integer, ForeignKey("Usuarios.UsuarioID"), nullable=False)
    PedidoID = Column(Integer, ForeignKey("Pedidos.PedidoID"), nullable=True)
    Mensaje = Column(Unicode(300), nullable=False)
    Leida = Column(Boolean, nullable=False, default=False)
    FechaEnvio = Column(DateTime, nullable=False, server_default=func.now())

    usuario = relationship("Usuario")
    pedido = relationship("Pedido", back_populates="notificaciones")
