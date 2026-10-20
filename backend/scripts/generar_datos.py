"""
Genera datos de demostración (catálogo, usuarios y pedidos) en TramaDB.

Uso (desde la carpeta backend, con el entorno virtual activado):
    python scripts/generar_datos.py --productos 1000 --usuarios 50 --pedidos 200

Los números son TOTALES DESEADOS: si la base ya tiene 4 productos y pide 1000, crea 996.
Ejecutarlo otra vez no agrega nada. Con la misma --semilla se obtienen los mismos datos.
Todo ocurre en una sola transacción: si algo falla, no se guarda nada.
Los usuarios generados llevan un hash de contraseña de marcador: no pueden iniciar sesión.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import func, select  # noqa: E402

from app import models  # noqa: E402
from app.datos_demo import generar  # noqa: E402

ENTIDADES = [("Categorías", models.Categoria), ("Productos", models.Producto), ("Usuarios", models.Usuario),
             ("Pedidos", models.Pedido), ("PedidoItems", models.PedidoItem), ("Pagos", models.Pago),
             ("Facturas", models.Factura), ("Notificaciones", models.Notificacion)]


def conteos(db):
    return {nombre: db.scalar(select(func.count()).select_from(m)) for nombre, m in ENTIDADES}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--productos", type=int, default=0, help="total deseado de productos")
    ap.add_argument("--usuarios", type=int, default=0, help="total deseado de usuarios")
    ap.add_argument("--pedidos", type=int, default=0, help="total deseado de pedidos")
    ap.add_argument("--semilla", type=int, default=2026, help="semilla para reproducir los mismos datos")
    args = ap.parse_args(argv)
    if min(args.productos, args.usuarios, args.pedidos) < 0 or max(args.productos, args.usuarios, args.pedidos) > 100_000:
        print("[FALLO] Los totales deben estar entre 0 y 100000.")
        return 1
    if not (args.productos or args.usuarios or args.pedidos):
        ap.print_help()
        return 1

    from app.database import SessionLocal
    with SessionLocal() as db:
        antes = conteos(db)
        try:
            nuevos = generar(db, args.productos, args.usuarios, args.pedidos, args.semilla)
            db.commit()
        except Exception as exc:  # noqa: BLE001
            db.rollback()
            print(f"[FALLO] No se guardó nada. {type(exc).__name__}: {str(exc)[:300]}")
            return 1
        despues = conteos(db)
    print(f"{'Tabla':<16}{'Antes':>10}{'Ahora':>10}")
    for nombre, _ in ENTIDADES:
        print(f"{nombre:<16}{antes[nombre]:>10}{despues[nombre]:>10}")
    print(f"\n[OK] Nuevos: {nuevos['productos']} productos, {nuevos['usuarios']} usuarios, {nuevos['pedidos']} pedidos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
