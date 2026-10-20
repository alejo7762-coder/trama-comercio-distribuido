/* =========================================================
   TRAMA — Sistema Transaccional de Comercio Electrónico
   Script de creación de base de datos (SQL Server)
   Fase 3 — Estructura de datos inicial
   ========================================================= */

IF DB_ID('TramaDB') IS NULL
BEGIN
    CREATE DATABASE TramaDB;
END
GO

USE TramaDB;
GO

/* ---------------------------------------------------------
   1. USUARIOS
   Clientes que se registran y autentican en la plataforma.
   --------------------------------------------------------- */
CREATE TABLE Usuarios (
    UsuarioID       INT IDENTITY(1,1) PRIMARY KEY,
    Nombre          NVARCHAR(100)   NOT NULL,
    Correo          NVARCHAR(150)   NOT NULL UNIQUE,
    PasswordHash    NVARCHAR(255)   NOT NULL,
    Rol             VARCHAR(20)     NOT NULL DEFAULT 'CLIENTE'
                        CONSTRAINT CK_Usuarios_Rol CHECK (Rol IN ('CLIENTE', 'ADMIN')),
    FechaRegistro   DATETIME2       NOT NULL DEFAULT SYSDATETIME()
);
GO

/* ---------------------------------------------------------
   2. CATEGORIAS
   Clasificación del catálogo de productos.
   --------------------------------------------------------- */
CREATE TABLE Categorias (
    CategoriaID     INT IDENTITY(1,1) PRIMARY KEY,
    Nombre          NVARCHAR(80)    NOT NULL UNIQUE
);
GO

/* ---------------------------------------------------------
   3. PRODUCTOS
   Catálogo e inventario.
   --------------------------------------------------------- */
CREATE TABLE Productos (
    ProductoID      INT IDENTITY(1,1) PRIMARY KEY,
    Nombre          NVARCHAR(150)   NOT NULL,
    Descripcion     NVARCHAR(500)   NULL,
    Precio          DECIMAL(10,2)   NOT NULL CONSTRAINT CK_Productos_Precio CHECK (Precio > 0),
    Stock           INT             NOT NULL CONSTRAINT CK_Productos_Stock CHECK (Stock >= 0),
    CategoriaID     INT             NOT NULL,
    FechaCreacion   DATETIME2       NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Productos_Categorias FOREIGN KEY (CategoriaID)
        REFERENCES Categorias(CategoriaID)
        ON DELETE NO ACTION
);
GO

/* ---------------------------------------------------------
   4. CARRITOS
   Un carrito activo por usuario.
   --------------------------------------------------------- */
CREATE TABLE Carritos (
    CarritoID       INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID       INT             NOT NULL UNIQUE,
    FechaCreacion   DATETIME2       NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Carritos_Usuarios FOREIGN KEY (UsuarioID)
        REFERENCES Usuarios(UsuarioID)
        ON DELETE CASCADE
);
GO

/* ---------------------------------------------------------
   5. CARRITO_ITEMS
   Productos agregados a un carrito, con cantidad.
   --------------------------------------------------------- */
CREATE TABLE CarritoItems (
    CarritoItemID   INT IDENTITY(1,1) PRIMARY KEY,
    CarritoID       INT             NOT NULL,
    ProductoID      INT             NOT NULL,
    Cantidad        INT             NOT NULL CONSTRAINT CK_CarritoItems_Cantidad CHECK (Cantidad > 0),
    PrecioUnitario  DECIMAL(10,2)   NOT NULL,
    CONSTRAINT FK_CarritoItems_Carritos FOREIGN KEY (CarritoID)
        REFERENCES Carritos(CarritoID)
        ON DELETE CASCADE,
    CONSTRAINT FK_CarritoItems_Productos FOREIGN KEY (ProductoID)
        REFERENCES Productos(ProductoID)
        ON DELETE NO ACTION,
    CONSTRAINT UQ_CarritoItems_Producto UNIQUE (CarritoID, ProductoID)
);
GO

/* ---------------------------------------------------------
   6. PEDIDOS
   Pedido confirmado por un usuario.
   --------------------------------------------------------- */
CREATE TABLE Pedidos (
    PedidoID        INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID       INT             NOT NULL,
    FechaPedido     DATETIME2       NOT NULL DEFAULT SYSDATETIME(),
    Estado          VARCHAR(20)     NOT NULL DEFAULT 'PENDIENTE'
                        CONSTRAINT CK_Pedidos_Estado CHECK (Estado IN ('PENDIENTE', 'PAGADO', 'ENVIADO', 'CANCELADO')),
    Total           DECIMAL(10,2)   NOT NULL CONSTRAINT CK_Pedidos_Total CHECK (Total >= 0),
    CONSTRAINT FK_Pedidos_Usuarios FOREIGN KEY (UsuarioID)
        REFERENCES Usuarios(UsuarioID)
        ON DELETE NO ACTION
);
GO

/* ---------------------------------------------------------
   7. PEDIDO_ITEMS
   Detalle de productos incluidos en cada pedido.
   --------------------------------------------------------- */
CREATE TABLE PedidoItems (
    PedidoItemID    INT IDENTITY(1,1) PRIMARY KEY,
    PedidoID        INT             NOT NULL,
    ProductoID      INT             NOT NULL,
    Cantidad        INT             NOT NULL CONSTRAINT CK_PedidoItems_Cantidad CHECK (Cantidad > 0),
    PrecioUnitario  DECIMAL(10,2)   NOT NULL,
    CONSTRAINT FK_PedidoItems_Pedidos FOREIGN KEY (PedidoID)
        REFERENCES Pedidos(PedidoID)
        ON DELETE CASCADE,
    CONSTRAINT FK_PedidoItems_Productos FOREIGN KEY (ProductoID)
        REFERENCES Productos(ProductoID)
        ON DELETE NO ACTION
);
GO

/* ---------------------------------------------------------
   8. PAGOS
   Un pago por pedido (evita cobros duplicados).
   --------------------------------------------------------- */
CREATE TABLE Pagos (
    PagoID          INT IDENTITY(1,1) PRIMARY KEY,
    PedidoID        INT             NOT NULL UNIQUE,
    Monto           DECIMAL(10,2)   NOT NULL CONSTRAINT CK_Pagos_Monto CHECK (Monto > 0),
    MetodoPago      VARCHAR(30)     NOT NULL
                        CONSTRAINT CK_Pagos_Metodo CHECK (MetodoPago IN ('TARJETA', 'PSE', 'CONTRAENTREGA')),
    Estado          VARCHAR(20)     NOT NULL DEFAULT 'APROBADO'
                        CONSTRAINT CK_Pagos_Estado CHECK (Estado IN ('APROBADO', 'RECHAZADO', 'PENDIENTE')),
    FechaPago       DATETIME2       NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Pagos_Pedidos FOREIGN KEY (PedidoID)
        REFERENCES Pedidos(PedidoID)
        ON DELETE CASCADE
);
GO

/* ---------------------------------------------------------
   9. FACTURAS
   Comprobante generado a partir de un pedido pagado.
   --------------------------------------------------------- */
CREATE TABLE Facturas (
    FacturaID       INT IDENTITY(1,1) PRIMARY KEY,
    PedidoID        INT             NOT NULL UNIQUE,
    NumeroFactura   VARCHAR(30)     NOT NULL UNIQUE,
    FechaEmision    DATETIME2       NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Facturas_Pedidos FOREIGN KEY (PedidoID)
        REFERENCES Pedidos(PedidoID)
        ON DELETE CASCADE
);
GO

/* ---------------------------------------------------------
   10. NOTIFICACIONES
   Confirmaciones y actualizaciones enviadas al cliente.
   --------------------------------------------------------- */
CREATE TABLE Notificaciones (
    NotificacionID  INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID       INT             NOT NULL,
    PedidoID        INT             NULL,
    Mensaje         NVARCHAR(300)   NOT NULL,
    Leida           BIT             NOT NULL DEFAULT 0,
    FechaEnvio      DATETIME2       NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Notificaciones_Usuarios FOREIGN KEY (UsuarioID)
        REFERENCES Usuarios(UsuarioID)
        ON DELETE CASCADE,
    CONSTRAINT FK_Notificaciones_Pedidos FOREIGN KEY (PedidoID)
        REFERENCES Pedidos(PedidoID)
        ON DELETE NO ACTION
);
GO
