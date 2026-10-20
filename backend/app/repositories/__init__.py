"""
Capa de acceso a datos. Cada función recibe la sesión y hace las consultas.

Regla de diseño: los repositorios hacen flush() pero NUNCA commit() ni
rollback(). Quien orquesta la operación (router o servicio) decide cuándo
confirmar o deshacer, para que varias escrituras formen una sola
transacción (indispensable en pedidos, pagos y Saga).
"""
