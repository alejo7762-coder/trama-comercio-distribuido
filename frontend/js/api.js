/* Cliente centralizado de la API Trama. */
(function(global){"use strict";
 const formatoPesos=new Intl.NumberFormat("es-CO",{style:"currency",currency:"COP",maximumFractionDigits:0});
 const tokenKey="trama_access_token", userKey="trama_user";
 function token(){return sessionStorage.getItem(tokenKey)||""}
 function usuario(){try{return JSON.parse(sessionStorage.getItem(userKey)||"null")}catch(e){return null}}
 function guardarSesion(data){sessionStorage.setItem(tokenKey,data.access_token);sessionStorage.setItem(userKey,JSON.stringify(data.usuario))}
 function cerrarSesion(){sessionStorage.removeItem(tokenKey);sessionStorage.removeItem(userKey)}
 function mensajeDeError(cuerpo,estado){if(cuerpo&&typeof cuerpo.detail==="string")return cuerpo.detail;if(cuerpo&&Array.isArray(cuerpo.detail))return cuerpo.detail.map(e=>((e.loc||[]).slice(1).join(".")?((e.loc||[]).slice(1).join(".")+": "):"")+e.msg).join(" · ");return "Error inesperado (HTTP "+estado+")"}
 async function solicitar(ruta,opciones){opciones=opciones||{};opciones.headers=Object.assign({},opciones.headers||{});if(token())opciones.headers.Authorization="Bearer "+token();if(opciones.body&&typeof opciones.body!=="string"){opciones.headers["Content-Type"]="application/json";opciones.body=JSON.stringify(opciones.body)}let respuesta;try{respuesta=await fetch(ruta,opciones)}catch(e){throw new Error("No se pudo conectar con la API. Comprueba que uvicorn esté en ejecución.")}let cuerpo=null;try{cuerpo=await respuesta.json()}catch(e){}if(!respuesta.ok){if(respuesta.status===401&&token())cerrarSesion();const error=new Error(mensajeDeError(cuerpo,respuesta.status));error.status=respuesta.status;throw error}return cuerpo}
 function listarCategorias(){return solicitar("/categorias")}
 function listarProductos(f){const p=new URLSearchParams();if(f&&f.buscar)p.set("buscar",f.buscar);if(f&&f.categoriaId)p.set("categoria_id",f.categoriaId);p.set("limit","100");return solicitar("/productos?"+p)}
 function crearProducto(d){return solicitar("/productos",{method:"POST",body:d})}
 function actualizarProducto(id,d){return solicitar("/productos/"+id,{method:"PATCH",body:d})}
 function eliminarProducto(id){return solicitar("/productos/"+id,{method:"DELETE"})}
 function login(d){return solicitar("/auth/login",{method:"POST",body:d}).then(d=>{guardarSesion(d);return d})}
 function registrar(d){return solicitar("/auth/register",{method:"POST",body:d}).then(d=>{guardarSesion(d);return d})}
 function miPerfil(){return solicitar("/auth/me")}
 function carrito(){return solicitar("/carrito")}
 function agregarCarrito(producto_id,cantidad){return solicitar("/carrito/items",{method:"POST",body:{producto_id,cantidad}})}
 function cambiarCantidad(id,cantidad){return solicitar("/carrito/items/"+id,{method:"PATCH",body:{cantidad}})}
 function quitarCarrito(id){return solicitar("/carrito/items/"+id,{method:"DELETE"})}
 function checkout(datos){return solicitar("/pedidos/checkout",{method:"POST",body:datos})}
 function misPedidos(){return solicitar("/pedidos/mis-pedidos")}
 function el(etiqueta,clase,texto){const n=document.createElement(etiqueta);if(clase)n.className=clase;if(texto!==undefined&&texto!==null)n.textContent=texto;return n}
 async function mostrarEstado(id){const n=document.getElementById(id);if(!n)return;try{await solicitar("/health/db");n.textContent="Sistema conectado";n.className="estado-api ok"}catch(e){n.textContent="API/base de datos sin conexión";n.className="estado-api error"}}
 function actualizarNavegacion(){const u=usuario();document.querySelectorAll("[data-admin]").forEach(n=>n.hidden=!u||u.rol!=="ADMIN");document.querySelectorAll("[data-auth]").forEach(n=>n.textContent=u?"Mi cuenta":"Ingresar / registrarse");return u}
 global.TramaApi={formatoPesos,token,usuario,guardarSesion,cerrarSesion,solicitar,listarCategorias,listarProductos,crearProducto,actualizarProducto,eliminarProducto,login,registrar,miPerfil,carrito,agregarCarrito,cambiarCantidad,quitarCarrito,checkout,misPedidos,el,mostrarEstado,actualizarNavegacion};
})(window);
