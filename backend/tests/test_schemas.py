from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.enums import Rol
from app.models import Usuario
from app.schemas.categoria import CategoriaCreate
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.schemas.usuario import UsuarioCreate, UsuarioRead


def producto_valido(**cambios):
    datos = dict(nombre="Mouse", precio="49900.00", stock=5, categoria_id=1)
    datos.update(cambios)
    return datos


class TestUsuario:
    def test_valido_y_recorta_nombre(self):
        u = UsuarioCreate(nombre="  Ana  ", correo="ana@correo.com", password="Clave1234")
        assert u.nombre == "Ana"

    def test_correo_invalido(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nombre="Ana", correo="no-es-correo", password="Clave1234")

    def test_password_corta(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nombre="Ana", correo="ana@correo.com", password="corta")

    def test_password_no_se_recorta_ni_se_muestra(self):
        u = UsuarioCreate(nombre="Ana", correo="ana@correo.com", password="  espacios  ")
        assert u.password == "  espacios  "
        assert "espacios" not in repr(u)

    def test_lectura_no_expone_hash(self):
        orm = Usuario(UsuarioID=1, Nombre="Ana", Correo="ana@correo.com",
                      PasswordHash="secreto", Rol="CLIENTE", FechaRegistro="2026-01-01T00:00:00")
        salida = UsuarioRead.model_validate(orm).model_dump()
        assert "password_hash" not in salida and "PasswordHash" not in salida
        assert salida["usuario_id"] == 1 and salida["rol"] == Rol.CLIENTE


class TestCategoria:
    def test_nombre_vacio(self):
        with pytest.raises(ValidationError):
            CategoriaCreate(nombre="   ")


class TestProducto:
    def test_valido(self):
        assert ProductoCreate(**producto_valido()).precio == Decimal("49900.00")

    @pytest.mark.parametrize("cambio", [
        {"precio": "0"}, {"precio": "-5"}, {"precio": "10.123"},
        {"precio": "123456789.00"}, {"stock": -1}, {"categoria_id": 0}, {"nombre": " "},
    ])
    def test_rechaza_datos_que_la_base_rechazaria(self, cambio):
        with pytest.raises(ValidationError):
            ProductoCreate(**producto_valido(**cambio))

    def test_update_vacio_no_permitido(self):
        with pytest.raises(ValidationError):
            ProductoUpdate()

    def test_update_no_permite_null_en_campos_obligatorios(self):
        with pytest.raises(ValidationError):
            ProductoUpdate(nombre=None)

    def test_update_permite_descripcion_null(self):
        u = ProductoUpdate(descripcion=None)
        assert u.model_dump(exclude_unset=True) == {"descripcion": None}
