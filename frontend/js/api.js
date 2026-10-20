/* Cliente de la API de Trama. Las rutas son relativas: la interfaz se sirve desde la misma API (/app/). */
(function (global) {
  "use strict";

  const formatoPesos = new Intl.NumberFormat("es-CO", {
    style: "currency", currency: "COP", maximumFractionDigits: 0,
  });

  function mensajeDeError(cuerpo, estado) {
    if (cuerpo && typeof cuerpo.detail === "string") return cuerpo.detail;
    if (cuerpo && Array.isArray(cuerpo.detail)) {
      return cuerpo.detail.map(function (e) {
        const campo = (e.loc || []).slice(1).join(".");
        return campo ? campo + ": " + e.msg : e.msg;
      }).join(" · ");
    }
    return "Error inesperado (HTTP " + estado + ")";
  }

  async function solicitar(ruta, opciones) {
    let respuesta;
    try {
      respuesta = await fetch(ruta, opciones);
    } catch (e) {
      throw new Error("No se pudo conectar con la API. Verifique que el servidor (uvicorn) esté en ejecución.");
    }
    let cuerpo = null;
    try { cuerpo = await respuesta.json(); } catch (e) { /* respuesta sin cuerpo JSON */ }
    if (!respuesta.ok) {
      const error = new Error(mensajeDeError(cuerpo, respuesta.status));
      error.status = respuesta.status;
      throw error;
    }
    return cuerpo;
  }

  function listarCategorias() {
    return solicitar("/categorias");
  }

  function listarProductos(filtros) {
    const params = new URLSearchParams();
    if (filtros && filtros.buscar) params.set("buscar", filtros.buscar);
    if (filtros && filtros.categoriaId) params.set("categoria_id", filtros.categoriaId);
    params.set("limit", "100");
    return solicitar("/productos?" + params.toString());
  }

  function crearProducto(datos) {
    return solicitar("/productos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
  }

  /* Crea un elemento con clase y texto. El texto se asigna con textContent: nunca se interpreta como HTML. */
  function el(etiqueta, clase, texto) {
    const nodo = document.createElement(etiqueta);
    if (clase) nodo.className = clase;
    if (texto !== undefined && texto !== null) nodo.textContent = texto;
    return nodo;
  }

  /* Muestra en la cabecera si la API y la base de datos responden. */
  async function mostrarEstado(idElemento) {
    const nodo = document.getElementById(idElemento);
    if (!nodo) return;
    try {
      await solicitar("/health/db");
      nodo.textContent = "API y base de datos conectadas";
      nodo.className = "estado-api ok";
    } catch (e) {
      nodo.textContent = "Sin conexión con la API o la base de datos";
      nodo.className = "estado-api error";
    }
  }

  global.TramaApi = { formatoPesos, listarCategorias, listarProductos, crearProducto, el, mostrarEstado };
})(window);
