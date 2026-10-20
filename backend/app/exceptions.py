"""
Excepciones de negocio. Las capas de datos y de servicios las lanzan y
main.py las traduce a respuestas HTTP, de modo que los repositorios no
dependen de FastAPI.
"""


class TramaError(Exception):
    """Base de las excepciones de negocio de Trama."""


class NoEncontradoError(TramaError):
    """El recurso solicitado no existe (HTTP 404)."""


class ConflictoError(TramaError):
    """La operación choca con datos existentes, p. ej. un correo repetido (HTTP 409)."""
