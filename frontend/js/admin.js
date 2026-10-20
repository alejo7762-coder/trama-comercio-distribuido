/* Pantalla de administración: registra productos (con validación) y muestra el inventario. */
(function () {
  "use strict";
  const api = window.TramaApi;
  const form = document.getElementById("form-producto");
  const aviso = document.getElementById("aviso");
  const cuerpoTabla = document.getElementById("tabla-productos");
  const boton = document.getElementById("guardar");
  const selectCategoria = document.getElementById("categoria_id");

  const campos = ["nombre", "categoria_id", "precio", "stock", "descripcion"];

  function marcarError(nombre, texto) {
    const campo = document.getElementById(nombre).closest(".campo");
    campo.classList.toggle("invalido", Boolean(texto));
    campo.querySelector(".error").textContent = texto || "";
  }

  /* Las mismas reglas que valida la API y la base de datos (la validación definitiva siempre es la del servidor). */
  function validar() {
    const leer = function (id) { return document.getElementById(id).value.trim(); };
    const v = {
      nombre: leer("nombre"),
      categoria_id: leer("categoria_id"),
      precio: leer("precio"),
      stock: leer("stock"),
      descripcion: leer("descripcion"),
    };
    const errores = {};
    if (!v.nombre) errores.nombre = "El nombre es obligatorio.";
    else if (v.nombre.length > 150) errores.nombre = "Máximo 150 caracteres.";
    if (!v.categoria_id) errores.categoria_id = "Seleccione una categoría.";
    if (!/^\d{1,8}(\.\d{1,2})?$/.test(v.precio) || Number(v.precio) <= 0)
      errores.precio = "Ingrese un valor mayor a 0, sin puntos de miles y con punto decimal (ej. 49900 o 49900.50).";
    if (!/^\d+$/.test(v.stock)) errores.stock = "Ingrese un número entero igual o mayor a 0.";
    if (v.descripcion.length > 500) errores.descripcion = "Máximo 500 caracteres.";
    campos.forEach(function (c) { marcarError(c, errores[c]); });
    return { valido: Object.keys(errores).length === 0, v: v };
  }

  function mostrarAviso(tipo, texto) {
    aviso.className = "alerta " + tipo;
    aviso.textContent = texto;
    aviso.hidden = false;
  }

  async function cargarCategorias() {
    const categorias = await api.listarCategorias();
    categorias.forEach(function (c) {
      const op = api.el("option", null, c.nombre);
      op.value = c.categoria_id;
      selectCategoria.appendChild(op);
    });
  }

  async function cargarTabla() {
    try {
      const productos = await api.listarProductos({});
      if (productos.length === 0) {
        const fila = api.el("tr"); const celda = api.el("td", null, "Aún no hay productos registrados.");
        celda.colSpan = 5; fila.appendChild(celda); return cuerpoTabla.replaceChildren(fila);
      }
      cuerpoTabla.replaceChildren(...productos.map(function (p) {
        const fila = api.el("tr");
        fila.appendChild(api.el("td", null, String(p.producto_id)));
        fila.appendChild(api.el("td", null, p.nombre));
        fila.appendChild(api.el("td", null, p.categoria ? p.categoria.nombre : "—"));
        fila.appendChild(api.el("td", "num", api.formatoPesos.format(Number(p.precio))));
        fila.appendChild(api.el("td", "num", String(p.stock)));
        return fila;
      }));
    } catch (e) {
      mostrarAviso("error", e.message);
    }
  }

  form.addEventListener("submit", async function (evento) {
    evento.preventDefault();
    aviso.hidden = true;
    const { valido, v } = validar();
    if (!valido) return mostrarAviso("error", "Corrija los campos marcados antes de guardar.");
    boton.disabled = true;
    try {
      const creado = await api.crearProducto({
        nombre: v.nombre,
        descripcion: v.descripcion || null,
        precio: v.precio,
        stock: Number(v.stock),
        categoria_id: Number(v.categoria_id),
      });
      mostrarAviso("ok", "Producto «" + creado.nombre + "» registrado con el código " + creado.producto_id + ".");
      form.reset();
      await cargarTabla();
    } catch (e) {
      mostrarAviso("error", e.message);
    } finally {
      boton.disabled = false;
    }
  });

  api.mostrarEstado("estado-api");
  cargarCategorias().catch(function (e) { mostrarAviso("error", e.message); });
  cargarTabla();
})();
