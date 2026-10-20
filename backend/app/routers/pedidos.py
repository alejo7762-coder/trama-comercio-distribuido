"""Checkout transaccional, historial y consulta de pedidos."""
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.database import confirmar, get_db
from app.dependencies import usuario_actual, administrador_actual
from app.email_service import enviar_confirmacion
from app.models import Usuario, Carrito, CarritoItem, Producto, Pedido, PedidoItem, Pago, Factura, Notificacion
from app.schemas.commerce import CheckoutCreate, PedidoRead

router=APIRouter(prefix="/pedidos",tags=["Pedidos"])

@router.post("/checkout", response_model=PedidoRead, status_code=201)
def checkout(datos:CheckoutCreate, usuario:Usuario=Depends(usuario_actual), db:Session=Depends(get_db)):
    if datos.metodo_pago != "CONTRAENTREGA":
        raise HTTPException(422,"En esta versión solo está disponible el pago contraentrega.")
    direccion=datos.direccion_envio.strip(); telefono=datos.telefono_contacto.strip()
    carrito=db.query(Carrito).filter_by(UsuarioID=usuario.UsuarioID).first()
    if not carrito: raise HTTPException(400,"El carrito está vacío")
    items=db.query(CarritoItem).filter_by(CarritoID=carrito.CarritoID).all()
    if not items: raise HTTPException(400,"El carrito está vacío")
    detalles=[]; total=Decimal("0.00")
    try:
        for ci in items:
            p=db.query(Producto).filter(Producto.ProductoID==ci.ProductoID).with_for_update().first()
            if p is None: raise HTTPException(409,"Un producto del carrito ya no está disponible")
            if ci.Cantidad > p.Stock: raise HTTPException(409,f"Stock insuficiente para {p.Nombre}. Disponible: {p.Stock}")
            precio=Decimal(str(p.Precio)); subtotal=precio*ci.Cantidad
            # UPDATE condicional atómico: evita stock negativo aun con compras concurrentes.
            result=db.execute(update(Producto).where(Producto.ProductoID==p.ProductoID,Producto.Stock>=ci.Cantidad,Producto.Activo.is_(True)).values(Stock=Producto.Stock-ci.Cantidad))
            if result.rowcount != 1: raise HTTPException(409,f"El stock de {p.Nombre} cambió. Actualiza el carrito.")
            detalles.append((p.ProductoID,p.Nombre,ci.Cantidad,precio,subtotal)); total += subtotal
        pedido=Pedido(UsuarioID=usuario.UsuarioID,Estado="PENDIENTE",Total=total,DireccionEnvio=direccion,TelefonoContacto=telefono)
        db.add(pedido); db.flush()
        for pid,nombre,cantidad,precio,subtotal in detalles:
            db.add(PedidoItem(PedidoID=pedido.PedidoID,ProductoID=pid,Cantidad=cantidad,PrecioUnitario=precio))
        db.add(Pago(PedidoID=pedido.PedidoID,Monto=total,MetodoPago="CONTRAENTREGA",Estado="PENDIENTE"))
        db.add(Factura(PedidoID=pedido.PedidoID,NumeroFactura=f"TR-{datetime.utcnow():%Y%m%d}-{pedido.PedidoID:06d}"))
        db.add(Notificacion(UsuarioID=usuario.UsuarioID,PedidoID=pedido.PedidoID,Mensaje=f"Pedido #{pedido.PedidoID} registrado correctamente."))
        for ci in items: db.delete(ci)
        confirmar(db); db.refresh(pedido)
    except Exception:
        db.rollback()
        raise
    email_ok=enviar_confirmacion(usuario.Correo,usuario.Nombre,pedido.PedidoID,f"{total:,.2f}",direccion)
    salida=[{"producto_id":pid,"nombre":nombre,"cantidad":cantidad,"precio_unitario":precio,"subtotal":subtotal} for pid,nombre,cantidad,precio,subtotal in detalles]
    return {"pedido_id":pedido.PedidoID,"fecha_pedido":pedido.FechaPedido,"estado":pedido.Estado,"total":pedido.Total,"direccion_envio":pedido.DireccionEnvio,"telefono_contacto":pedido.TelefonoContacto,"metodo_pago":datos.metodo_pago,"email_enviado":email_ok,"items":salida}

@router.get("/mis-pedidos",response_model=list[PedidoRead])
def mis_pedidos(usuario:Usuario=Depends(usuario_actual),db:Session=Depends(get_db)):
    pedidos=db.query(Pedido).filter_by(UsuarioID=usuario.UsuarioID).order_by(Pedido.PedidoID.desc()).all(); salida=[]
    for p in pedidos:
        items=db.query(PedidoItem).filter_by(PedidoID=p.PedidoID).all(); det=[]
        for i in items:
            prod=db.query(Producto).filter_by(ProductoID=i.ProductoID).first()
            det.append({"producto_id":i.ProductoID,"nombre":prod.Nombre if prod else "Producto eliminado","cantidad":i.Cantidad,"precio_unitario":i.PrecioUnitario,"subtotal":i.PrecioUnitario*i.Cantidad})
        pago=db.query(Pago).filter_by(PedidoID=p.PedidoID).first()
        salida.append({"pedido_id":p.PedidoID,"fecha_pedido":p.FechaPedido,"estado":p.Estado,"total":p.Total,"direccion_envio":p.DireccionEnvio,"telefono_contacto":p.TelefonoContacto,"metodo_pago":pago.MetodoPago if pago else "—","email_enviado":False,"items":det})
    return salida

@router.get("/",response_model=list[PedidoRead])
def listar_todos_pedidos(_:Usuario=Depends(administrador_actual),db:Session=Depends(get_db)):
    pedidos=db.query(Pedido).order_by(Pedido.PedidoID.desc()).all(); salida=[]
    for p in pedidos:
        items=db.query(PedidoItem).filter_by(PedidoID=p.PedidoID).all(); det=[]
        for i in items:
            prod=db.query(Producto).filter_by(ProductoID=i.ProductoID).first()
            det.append({"producto_id":i.ProductoID,"nombre":prod.Nombre if prod else "Producto eliminado","cantidad":i.Cantidad,"precio_unitario":i.PrecioUnitario,"subtotal":i.PrecioUnitario*i.Cantidad})
        pago=db.query(Pago).filter_by(PedidoID=p.PedidoID).first()
        salida.append({"pedido_id":p.PedidoID,"fecha_pedido":p.FechaPedido,"estado":p.Estado,"total":p.Total,"direccion_envio":p.DireccionEnvio,"telefono_contacto":p.TelefonoContacto,"metodo_pago":pago.MetodoPago if pago else "—","email_enviado":False,"items":det})
    return salida
