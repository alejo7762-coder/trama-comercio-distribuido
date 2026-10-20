from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import confirmar, get_db
from app.dependencies import administrador_actual
from app.repositories import categoria_repository
from app.schemas.categoria import CategoriaCreate, CategoriaRead

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=list[CategoriaRead], summary="Listar categorías")
def listar_categorias(db: Session = Depends(get_db)):
    return categoria_repository.listar(db)


@router.post("", response_model=CategoriaRead, status_code=201, summary="Registrar una categoría")
def crear_categoria(datos: CategoriaCreate, _: object = Depends(administrador_actual), db: Session = Depends(get_db)):
    categoria = categoria_repository.crear(db, datos)
    confirmar(db)
    return categoria
