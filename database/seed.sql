/* =========================================================
   TRAMA — Datos iniciales de prueba
   Ejecutar DESPUÉS de schema.sql
   ========================================================= */

USE TramaDB;
GO

-- Usuarios
INSERT INTO Usuarios (Nombre, Correo, PasswordHash, Rol) VALUES
('Alejo Ramírez', 'alejo@correo.com', 'hash_pendiente_1', 'ADMIN'),
('Camila Sosa', 'camila@correo.com', 'hash_pendiente_2', 'CLIENTE'),
('Manuel Osorio', 'manuel@correo.com', 'hash_pendiente_3', 'CLIENTE');
GO

-- Categorías
INSERT INTO Categorias (Nombre) VALUES
('Tecnología'),
('Hogar'),
('Deportes');
GO

-- Productos
INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, CategoriaID) VALUES
('Audífonos Bluetooth', 'Audífonos inalámbricos con cancelación de ruido', 149900.00, 25, 1),
('Teclado Mecánico', 'Teclado mecánico retroiluminado', 189900.00, 15, 1),
('Cafetera Eléctrica', 'Cafetera de goteo 1.2L', 99900.00, 10, 2),
('Balón de Fútbol', 'Balón talla 5 profesional', 79900.00, 30, 3);
GO

-- Carrito de un usuario (Camila) con un producto agregado
INSERT INTO Carritos (UsuarioID) VALUES (2);
GO

INSERT INTO CarritoItems (CarritoID, ProductoID, Cantidad, PrecioUnitario) VALUES
(1, 1, 1, 149900.00);
GO

-- Pedido de prueba ya confirmado (Manuel)
INSERT INTO Pedidos (UsuarioID, Estado, Total) VALUES
(3, 'PAGADO', 189900.00);
GO

INSERT INTO PedidoItems (PedidoID, ProductoID, Cantidad, PrecioUnitario) VALUES
(1, 2, 1, 189900.00);
GO

-- Pago asociado al pedido de prueba
INSERT INTO Pagos (PedidoID, Monto, MetodoPago, Estado) VALUES
(1, 189900.00, 'TARJETA', 'APROBADO');
GO

-- Factura asociada al pedido de prueba
INSERT INTO Facturas (PedidoID, NumeroFactura) VALUES
(1, 'FAC-2026-0001');
GO

-- Notificación de confirmación
INSERT INTO Notificaciones (UsuarioID, PedidoID, Mensaje) VALUES
(3, 1, 'Tu pedido #1 ha sido confirmado y pagado exitosamente.');
GO
