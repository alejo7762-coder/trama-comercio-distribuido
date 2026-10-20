/* Ejecutar una sola vez en TramaDB existente. Para una BD nueva, usar schema.sql actualizado. */
USE TramaDB;
GO
IF COL_LENGTH('dbo.Usuarios','Telefono') IS NULL
    ALTER TABLE dbo.Usuarios ADD Telefono NVARCHAR(30) NOT NULL CONSTRAINT DF_Usuarios_Telefono DEFAULT '';
GO
IF COL_LENGTH('dbo.Usuarios','Direccion') IS NULL
    ALTER TABLE dbo.Usuarios ADD Direccion NVARCHAR(300) NOT NULL CONSTRAINT DF_Usuarios_Direccion DEFAULT '';
GO
IF COL_LENGTH('dbo.Pedidos','DireccionEnvio') IS NULL
    ALTER TABLE dbo.Pedidos ADD DireccionEnvio NVARCHAR(300) NOT NULL CONSTRAINT DF_Pedidos_DireccionEnvio DEFAULT '';
GO
IF COL_LENGTH('dbo.Pedidos','TelefonoContacto') IS NULL
    ALTER TABLE dbo.Pedidos ADD TelefonoContacto NVARCHAR(30) NOT NULL CONSTRAINT DF_Pedidos_TelefonoContacto DEFAULT '';
GO
IF COL_LENGTH('dbo.Productos','Activo') IS NULL
    ALTER TABLE dbo.Productos ADD Activo BIT NOT NULL CONSTRAINT DF_Productos_Activo DEFAULT 1;
GO
