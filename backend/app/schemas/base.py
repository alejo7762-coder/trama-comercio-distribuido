from pydantic import BaseModel, ConfigDict


class LecturaORM(BaseModel):
    """
    Base de los esquemas de salida. Permite construirlos directamente desde
    objetos ORM (cuyos atributos se llaman UsuarioID, Nombre, ...) mientras
    el JSON de la API usa nombres en snake_case (usuario_id, nombre, ...).
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
