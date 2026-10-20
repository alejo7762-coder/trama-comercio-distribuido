/* Pantalla de catálogo: consulta productos en la API con búsqueda y filtro por categoría. */
(function () {
  "use strict";
  const api = window.TramaApi;
  const lista = document.getElementById("productos");
  const conteo = document.getElementById("conteo");
  const inputBuscar = document.getElementById("buscar");
  const selectCategoria = document.getElementById("categoria");
  let solicitudActual = 0;
  let temporizador = null;

  function mensaje(texto) {
    lista.replaceChildren(api.el("div", "mensaje", texto));
  }

  function etiquetaStock(stock) {
    if (stock <= 0) return ["Agotado", "agotado"];
    if (stock <= 5) return ["Quedan " + stock + " unidades", "bajo"];
    return ["Disponible (" + stock + ")", "ok"];
  }

  function tarjeta(p) {
    const card = api.el("article", "pcard");
    card.appendChild(api.el("span", "cat", p.categoria ? p.categoria.nombre : "Sin categoría"));
    card.appendChild(api.el("h3", null, p.nombre));
    card.appendChild(api.el("p", null, p.descripcion || "Sin descripción."));
    card.appendChild(api.el("div", "precio", api.formatoPesos.format(Number(p.precio))));
    const [texto, clase] = etiquetaStock(p.stock);
    card.appendChild(api.el("span", "stock " + clase, texto));
    const boton = api.el("button", null, p.stock > 0 ? "Agregar al carrito" : "Agotado");
    boton.disabled = p.stock <= 0;
    boton.addEventListener("click", async function () {
      if (!api.token()) { location.href = "cuenta.html"; return; }
      boton.disabled = true;
      try { await api.agregarCarrito(p.producto_id, 1); boton.textContent = "Agregado ✓"; }
      catch (e) { if (e.status === 401) location.href = "cuenta.html"; else alert(e.message); }
      finally { setTimeout(function(){ boton.disabled = p.stock <= 0; if (!boton.disabled) boton.textContent = "Agregar al carrito"; }, 1200); }
    });
    card.appendChild(boton);
    return card;
  }

  async function cargar() {
    const numero = ++solicitudActual;
    mensaje("Cargando productos…");
    try {
      const productos = await api.listarProductos({
        buscar: inputBuscar.value.trim(),
        categoriaId: selectCategoria.value,
      });
      if (numero !== solicitudActual) return; // llegó una respuesta más nueva; se descarta esta
      conteo.textContent = productos.length + (productos.length === 1 ? " producto" : " productos");
      if (productos.length === 0) return mensaje("No hay productos que coincidan con la búsqueda.");
      lista.replaceChildren(...productos.map(tarjeta));
    } catch (e) {
      if (numero !== solicitudActual) return;
      conteo.textContent = "";
      mensaje(e.message);
    }
  }

  async function iniciar() {
    api.mostrarEstado("estado-api");
    api.actualizarNavegacion();
    try {
      const categorias = await api.listarCategorias();
      categorias.forEach(function (c) {
        const op = api.el("option", null, c.nombre);
        op.value = c.categoria_id;
        selectCategoria.appendChild(op);
      });
    } catch (e) { /* el error se mostrará al cargar los productos */ }
    inputBuscar.addEventListener("input", function () {
      clearTimeout(temporizador);
      temporizador = setTimeout(cargar, 300);
    });
    selectCategoria.addEventListener("change", cargar);
    cargar();
  }

  iniciar();
})();
