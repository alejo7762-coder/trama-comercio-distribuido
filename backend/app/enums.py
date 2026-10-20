"""Valores controlados del dominio."""
from enum import Enum

class Rol(str, Enum):
    CLIENTE = "CLIENTE"
    ADMIN = "ADMIN"
