from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select

from app.datos_demo import generar
from app.models import Categoria, Factura, Notificacion, Pago, Pedido, PedidoItem, Producto, Usuario

AHORA = datetime(2026, 10, 19, 12, 0, 0)


def contar(db, modelo):
    return db.scalar(select(func.count()).select_from(modelo))


def test_genera_los_totales_pedidos(db):
    r = generar(db, productos=300, usuarios=40, pedidos=120, ahora=AHORA)
    db.commit()
    assert r == {"productos": 300, "usuarios": 40, "pedidos": 120}
    assert (contar(db, Producto), contar(db, Usuario), contar(db, Pedido)) == (300, 40, 120)
    assert contar(db, Categoria) == 12


def test_es_idempotente_por_total_deseado(db):
    generar(db, productos=100, usuarios=10, pedidos=30, ahora=AHORA)
    db.commit()
    r = generar(db, productos=100, usuarios=10, pedidos=30, ahora=AHORA)
    assert r == {"productos": 0, "usuarios": 0, "pedidos": 0}
    r = generar(db, productos=150, ahora=AHORA)
    assert r["productos"] == 50 and contar(db, Producto) == 150


def test_cuenta_los_datos_que_ya_existian(db):
    db.add(Categoria(Nombre="Tecnología")); db.flush()
    db.add(Producto(Nombre="Teclado Mecánico", Precio=189900, Stock=15, CategoriaID=1)); db.flush()
    r = generar(db, productos=50, ahora=AHORA)
    assert r["productos"] == 49 and contar(db, Producto) == 50


def test_misma_semilla_mismos_datos(db):
    generar(db, productos=60, semilla=7, ahora=AHORA); db.flush()
    a = sorted(db.scalars(select(Producto.Nombre)))
    db.rollback()
    generar(db, productos=60, semilla=7, ahora=AHORA); db.flush()
    assert sorted(db.scalars(select(Producto.Nombre))) == a


def test_datos_respetan_las_reglas_de_negocio(db):
    generar(db, productos=200, usuarios=25, pedidos=150, ahora=AHORA)
    db.commit()
    nombres = list(db.scalars(select(Producto.Nombre)))
    assert len(nombres) == len(set(nombres))                      # nombres únicos
    assert all(p.Precio > 0 and p.Stock >= 0 for p in db.scalars(select(Producto)))
    for pedido in db.scalars(select(Pedido)):
        assert pedido.items and pedido.Total == sum(i.PrecioUnitario * i.Cantidad for i in pedido.items)
        pagado = pedido.Estado in ("PAGADO", "ENVIADO")
        assert (pedido.pago is not None) == pagado and (pedido.factura is not None) == pagado
        if pagado:
            assert pedido.pago.Monto == pedido.Total and pedido.pago.Estado == "APROBADO"
        assert pedido.FechaPedido <= AHORA
    facturas = list(db.scalars(select(Factura.NumeroFactura)))
    assert len(facturas) == len(set(facturas))
    assert contar(db, Notificacion) == 150


def test_no_crea_pedidos_sin_clientes_o_productos(db):
    assert generar(db, pedidos=10, ahora=AHORA)["pedidos"] == 0
