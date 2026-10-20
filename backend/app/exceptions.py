"""Excepciones de dominio traducidas a respuestas HTTP en main.py."""

class NoEncontradoError(Exception):
    """El recurso solicitado no existe."""

class ConflictoError(Exception):
    """La operación viola una regla de negocio o unicidad."""
