"""Los errores de negocio se traducen a respuestas HTTP correctas."""

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.exceptions import ConflictoError, NoEncontradoError
from app.main import app

router = APIRouter()


@router.get("/_prueba/no-encontrado")
def _a():
    raise NoEncontradoError("no existe")


@router.get("/_prueba/conflicto")
def _b():
    raise ConflictoError("ya existe")


app.include_router(router)
client = TestClient(app)


def test_404():
    r = client.get("/_prueba/no-encontrado")
    assert r.status_code == 404 and r.json() == {"detail": "no existe"}


def test_409():
    r = client.get("/_prueba/conflicto")
    assert r.status_code == 409 and r.json() == {"detail": "ya existe"}
