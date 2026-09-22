# Trama — Sistema Transaccional de Comercio Electrónico

Proyecto desarrollado para la asignatura **Sistemas Transaccionales**, Universidad Manuela Beltrán (UMB).

Sistema distribuido para una plataforma de comercio electrónico, orientado a la gestión de catálogo, carrito, pedidos y pagos en tiempo real.

## Estado del proyecto

- ✅ **Fase 1** — Prototipo de interfaz inicial (`index.html`).
- ✅ **Fase 3** — Base de datos relacional inicial y estructura base del backend.
- ⏳ Próximas fases: operaciones CRUD, lógica transaccional y conexión completa entre frontend, backend y base de datos.

## Estructura del repositorio

```
trama-comercio-distribuido/
├── index.html              # Prototipo de interfaz (Fase 1)
├── database/
│   ├── schema.sql           # Creación de la base de datos y tablas
│   └── seed.sql              # Datos iniciales de prueba
├── backend/
│   ├── app/
│   │   ├── main.py           # Punto de entrada de la API (FastAPI)
│   │   ├── database.py       # Configuración de conexión a SQL Server
│   │   ├── models.py         # Modelos ORM (reflejan las tablas de schema.sql)
│   │   └── routers/
│   │       └── health.py     # Endpoint de verificación de estado
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## Modelo relacional

Entidades principales: `Usuarios`, `Categorias`, `Productos`, `Carritos`, `CarritoItems`, `Pedidos`, `PedidoItems`, `Pagos`, `Facturas`, `Notificaciones`.

Relaciones clave:
- Un usuario tiene **un** carrito (`Carritos.UsuarioID` es único).
- Un carrito tiene muchos `CarritoItems`, cada uno asociado a un producto.
- Un usuario puede tener muchos pedidos; cada pedido tiene muchos `PedidoItems`.
- Cada pedido tiene **un único** pago y **una única** factura asociada (relaciones 1 a 1).
- Las notificaciones se asocian a un usuario y, opcionalmente, a un pedido.

## 1. Cómo ejecutar la base de datos

Requisitos: tener **SQL Server** instalado (o SQL Server Express) y una herramienta de administración como **SQL Server Management Studio (SSMS)** o Azure Data Studio.

1. Abre SSMS y conéctate a tu instancia local de SQL Server.
2. Abre el archivo `database/schema.sql` y ejecútalo completo (botón *Execute* o F5). Esto crea la base de datos `TramaDB` y todas sus tablas.
3. Abre el archivo `database/seed.sql` y ejecútalo para insertar los datos iniciales de prueba.
4. Verifica que todo quedó creado correctamente:
   ```sql
   USE TramaDB;
   SELECT * FROM Usuarios;
   SELECT * FROM Productos;
   ```

## 2. Cómo ejecutar el backend

Requisitos: **Python 3.10+** instalado y el **ODBC Driver 17 (o 18) for SQL Server** instalado en tu sistema operativo.

1. Entra a la carpeta del backend:
   ```bash
   cd backend
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Copia el archivo de variables de entorno y complétalo con tus datos reales de conexión:
   ```bash
   cp .env.example .env
   ```
5. Ejecuta el servidor de desarrollo:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Abre en el navegador:
   - `http://127.0.0.1:8000/health` → confirma que la API está viva.
   - `http://127.0.0.1:8000/health/db` → confirma que la API se conecta correctamente a `TramaDB`.
   - `http://127.0.0.1:8000/docs` → documentación interactiva generada automáticamente por FastAPI.

## Alcance de esta fase

Esta entrega establece la base técnica del sistema: creación de la base de datos, definición de tablas con llaves primarias y foráneas, restricciones de integridad, datos de prueba, y la organización inicial del backend con su conexión a la base de datos. **No incluye todavía** operaciones CRUD completas ni la integración funcional entre frontend, backend y base de datos — esto se desarrollará en las siguientes fases del proyecto.
