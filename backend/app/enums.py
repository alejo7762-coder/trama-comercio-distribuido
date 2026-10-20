"""
Valores permitidos por las restricciones CHECK de la base de datos.
Se definen una sola vez para que modelos, esquemas y servicios usen
exactamente los mismos valores que schema.sql.
"""

from enum import Enum


class Rol(str, Enum):
    CLIENTE = "CLIENTE"
    ADMIN = "ADMIN"


class EstadoPedido(str, Enum):
    PENDIENTE = "PENDIENTE"
    PAGADO = "PAGADO"
    ENVIADO = "ENVIADO"
    CANCELADO = "CANCELADO"


class MetodoPago(str, Enum):
    TARJETA = "TARJETA"
    PSE = "PSE"
    CONTRAENTREGA = "CONTRAENTREGA"


class EstadoPago(str, Enum):
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    PENDIENTE = "PENDIENTE"
