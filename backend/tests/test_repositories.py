import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictoError, NoEncontradoError
from app.models import Pago, Pedido, Producto
from app.repositories import categoria_repository as cats
from app.repositories import producto_repository as prods
from app.repositories import usuario_repository as users
from app.schemas.categoria import CategoriaCreate
from app.schemas.producto import ProductoCreate, ProductoRead, ProductoUpdate


def nueva_categoria(db, nombre="Tecnología"):
    return cats.crear(db, CategoriaCreate(nombre=nombre))


def nuevo_producto(db, categoria_id, nombre="Mouse", precio="49900.00", stock=5, descripcion=None):
    return prods.crear(db, ProductoCreate(
        nombre=nombre, precio=precio, stock=stock, categoria_id=categoria_id, descripcion=descripcion))


class TestUsuarios:
    def test_crear_y_buscar(self, db):
        u = users.crear(db, "Ana", "Ana@Correo.com", "hash")
        assert u.UsuarioID and u.Rol == "CLIENTE" and u.FechaRegistro is not None
        assert u.Correo == "ana@correo.com"
        assert users.obtener_por_correo(db, " ANA@correo.COM ").UsuarioID == u.UsuarioID

    def test_correo_duplicado_ignora_mayusculas(self, db):
        users.crear(db, "Ana", "ana@correo.com", "hash")
        with pytest.raises(ConflictoError):
            users.crear(db, "Otra", "ANA@correo.com", "hash")

    def test_listar_paginado(self, db):
        for i in range(5):
            users.crear(db, f"U{i}", f"u{i}@correo.com", "h")
        assert [u.Nombre for u in users.listar(db, skip=1, limit=2)] == ["U1", "U2"]


class TestCategorias:
    def test_duplicada(self, db):
        nueva_categoria(db)
        with pytest.raises(ConflictoError):
            nueva_categoria(db)


class TestProductos:
    def test_crear_con_categoria_inexistente(self, db):
        with pytest.raises(NoEncontradoError):
            nuevo_producto(db, categoria_id=99)

    def test_crear_y_leer_con_categoria(self, db):
        cat = nueva_categoria(db)
        p = nuevo_producto(db, cat.CategoriaID, descripcion="Inalámbrico")
        salida = ProductoRead.model_validate(prods.obtener_por_id(db, p.ProductoID)).model_dump()
        assert salida["categoria"]["nombre"] == "Tecnología"
        assert str(salida["precio"]) == "49900.00" and salida["fecha_creacion"] is not None

    def test_filtros(self, db):
        t = nueva_categoria(db, "Tecnología")
        h = nueva_categoria(db, "Hogar")
        nuevo_producto(db, t.CategoriaID, "Teclado")
        nuevo_producto(db, t.CategoriaID, "Mouse")
        nuevo_producto(db, h.CategoriaID, "Cafetera")
        assert len(prods.listar(db)) == 3
        assert {p.Nombre for p in prods.listar(db, categoria_id=h.CategoriaID)} == {"Cafetera"}
        assert {p.Nombre for p in prods.listar(db, buscar="  tec ")} == {"Teclado"}

    def test_busqueda_trata_el_porcentaje_como_texto(self, db):
        c = nueva_categoria(db)
        nuevo_producto(db, c.CategoriaID, "Mouse")
        assert prods.listar(db, buscar="%") == []

    def test_actualizar_parcial(self, db):
        c = nueva_categoria(db)
        p = nuevo_producto(db, c.CategoriaID, stock=5)
        r = prods.actualizar(db, p.ProductoID, ProductoUpdate(stock=0))
        assert r.Stock == 0 and r.Nombre == "Mouse"

    def test_actualizar_inexistente_o_categoria_invalida(self, db):
        c = nueva_categoria(db)
        p = nuevo_producto(db, c.CategoriaID)
        with pytest.raises(NoEncontradoError):
            prods.actualizar(db, 999, ProductoUpdate(stock=1))
        with pytest.raises(NoEncontradoError):
            prods.actualizar(db, p.ProductoID, ProductoUpdate(categoria_id=999))

    def test_repositorio_no_confirma_la_transaccion(self, db):
        c = nueva_categoria(db)
        db.rollback()
        assert cats.obtener_por_id(db, c.CategoriaID) is None


class TestRestriccionesDeLaBase:
    """Las mismas reglas de schema.sql: aunque el código falle, la base protege los datos."""

    def test_stock_negativo(self, db):
        c = nueva_categoria(db)
        db.add(Producto(Nombre="X", Precio=10, Stock=-1, CategoriaID=c.CategoriaID))
        with pytest.raises(IntegrityError):
            db.flush()

    def test_clave_foranea(self, db):
        db.add(Producto(Nombre="X", Precio=10, Stock=1, CategoriaID=999))
        with pytest.raises(IntegrityError):
            db.flush()

    def test_un_solo_pago_por_pedido(self, db):
        u = users.crear(db, "Ana", "ana@correo.com", "h")
        ped = Pedido(UsuarioID=u.UsuarioID, Total=100)
        db.add(ped); db.flush()
        db.add(Pago(PedidoID=ped.PedidoID, Monto=100, MetodoPago="PSE")); db.flush()
        db.add(Pago(PedidoID=ped.PedidoID, Monto=100, MetodoPago="PSE"))
        with pytest.raises(IntegrityError):
            db.flush()

    def test_estado_de_pedido_invalido(self, db):
        u = users.crear(db, "Ana", "ana@correo.com", "h")
        db.add(Pedido(UsuarioID=u.UsuarioID, Total=100, Estado="INVENTADO"))
        with pytest.raises(IntegrityError):
            db.flush()
