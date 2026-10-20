"""
Verifica los modelos, esquemas y repositorios contra la base de datos real.

Uso (desde la carpeta backend, con el entorno virtual activado):
    python scripts/check_models.py

NO deja datos: las escrituras de prueba se hacen dentro de una transacción
que siempre se deshace (rollback). Nunca ejecuta commit.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import func, select  # noqa: E402
from sqlalchemy.exc import IntegrityError  # noqa: E402

from app import models  # noqa: E402
from app.repositories import categoria_repository, producto_repository  # noqa: E402
from app.schemas.categoria import CategoriaCreate  # noqa: E402
from app.schemas.producto import ProductoCreate, ProductoRead  # noqa: E402

ENTIDADES = [models.Usuario, models.Categoria, models.Producto, models.Carrito, models.CarritoItem,
             models.Pedido, models.PedidoItem, models.Pago, models.Factura, models.Notificacion]


class Resultado:
    def __init__(self):
        self.fallos = 0

    def ok(self, msg):
        print(f"[OK]    {msg}")

    def fallo(self, msg):
        self.fallos += 1
        print(f"[FALLO] {msg}")

    def comprobar(self, condicion, msg_ok, msg_fallo):
        (self.ok if condicion else self.fallo)(msg_ok if condicion else msg_fallo)


def verificar(session_factory) -> int:
    r = Resultado()

    # 1. Lectura de las 10 entidades con el ORM
    print("--- 1. Lectura de entidades ---")
    with session_factory() as db:
        for modelo in ENTIDADES:
            try:
                n = db.scalar(select(func.count()).select_from(modelo))
                r.ok(f"{modelo.__tablename__}: {n} fila(s)")
            except Exception as e:  # noqa: BLE001
                r.fallo(f"{modelo.__tablename__}: {type(e).__name__}: {str(e)[:150]}")
                db.rollback()

    # 2. Relaciones entre entidades
    print("--- 2. Relaciones ---")
    with session_factory() as db:
        prod = producto_repository.listar(db, limit=1)
        r.comprobar(prod and prod[0].categoria is not None,
                    f"Producto -> Categoría: '{prod[0].Nombre}' pertenece a '{prod[0].categoria.Nombre}'"
                    if prod and prod[0].categoria else "",
                    "No se pudo leer un producto con su categoría")
        if prod:
            salida = ProductoRead.model_validate(prod[0]).model_dump()
            r.comprobar(salida["categoria"] is not None and "precio" in salida,
                        f"Esquema ProductoRead: precio={salida['precio']}, categoría='{salida['categoria']['nombre']}'"
                        if salida["categoria"] else "",
                        "ProductoRead no pudo construirse desde el modelo")
        pedido = db.scalar(select(models.Pedido).limit(1))
        if pedido:
            r.comprobar(len(pedido.items) >= 1 and pedido.pago is not None and pedido.factura is not None,
                        f"Pedido #{pedido.PedidoID}: {len(pedido.items)} ítem(s), pago {pedido.pago.Estado}, "
                        f"factura {pedido.factura.NumeroFactura}" if pedido.pago and pedido.factura else "",
                        f"Pedido #{pedido.PedidoID} no tiene ítems, pago o factura asociados")
        else:
            print("[AVISO] No hay pedidos de prueba; ejecute database/seed.sql")
        carrito = db.scalar(select(models.Carrito).limit(1))
        if carrito:
            r.comprobar(len(carrito.items) >= 1,
                        f"Carrito #{carrito.CarritoID}: {len(carrito.items)} ítem(s)",
                        "El carrito no tiene ítems")

    # 3. Escritura con los repositorios, siempre deshecha
    print("--- 3. Escritura reversible (rollback) ---")
    marca = "_prueba_fase3_"
    with session_factory() as db:
        try:
            cat = categoria_repository.crear(db, CategoriaCreate(nombre=marca))
            p = producto_repository.crear(db, ProductoCreate(
                nombre=marca + "producto", descripcion="Descripción con tilde: ñandú",
                precio="1234.50", stock=3, categoria_id=cat.CategoriaID))
            r.comprobar(p.ProductoID and p.FechaCreacion is not None,
                        f"Repositorios: categoría #{cat.CategoriaID} y producto #{p.ProductoID} creados (aún sin confirmar)",
                        "El producto no recibió ID o fecha de la base de datos")
            leido = producto_repository.obtener_por_id(db, p.ProductoID)
            r.comprobar(leido.Descripcion == "Descripción con tilde: ñandú",
                        "Las tildes y la ñ se guardan y leen correctamente",
                        f"Texto alterado al guardar: {leido.Descripcion!r}")
        except Exception as e:  # noqa: BLE001
            r.fallo(f"Error en repositorios: {type(e).__name__}: {str(e)[:200]}")
        finally:
            db.rollback()
    with session_factory() as db:
        quedan = db.scalar(select(func.count()).select_from(models.Categoria)
                           .where(models.Categoria.Nombre == marca))
        r.comprobar(quedan == 0, "Rollback correcto: no quedó ningún dato de prueba",
                    "QUEDARON DATOS DE PRUEBA en la base; elimine la categoría '_prueba_fase3_'")

    # 4. La base debe rechazar datos inválidos
    print("--- 4. Restricciones de la base de datos ---")
    with session_factory() as db:
        cat = db.scalar(select(models.Categoria).limit(1))
        if cat:
            db.add(models.Producto(Nombre=marca, Precio=10, Stock=-1, CategoriaID=cat.CategoriaID))
            try:
                db.flush()
                r.fallo("La base ACEPTÓ un stock negativo")
            except IntegrityError:
                r.ok("Stock negativo rechazado (CK_Productos_Stock)")
            finally:
                db.rollback()
    with session_factory() as db:
        pago = db.scalar(select(models.Pago).limit(1))
        if pago:
            db.add(models.Pago(PedidoID=pago.PedidoID, Monto=100, MetodoPago="PSE"))
            try:
                db.flush()
                r.fallo("La base ACEPTÓ un segundo pago para el mismo pedido")
            except IntegrityError:
                r.ok("Segundo pago para el mismo pedido rechazado (UNIQUE)")
            finally:
                db.rollback()

    print()
    if r.fallos:
        print(f"Resultado: {r.fallos} comprobación(es) fallida(s).")
        return 1
    print("Resultado: capa de datos verificada.")
    return 0


if __name__ == "__main__":
    from app.database import SessionLocal
    sys.exit(verificar(SessionLocal))
