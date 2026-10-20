"""
Pruebas de la API de catálogo de extremo a extremo (HTTP -> routers -> repositorios -> base).
Usan SQLite en memoria; cada solicitud obtiene una sesión nueva, como en producción, de modo
que también se comprueba que los datos realmente se confirman (commit).
"""

import pytest
import os
from types import SimpleNamespace
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.dependencies import administrador_actual


@pytest.fixture()
def client():
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-that-is-at-least-32-characters-long"
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, _):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    fabrica = sessionmaker(bind=engine, autoflush=False)

    def _get_db():
        sesion = fabrica()
        try:
            yield sesion
        finally:
            sesion.close()

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[administrador_actual] = lambda: SimpleNamespace(Rol="ADMIN")
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()


def crear_categoria(client, nombre="Tecnología"):
    r = client.post("/categorias", json={"nombre": nombre})
    assert r.status_code == 201, r.text
    return r.json()["categoria_id"]


def producto(cid, **cambios):
    datos = {"nombre": "Teclado", "descripcion": "Mecánico", "precio": "189900.00",
             "stock": 15, "categoria_id": cid}
    datos.update(cambios)
    return datos


class TestCategorias:
    def test_crear_y_listar(self, client):
        assert client.get("/categorias").json() == []
        crear_categoria(client, "Hogar")
        assert [c["nombre"] for c in client.get("/categorias").json()] == ["Hogar"]

    def test_duplicada_409(self, client):
        crear_categoria(client)
        r = client.post("/categorias", json={"nombre": "Tecnología"})
        assert r.status_code == 409


class TestProductos:
    def test_registrar_y_consultar(self, client):
        cid = crear_categoria(client)
        r = client.post("/productos", json=producto(cid))
        assert r.status_code == 201
        creado = r.json()
        assert creado["precio"] == "189900.00" and creado["categoria"]["nombre"] == "Tecnología"
        assert "password" not in r.text.lower()
        # El dato quedó confirmado: otra solicitud (otra sesión) lo ve.
        leido = client.get(f"/productos/{creado['producto_id']}").json()
        assert leido["nombre"] == "Teclado" and leido["stock"] == 15

    def test_acentos_y_enie(self, client):
        cid = crear_categoria(client)
        client.post("/productos", json=producto(cid, nombre="Cafetera ñandú", descripcion="Descripción con tilde"))
        assert client.get("/productos").json()[0]["nombre"] == "Cafetera ñandú"

    @pytest.mark.parametrize("cambio", [
        {"precio": "0"}, {"precio": "-1"}, {"precio": "10.999"}, {"stock": -1},
        {"nombre": "   "}, {"nombre": "x" * 151}, {"categoria_id": 0},
    ])
    def test_datos_invalidos_422(self, client, cambio):
        cid = crear_categoria(client)
        r = client.post("/productos", json=producto(cid, **cambio))
        assert r.status_code == 422
        assert client.get("/productos").json() == []  # no se guardó nada

    def test_categoria_inexistente_404(self, client):
        assert client.post("/productos", json=producto(999)).status_code == 404

    def test_filtros(self, client):
        t, h = crear_categoria(client, "Tecnología"), crear_categoria(client, "Hogar")
        client.post("/productos", json=producto(t, nombre="Teclado"))
        client.post("/productos", json=producto(t, nombre="Mouse"))
        client.post("/productos", json=producto(h, nombre="Cafetera"))
        assert len(client.get("/productos").json()) == 3
        assert [p["nombre"] for p in client.get(f"/productos?categoria_id={h}").json()] == ["Cafetera"]
        assert [p["nombre"] for p in client.get("/productos?buscar=tecl").json()] == ["Teclado"]
        assert client.get("/productos?buscar=%25").json() == []

    def test_parametros_invalidos(self, client):
        assert client.get("/productos?limit=0").status_code == 422
        assert client.get("/productos?limit=1000").status_code == 422
        assert client.get("/productos/abc").status_code == 422
        assert client.get("/productos/999").status_code == 404

    def test_actualizar_parcial(self, client):
        pid = client.post("/productos", json=producto(crear_categoria(client))).json()["producto_id"]
        r = client.patch(f"/productos/{pid}", json={"stock": 3})
        assert r.status_code == 200 and r.json()["stock"] == 3 and r.json()["nombre"] == "Teclado"
        assert client.patch(f"/productos/{pid}", json={}).status_code == 422
        assert client.patch(f"/productos/{pid}", json={"nombre": None}).status_code == 422
        assert client.patch("/productos/999", json={"stock": 1}).status_code == 404

    def test_html_no_se_interpreta_en_la_api(self, client):
        cid = crear_categoria(client)
        client.post("/productos", json=producto(cid, nombre="<script>alert(1)</script>"))
        assert client.get("/productos").json()[0]["nombre"] == "<script>alert(1)</script>"


class TestInterfazWeb:
    @pytest.mark.parametrize("ruta", ["/app/", "/app/catalogo.html", "/app/admin.html",
                                      "/app/js/api.js", "/app/js/catalogo.js", "/app/js/admin.js",
                                      "/app/css/estilos.css"])
    def test_archivos_estaticos_servidos(self, client, ruta):
        assert client.get(ruta).status_code == 200

    def test_raiz_redirige_a_la_interfaz(self, client):
        r = client.get("/", follow_redirects=False)
        assert r.status_code in (302, 307) and r.headers["location"] == "/app/"


class TestComercio:
    def test_registro_login_carrito_checkout_y_stock(self, client, monkeypatch):
        import app.routers.pedidos as modulo_pedidos
        monkeypatch.setattr(modulo_pedidos, "enviar_confirmacion", lambda *args: True)
        registro = client.post("/auth/register", json={
            "nombre": "Cliente Prueba",
            "correo": "cliente.prueba@example.com",
            "password": "UnaClaveSegura123!",
            "telefono": "3001234567",
            "direccion": "Calle 10 # 20-30",
        })
        assert registro.status_code == 201, registro.text
        token = registro.json()["access_token"]
        headers = {"Authorization": "Bearer " + token}
        assert registro.json()["usuario"]["rol"] == "CLIENTE"

        login = client.post("/auth/login", json={
            "correo": "cliente.prueba@example.com",
            "password": "UnaClaveSegura123!",
        })
        assert login.status_code == 200
        assert client.post("/auth/login", json={
            "correo": "cliente.prueba@example.com",
            "password": "incorrecta",
        }).status_code == 401

        cid = crear_categoria(client, "Hogar")
        creado = client.post("/productos", json=producto(cid, nombre="Lámpara", precio="50000.00", stock=4))
        assert creado.status_code == 201, creado.text
        pid = creado.json()["producto_id"]

        agregado = client.post("/carrito/items", json={"producto_id": pid, "cantidad": 2}, headers=headers)
        assert agregado.status_code == 201, agregado.text
        assert agregado.json()["items"][0]["cantidad"] == 2
        assert agregado.json()["total"] == "100000.00"

        pedido = client.post("/pedidos/checkout", json={
            "direccion_envio": "Carrera 7 # 10-20",
            "telefono_contacto": "3007654321",
            "metodo_pago": "CONTRAENTREGA",
        }, headers=headers)
        assert pedido.status_code == 201, pedido.text
        datos = pedido.json()
        assert datos["total"] == "100000.00"
        assert datos["email_enviado"] is True
        assert datos["items"][0]["cantidad"] == 2

        productos = client.get("/productos").json()
        lampara = next(p for p in productos if p["producto_id"] == pid)
        assert lampara["stock"] == 2
        carrito = client.get("/carrito", headers=headers)
        assert carrito.status_code == 200 and carrito.json()["items"] == []
        historial = client.get("/pedidos/mis-pedidos", headers=headers)
        assert historial.status_code == 200 and len(historial.json()) == 1

    def test_registro_rechaza_correo_duplicado(self, client):
        datos = {
            "nombre": "Cliente Prueba",
            "correo": "duplicado@example.com",
            "password": "UnaClaveSegura123!",
            "telefono": "3001234567",
            "direccion": "Calle 10 # 20-30",
        }
        assert client.post("/auth/register", json=datos).status_code == 201
        assert client.post("/auth/register", json=datos).status_code == 409

    def test_checkout_rechaza_stock_insuficiente_sin_descontar(self, client):
        registro = client.post("/auth/register", json={
            "nombre": "Cliente Stock",
            "correo": "stock@example.com",
            "password": "UnaClaveSegura123!",
            "telefono": "3001234567",
            "direccion": "Calle 10 # 20-30",
        })
        headers = {"Authorization": "Bearer " + registro.json()["access_token"]}
        cid = crear_categoria(client, "Deportes")
        creado = client.post("/productos", json=producto(cid, nombre="Balón", precio="80000.00", stock=1))
        pid = creado.json()["producto_id"]
        assert client.post("/carrito/items", json={"producto_id": pid, "cantidad": 1}, headers=headers).status_code == 201
        # Simula que otra compra agotó el inventario antes de confirmar este carrito.
        assert client.patch(f"/productos/{pid}", json={"stock": 0}).status_code == 200
        pedido = client.post("/pedidos/checkout", json={
            "direccion_envio": "Carrera 7 # 10-20",
            "telefono_contacto": "3007654321",
            "metodo_pago": "CONTRAENTREGA",
        }, headers=headers)
        assert pedido.status_code == 409
        assert client.get("/productos").json()[0]["stock"] == 0
