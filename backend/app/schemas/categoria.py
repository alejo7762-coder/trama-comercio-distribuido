from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.schemas.base import LecturaORM

NombreCategoria = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]


class CategoriaCreate(BaseModel):
    nombre: NombreCategoria


class CategoriaRead(LecturaORM):
    categoria_id: int = Field(validation_alias="CategoriaID")
    nombre: str = Field(validation_alias="Nombre")
