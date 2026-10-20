"""Modelos ORM para catálogo y comercio transaccional."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Usuario(Base):
    __tablename__="Usuarios"
    __table_args__=(CheckConstraint("Rol IN ('CLIENTE', 'ADMIN')",name="CK_Usuarios_Rol"),)
    UsuarioID=Column(Integer,primary_key=True,index=True)
    Nombre=Column(String(100),nullable=False)
    Correo=Column(String(150),nullable=False,unique=True,index=True)
    PasswordHash=Column(String(255),nullable=False)
    Rol=Column(String(20),nullable=False,default="CLIENTE")
    FechaRegistro=Column(DateTime,server_default=func.now())
    Telefono=Column(String(30),nullable=False,default="")
    Direccion=Column(String(300),nullable=False,default="")

class Categoria(Base):
    __tablename__="Categorias"
    CategoriaID=Column(Integer,primary_key=True,index=True)
    Nombre=Column(String(80),nullable=False,unique=True)

class Producto(Base):
    __tablename__="Productos"
    __table_args__=(CheckConstraint("Precio > 0",name="CK_Productos_Precio"),CheckConstraint("Stock >= 0",name="CK_Productos_Stock"))
    ProductoID=Column(Integer,primary_key=True,index=True)
    Nombre=Column(String(150),nullable=False)
    Descripcion=Column(String(500),nullable=True)
    Precio=Column(Numeric(10,2),nullable=False)
    Stock=Column(Integer,nullable=False)
    CategoriaID=Column(Integer,ForeignKey("Categorias.CategoriaID"),nullable=False)
    FechaCreacion=Column(DateTime,server_default=func.now())
    Activo=Column(Boolean,nullable=False,default=True,server_default="1")
    categoria=relationship("Categoria")

class Carrito(Base):
    __tablename__="Carritos"
    CarritoID=Column(Integer,primary_key=True,index=True)
    UsuarioID=Column(Integer,ForeignKey("Usuarios.UsuarioID"),nullable=False,unique=True)
    FechaCreacion=Column(DateTime,server_default=func.now())

class CarritoItem(Base):
    __tablename__="CarritoItems"
    __table_args__=(CheckConstraint("Cantidad > 0",name="CK_CarritoItems_Cantidad"),UniqueConstraint("CarritoID","ProductoID",name="UQ_CarritoItems_Carrito_Producto"))
    CarritoItemID=Column(Integer,primary_key=True,index=True)
    CarritoID=Column(Integer,ForeignKey("Carritos.CarritoID"),nullable=False)
    ProductoID=Column(Integer,ForeignKey("Productos.ProductoID"),nullable=False)
    Cantidad=Column(Integer,nullable=False)
    PrecioUnitario=Column(Numeric(10,2),nullable=False)

class Pedido(Base):
    __tablename__="Pedidos"
    __table_args__=(CheckConstraint("Estado IN ('PENDIENTE', 'PAGADO', 'ENVIADO', 'CANCELADO')",name="CK_Pedidos_Estado"),CheckConstraint("Total >= 0",name="CK_Pedidos_Total"))
    PedidoID=Column(Integer,primary_key=True,index=True)
    UsuarioID=Column(Integer,ForeignKey("Usuarios.UsuarioID"),nullable=False)
    FechaPedido=Column(DateTime,server_default=func.now())
    Estado=Column(String(20),nullable=False,default="PENDIENTE")
    Total=Column(Numeric(10,2),nullable=False)
    DireccionEnvio=Column(String(300),nullable=False,default="")
    TelefonoContacto=Column(String(30),nullable=False,default="")

class PedidoItem(Base):
    __tablename__="PedidoItems"
    __table_args__=(CheckConstraint("Cantidad > 0",name="CK_PedidoItems_Cantidad"),)
    PedidoItemID=Column(Integer,primary_key=True,index=True)
    PedidoID=Column(Integer,ForeignKey("Pedidos.PedidoID"),nullable=False)
    ProductoID=Column(Integer,ForeignKey("Productos.ProductoID"),nullable=False)
    Cantidad=Column(Integer,nullable=False)
    PrecioUnitario=Column(Numeric(10,2),nullable=False)

class Pago(Base):
    __tablename__="Pagos"
    __table_args__=(CheckConstraint("Monto > 0",name="CK_Pagos_Monto"),CheckConstraint("MetodoPago IN ('TARJETA', 'PSE', 'CONTRAENTREGA')",name="CK_Pagos_MetodoPago"),CheckConstraint("Estado IN ('APROBADO', 'RECHAZADO', 'PENDIENTE')",name="CK_Pagos_Estado"))
    PagoID=Column(Integer,primary_key=True,index=True)
    PedidoID=Column(Integer,ForeignKey("Pedidos.PedidoID"),nullable=False,unique=True)
    Monto=Column(Numeric(10,2),nullable=False)
    MetodoPago=Column(String(30),nullable=False)
    Estado=Column(String(20),nullable=False,default="PENDIENTE")
    FechaPago=Column(DateTime,server_default=func.now())

class Factura(Base):
    __tablename__="Facturas"
    FacturaID=Column(Integer,primary_key=True,index=True)
    PedidoID=Column(Integer,ForeignKey("Pedidos.PedidoID"),nullable=False,unique=True)
    NumeroFactura=Column(String(30),nullable=False,unique=True)
    FechaEmision=Column(DateTime,server_default=func.now())

class Notificacion(Base):
    __tablename__="Notificaciones"
    NotificacionID=Column(Integer,primary_key=True,index=True)
    UsuarioID=Column(Integer,ForeignKey("Usuarios.UsuarioID"),nullable=False)
    PedidoID=Column(Integer,ForeignKey("Pedidos.PedidoID"),nullable=True)
    Mensaje=Column(String(300),nullable=False)
    Leida=Column(Boolean,nullable=False,default=False)
    FechaEnvio=Column(DateTime,server_default=func.now())
