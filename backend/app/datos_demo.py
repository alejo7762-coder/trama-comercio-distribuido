"""
Generador de datos de demostración para Trama.

Crea catálogo, usuarios y pedidos históricos con datos sintéticos (marcas ficticias,
nombres comunes colombianos) respetando todas las restricciones de la base de datos.

Es idempotente por "total deseado": generar(productos=1000) deja la base con 1000
productos en total, cuente los que ya existían; ejecutarlo de nuevo no agrega nada.
Con la misma semilla produce siempre los mismos datos.

No hace commit: quien lo invoca confirma o deshace la transacción.
"""

import random
import unicodedata
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Categoria, Factura, Notificacion, Pago, Pedido, PedidoItem, Producto, Usuario,
)

# categoría -> (rango de precios en COP, tipos de producto, marcas ficticias, usos)
CATALOGO = {
    "Tecnología": ((39_900, 3_499_900), ["Audífonos Bluetooth", "Teclado Mecánico", "Mouse Inalámbrico", "Monitor LED", "Cargador Rápido", "Parlante Portátil", "Cámara Web", "Disco Duro Externo", "Smartwatch", "Router WiFi"],
                   ["Nova", "Kyma", "Orbita", "Lumen", "Zenit", "Tera"], ["trabajar desde casa", "estudiar", "jugar", "viajar"]),
    "Hogar": ((14_900, 1_299_900), ["Lámpara de Mesa", "Juego de Sábanas", "Cojín Decorativo", "Organizador", "Espejo de Pared", "Cortina Blackout", "Tapete", "Reloj de Pared"],
              ["Casaviva", "Hogarte", "Nido", "Brisa", "Andina"], ["la sala", "el dormitorio", "el comedor", "el estudio"]),
    "Cocina": ((12_900, 899_900), ["Cafetera Eléctrica", "Licuadora", "Sartén Antiadherente", "Juego de Cuchillos", "Olla a Presión", "Tostadora", "Freidora de Aire", "Set de Tuppers"],
               ["Sabora", "Chefio", "Fogón", "Delicia", "Cumbre"], ["el desayuno", "el almuerzo", "reuniones familiares", "preparar a diario"]),
    "Deportes": ((19_900, 1_199_900), ["Balón de Fútbol", "Guantes de Gimnasio", "Pesas Ajustables", "Colchoneta de Yoga", "Bicicleta Estática", "Cuerda para Saltar", "Botella Deportiva", "Maleta Deportiva"],
                 ["Vigor", "Ritmo", "Atleta", "Ímpetu", "Cima"], ["entrenar en casa", "salir a correr", "el gimnasio", "el fin de semana"]),
    "Moda": ((24_900, 699_900), ["Camiseta Algodón", "Jean Clásico", "Chaqueta Impermeable", "Tenis Urbanos", "Gorra", "Bolso de Mano", "Reloj Casual", "Gafas de Sol"],
             ["Trama Urbana", "Estilo Sur", "Alba", "Marea", "Cruz del Sur"], ["todos los días", "la oficina", "salir de noche", "viajar"]),
    "Belleza": ((9_900, 349_900), ["Crema Hidratante", "Perfume", "Set de Brochas", "Shampoo Reparador", "Mascarilla Facial", "Secador de Cabello", "Plancha de Cabello", "Protector Solar"],
                ["Aura", "Petalia", "Lúmina", "Esencia", "Brillo"], ["el cuidado diario", "regalar", "pieles sensibles", "el cabello seco"]),
    "Juguetes": ((14_900, 599_900), ["Bloques de Construcción", "Muñeca Articulada", "Carro a Control Remoto", "Rompecabezas", "Peluche Gigante", "Juego de Mesa", "Set de Pintura", "Pista de Carros"],
                 ["Chispa", "Pequeño Mundo", "Fantasía", "Aventura", "Arcoíris"], ["niños de 3 a 6 años", "jugar en familia", "regalar", "aprender jugando"]),
    "Libros": ((19_900, 189_900), ["Novela Contemporánea", "Manual de Programación", "Libro de Cocina", "Atlas Ilustrado", "Cuentos Infantiles", "Biografía", "Ensayo de Historia", "Guía de Viaje"],
               ["Editorial Aurora", "Ediciones Faro", "Letra Viva", "Páginas del Sur", "Tinta Nueva"], ["leer en vacaciones", "regalar", "estudiar", "coleccionar"]),
    "Mascotas": ((9_900, 459_900), ["Alimento para Perro", "Cama para Mascota", "Rascador para Gato", "Correa Extensible", "Juguete Mordedor", "Arenero", "Transportadora", "Comedero Automático"],
                 ["Huellitas", "Patitas", "Amigo Fiel", "Mimo", "Colita"], ["perros medianos", "gatos", "cachorros", "mascotas activas"]),
    "Oficina": ((7_900, 1_499_900), ["Silla Ergonómica", "Escritorio", "Lapicero Gel", "Agenda", "Archivador", "Lámpara LED de Escritorio", "Calculadora", "Resma de Papel"],
                ["Prisma", "Gestión", "Norte", "Ofitec", "Línea Recta"], ["la oficina", "teletrabajo", "estudiar", "organizar documentos"]),
    "Salud": ((8_900, 399_900), ["Termómetro Digital", "Tensiómetro", "Vitaminas", "Botiquín", "Masajeador", "Oxímetro", "Pastillero Semanal", "Báscula Digital"],
              ["Vital", "Sanitas Plus", "Equilibrio", "Salud Total", "Armonía"], ["el cuidado en casa", "adultos mayores", "el bienestar diario", "viajar"]),
    "Ferretería": ((6_900, 899_900), ["Taladro Inalámbrico", "Juego de Destornilladores", "Cinta Métrica", "Caja de Herramientas", "Escalera Plegable", "Martillo", "Nivel Láser", "Set de Brocas"],
                   ["Forja", "Titán", "Obra Firme", "Maestro", "Yunque"], ["reparaciones del hogar", "proyectos de bricolaje", "talleres", "obra"]),
}

NOMBRES = ["Camila", "Santiago", "Valentina", "Mateo", "Sofía", "Samuel", "Isabella", "Sebastián", "Mariana", "Daniel", "Luciana", "Nicolás",
           "Gabriela", "Andrés", "Juliana", "Felipe", "Daniela", "Alejandro", "Paula", "Julián", "Laura", "Esteban", "Natalia", "Tomás", "Carolina", "David", "Manuela", "Simón", "Andrea", "Emilio"]
APELLIDOS = ["Gómez", "Rodríguez", "Martínez", "López", "García", "Hernández", "Díaz", "Pérez", "Sánchez", "Ramírez", "Torres", "Flórez", "Vargas", "Castro", "Rojas",
             "Moreno", "Jiménez", "Ortiz", "Gutiérrez", "Cárdenas", "Mejía", "Osorio", "Restrepo", "Arias", "Salazar", "Medina", "Cano", "Bedoya", "Quintero", "Zapata"]
METODOS = ["TARJETA", "PSE", "CONTRAENTREGA"]


def _sin_tildes(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower().replace(" ", "")


def _contar(db: Session, modelo) -> int:
    return db.scalar(select(func.count()).select_from(modelo)) or 0


def _asegurar_categorias(db: Session) -> dict:
    existentes = {c.Nombre: c.CategoriaID for c in db.scalars(select(Categoria))}
    for nombre in CATALOGO:
        if nombre not in existentes:
            c = Categoria(Nombre=nombre)
            db.add(c)
            db.flush()
            existentes[nombre] = c.CategoriaID
    return existentes


def _crear_productos(db: Session, total_deseado: int, semilla: int) -> int:
    necesarios = total_deseado - _contar(db, Producto)
    if necesarios <= 0:
        return 0
    categorias = _asegurar_categorias(db)
    nombres_usados = set(db.scalars(select(Producto.Nombre)))
    rng = random.Random(semilla)
    nombres_categoria = list(CATALOGO)
    creados, lote = 0, []
    while creados < necesarios:
        categoria = rng.choice(nombres_categoria)
        (minimo, maximo), tipos, marcas, usos = CATALOGO[categoria]
        tipo, marca = rng.choice(tipos), rng.choice(marcas)
        codigo = f"{rng.choice('ABCDEFGHJKLMNPRSTVXZ')}{rng.randint(100, 999)}"
        nombre = f"{tipo} {marca} {codigo}"
        precio = round((minimo + (maximo - minimo) * rng.random() ** 2) / 100) * 100
        stock = 0 if rng.random() < 0.05 else rng.randint(1, 150)
        uso = rng.choice(usos)
        if nombre in nombres_usados:
            continue
        nombres_usados.add(nombre)
        lote.append(Producto(
            Nombre=nombre,
            Descripcion=f"{tipo} de la línea {marca}, pensado para {uso}.",
            Precio=Decimal(precio).quantize(Decimal("0.01")),
            Stock=stock,
            CategoriaID=categorias[categoria],
        ))
        creados += 1
        if len(lote) >= 500:
            db.add_all(lote); db.flush(); lote = []
    if lote:
        db.add_all(lote); db.flush()
    return creados


def _crear_usuarios(db: Session, total_deseado: int, semilla: int) -> int:
    necesarios = total_deseado - _contar(db, Usuario)
    if necesarios <= 0:
        return 0
    correos = set(db.scalars(select(Usuario.Correo)))
    rng = random.Random(semilla + 1)
    creados, lote, intento = 0, [], 0
    while creados < necesarios:
        intento += 1
        nombre, ap1, ap2 = rng.choice(NOMBRES), rng.choice(APELLIDOS), rng.choice(APELLIDOS)
        correo = f"{_sin_tildes(nombre)}.{_sin_tildes(ap1)}{intento}@correo.com"
        if correo in correos:
            continue
        correos.add(correo)
        lote.append(Usuario(Nombre=f"{nombre} {ap1} {ap2}", Correo=correo,
                            PasswordHash="hash_pendiente_demo", Rol="CLIENTE"))
        creados += 1
        if len(lote) >= 500:
            db.add_all(lote); db.flush(); lote = []
    if lote:
        db.add_all(lote); db.flush()
    return creados


def _crear_pedidos(db: Session, total_deseado: int, semilla: int, ahora: datetime) -> int:
    necesarios = total_deseado - _contar(db, Pedido)
    if necesarios <= 0:
        return 0
    productos = [(p.ProductoID, p.Precio) for p in db.execute(select(Producto.ProductoID, Producto.Precio))]
    clientes = list(db.scalars(select(Usuario.UsuarioID).where(Usuario.Rol == "CLIENTE")))
    if not productos or not clientes:
        return 0
    ultima = db.scalar(select(func.max(Factura.NumeroFactura)).where(Factura.NumeroFactura.like("FAC-GEN-%")))
    secuencia = int(ultima.split("-")[-1]) if ultima else 0
    rng = random.Random(semilla + 2)
    lote = []
    for _ in range(necesarios):
        cliente = rng.choice(clientes)
        fecha = (ahora - timedelta(days=rng.randint(0, 180), minutes=rng.randint(0, 1439))).replace(microsecond=0)
        sorteo = rng.random()
        estado = "PAGADO" if sorteo < 0.80 else "ENVIADO" if sorteo < 0.90 else "PENDIENTE" if sorteo < 0.95 else "CANCELADO"
        items, total = [], Decimal("0.00")
        for pid, precio in rng.sample(productos, k=min(rng.randint(1, 4), len(productos))):
            cantidad = rng.randint(1, 3)
            items.append(PedidoItem(ProductoID=pid, Cantidad=cantidad, PrecioUnitario=precio))
            total += precio * cantidad
        pedido = Pedido(UsuarioID=cliente, FechaPedido=fecha, Estado=estado, Total=total, items=items)
        if estado in ("PAGADO", "ENVIADO"):
            secuencia += 1
            fecha_pago = fecha + timedelta(minutes=rng.randint(1, 30))
            pedido.pago = Pago(Monto=total, MetodoPago=rng.choice(METODOS), Estado="APROBADO", FechaPago=fecha_pago)
            pedido.factura = Factura(NumeroFactura=f"FAC-GEN-{secuencia:06d}", FechaEmision=fecha_pago)
            texto = "Tu pedido fue confirmado y pagado exitosamente." if estado == "PAGADO" else "Tu pedido fue despachado y va en camino."
        else:
            texto = "Tu pedido está pendiente de pago." if estado == "PENDIENTE" else "Tu pedido fue cancelado."
        pedido.notificaciones = [Notificacion(UsuarioID=cliente, Mensaje=texto, Leida=rng.random() < 0.7,
                                              FechaEnvio=fecha + timedelta(minutes=rng.randint(1, 40)))]
        lote.append(pedido)
        if len(lote) >= 200:
            db.add_all(lote); db.flush(); lote = []
    if lote:
        db.add_all(lote); db.flush()
    return necesarios


def generar(db: Session, productos: int = 0, usuarios: int = 0, pedidos: int = 0,
            semilla: int = 2026, ahora: datetime | None = None) -> dict:
    """
    Deja la base con al menos `productos`, `usuarios` y `pedidos` en total.
    Devuelve cuántos registros nuevos creó de cada tipo.
    """
    ahora = ahora or datetime.now()
    resultado = {"productos": _crear_productos(db, productos, semilla)}
    resultado["usuarios"] = _crear_usuarios(db, usuarios, semilla)
    resultado["pedidos"] = _crear_pedidos(db, pedidos, semilla, ahora)
    return resultado
