/* =========================================================
   TRAMA — Migración 001: índices para consultas con muchos datos
   Repetible: crea cada índice solo si no existe. No modifica datos.

   SQL Server no crea índices automáticamente sobre las claves foráneas.
   Estos índices aceleran el filtro por categoría, la búsqueda por nombre,
   el historial de pedidos de un usuario y las uniones de ítems.
   ========================================================= */

USE TramaDB;
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Productos_CategoriaID' AND object_id = OBJECT_ID('dbo.Productos'))
    CREATE INDEX IX_Productos_CategoriaID ON dbo.Productos (CategoriaID);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Productos_Nombre' AND object_id = OBJECT_ID('dbo.Productos'))
    CREATE INDEX IX_Productos_Nombre ON dbo.Productos (Nombre);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Pedidos_UsuarioID' AND object_id = OBJECT_ID('dbo.Pedidos'))
    CREATE INDEX IX_Pedidos_UsuarioID ON dbo.Pedidos (UsuarioID, FechaPedido);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Pedidos_FechaPedido' AND object_id = OBJECT_ID('dbo.Pedidos'))
    CREATE INDEX IX_Pedidos_FechaPedido ON dbo.Pedidos (FechaPedido) INCLUDE (Estado, Total);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_PedidoItems_PedidoID' AND object_id = OBJECT_ID('dbo.PedidoItems'))
    CREATE INDEX IX_PedidoItems_PedidoID ON dbo.PedidoItems (PedidoID);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_PedidoItems_ProductoID' AND object_id = OBJECT_ID('dbo.PedidoItems'))
    CREATE INDEX IX_PedidoItems_ProductoID ON dbo.PedidoItems (ProductoID);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_CarritoItems_ProductoID' AND object_id = OBJECT_ID('dbo.CarritoItems'))
    CREATE INDEX IX_CarritoItems_ProductoID ON dbo.CarritoItems (ProductoID);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Notificaciones_UsuarioID' AND object_id = OBJECT_ID('dbo.Notificaciones'))
    CREATE INDEX IX_Notificaciones_UsuarioID ON dbo.Notificaciones (UsuarioID, Leida);
GO
