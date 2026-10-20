"""Envío SMTP opcional de confirmaciones de pedido."""
import os
import smtplib
import logging
from email.message import EmailMessage

logger = logging.getLogger("trama.email")

def enviar_confirmacion(destinatario: str, nombre: str, pedido_id: int, total: str, direccion: str) -> bool:
    host = os.getenv("SMTP_HOST", "").strip()
    remitente = os.getenv("SMTP_FROM", "").strip()
    if not host or not remitente:
        logger.warning("SMTP no configurado; no se envió correo para el pedido %s", pedido_id)
        return False
    mensaje = EmailMessage()
    mensaje["Subject"] = f"Trama: confirmación del pedido #{pedido_id}"
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje.set_content(f"Hola {nombre},\n\nRecibimos tu pedido #{pedido_id} en Trama.\nTotal: COP {total}\nDirección de entrega: {direccion}\n\nEste mensaje confirma el registro del pedido; no representa un cobro de tarjeta.\n\nGracias por comprar en Trama.")
    try:
        port = int(os.getenv("SMTP_PORT", "587"))
        with smtplib.SMTP(host, port, timeout=10) as server:
            if os.getenv("SMTP_STARTTLS", "true").lower() in ("1", "true", "yes"):
                server.starttls()
            user = os.getenv("SMTP_USER", "")
            password = os.getenv("SMTP_PASSWORD", "")
            if user:
                server.login(user, password)
            server.send_message(mensaje)
        return True
    except Exception:
        logger.exception("No se pudo enviar la confirmación del pedido %s", pedido_id)
        return False
