/* Portada: muestra algunos productos reales del catálogo y el estado de la API. */
(function () {
  "use strict";
  const api = window.TramaApi;
  const contenedor = document.getElementById("showcase-lista");

  function mini(p) {
    const fila = api.el("div", "mini");
    const img = api.el("span", "mini-img tono-" + (p.categoria_id % 3), (p.nombre || "?").charAt(0).toUpperCase());
    img.setAttribute("aria-hidden", "true");
    const texto = api.el("div");
    texto.appendChild(api.el("strong", null, p.nombre));
    texto.appendChild(api.el("span", "p", api.formatoPesos.format(Number(p.precio))));
    fila.appendChild(img);
    fila.appendChild(texto);
    return fila;
  }

  async function iniciar() {
    api.mostrarEstado("estado-api");
    try {
      const productos = (await api.listarProductos({})).slice(0, 3);
      if (productos.length === 0) {
        contenedor.replaceChildren(api.el("p", "showcase-vacio", "Aún no hay productos registrados."));
        return;
      }
      contenedor.replaceChildren(...productos.map(mini));
    } catch (e) {
      contenedor.replaceChildren(api.el("p", "showcase-vacio", "No se pudo cargar el catálogo."));
    }
  }

  iniciar();
})();
