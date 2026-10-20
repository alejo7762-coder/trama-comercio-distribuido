"""
Pruebas de la API de catálogo de extremo a extremo (HTTP -> routers -> repositorios -> base).
Usan SQLite en memoria; cada solicitud obtiene una sesión nueva, como en producción, de modo
que también se comprueba que los datos realmente se confirman (commit).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
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
                                      "/app/js/inicio.js", "/app/css/estilos.css",
                                      "/app/img/logo-web.png", "/app/img/logo-icono.png", "/app/img/favicon.png"])
    def test_archivos_estaticos_servidos(self, client, ruta):
        assert client.get(ruta).status_code == 200

    def test_raiz_redirige_a_la_interfaz(self, client):
        r = client.get("/", follow_redirects=False)
        assert r.status_code in (302, 307) and r.headers["location"] == "/app/"
