# Trama — Sistema Transaccional de Comercio Electrónico

Proyecto de la asignatura **Sistemas Transaccionales**, Universidad Manuela Beltrán (UMB), Ingeniería de Software.

Sistema para una plataforma de comercio electrónico orientado a catálogo, carrito, pedidos y pagos. El diseño completo (arquitectura de microservicios, casos de uso, clases y modelo relacional) está en el documento maestro; este repositorio contiene su implementación progresiva.

## Estado del proyecto

| Funcionalidad | Estado |
|---|---|
| Base de datos relacional en SQL Server (10 tablas, restricciones, datos de prueba) | Implementado |
| Modelos, esquemas de validación y repositorios | Implementado |
| **Consultar catálogo** (búsqueda por nombre y filtro por categoría) — RF04 | **Implementado** |
| **Registrar productos** con validación en pantalla, API y base de datos — RF05 (parcial) | **Implementado** |
| Pruebas automatizadas (62) y pruebas de la interfaz | Implementado |
| Registro e inicio de sesión, roles — RF01 a RF03 | Pendiente |
| Carrito, pedidos, pagos, facturas, notificaciones — RF06 a RF12 | Pendiente |
| Microservicios, API Gateway, mensajería asíncrona y patrón Saga | Pendiente (solo diseño) |
| MongoDB | Pendiente (el catálogo está hoy en SQL Server) |

### Limitaciones conocidas

- Las operaciones de escritura (`POST` y `PATCH` de productos y categorías) **todavía no exigen inicio de sesión**; se restringirán al rol administrador cuando se implemente la autenticación.
- El backend es una sola aplicación FastAPI; la separación en microservicios es una fase posterior.
- Actualizar un producto está disponible en la API (`PATCH /productos/{id}`) pero aún no tiene pantalla.

## Estructura del repositorio

```
trama-comercio-distribuido/
├── frontend/                    # Interfaz web (HTML, CSS y JavaScript)
│   ├── index.html               # Inicio y estado del proyecto
│   ├── catalogo.html            # Consulta del catálogo
│   ├── admin.html               # Registro de productos e inventario
│   ├── css/estilos.css          # Sistema de diseño (colores y estilos de la marca)
│   ├── img/                     # Logo de Trama, ícono y favicon
│   └── js/                      # api.js (cliente de la API), inicio.js, catalogo.js, admin.js
├── database/
│   ├── schema.sql               # Crea TramaDB y sus tablas (repetible)
│   └── seed.sql                 # Datos de prueba (repetible)
├── backend/
│   ├── app/
│   │   ├── main.py              # Aplicación FastAPI; sirve la API y la interfaz
│   │   ├── database.py          # Conexión a SQL Server
│   │   ├── models.py            # Modelos ORM (reflejan schema.sql)
│   │   ├── enums.py, exceptions.py
│   │   ├── schemas/             # Validación de entrada y salida (Pydantic)
│   │   ├── repositories/        # Acceso a datos
│   │   └── routers/             # Endpoints: health, categorías, productos
│   ├── scripts/                 # check_env.py, check_models.py
│   ├── tests/                   # Pruebas automatizadas
│   ├── requirements.txt, requirements-dev.txt
│   └── .env.example
├── docs/evidencias/             # Capturas de pantalla de las pruebas
└── README.md
```

## Identidad visual

La interfaz usa los colores del logo de Trama. Las variables están en `frontend/css/estilos.css`.

| Uso | Color |
|---|---|
| Texto y fondos oscuros (azul marino) | `#0C1B33` |
| Turquesa del logo (fondos decorativos) | `#01A29D` |
| Verde del logo (fondos decorativos) | `#01A26B` |
| Botones y textos de acento (versiones oscuras, contraste mínimo 4.5:1) | `#0A8480` a `#077A52`, `#0B6F6B` |
| Fondo general y etiquetas suaves | `#F3F9F8`, `#E7F7F4` |

Tipografías: Poppins (títulos) e Inter (texto), cargadas desde Google Fonts.

## Requisitos

- Windows con **Python 3.10 o superior**.
- **SQL Server** (Express o Developer) y SQL Server Management Studio.
- **ODBC Driver 17 o 18 for SQL Server**.

## 1. Base de datos

1. En SSMS conéctate a tu instancia (por ejemplo `localhost\SQLEXPRESS`).
2. Abre y ejecuta `database/schema.sql` y después `database/seed.sql`. Ambos se pueden ejecutar varias veces sin dañar los datos.
3. Comprueba: `USE TramaDB; SELECT * FROM Productos;` debe mostrar 4 productos.

## 2. Backend

Desde la carpeta `backend`, en PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
notepad .env
python scripts/check_env.py
uvicorn app.main:app --reload
```

En el `.env` configura `DB_SERVER` (por ejemplo `localhost\SQLEXPRESS`) y `DB_TRUSTED_CONNECTION=yes` si usas autenticación de Windows. `python scripts/check_env.py` diagnostica el entorno y no debe mostrar ningún `[FALLO]`.

## 3. Usar la aplicación

Con `uvicorn` en ejecución abre en el navegador:

| Dirección | Qué muestra |
|---|---|
| `http://127.0.0.1:8000/` | Inicio de la interfaz |
| `http://127.0.0.1:8000/app/catalogo.html` | Catálogo con búsqueda y filtro |
| `http://127.0.0.1:8000/app/admin.html` | Registro de productos |
| `http://127.0.0.1:8000/docs` | Documentación interactiva de la API |
| `http://127.0.0.1:8000/health/db` | Estado de la conexión con SQL Server |

La interfaz debe abrirse a través del servidor (no haciendo doble clic en los `.html`), porque consulta la API.

### Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/productos` | Lista productos. Parámetros: `buscar`, `categoria_id`, `skip`, `limit` |
| GET | `/productos/{id}` | Detalle de un producto |
| POST | `/productos` | Registra un producto (201) |
| PATCH | `/productos/{id}` | Actualiza campos de un producto |
| GET | `/categorias` | Lista categorías |
| POST | `/categorias` | Registra una categoría |
| GET | `/health`, `/health/db` | Estado de la API y de la base de datos |

Códigos de error: `422` datos inválidos, `404` recurso inexistente, `409` conflicto con datos existentes, `503` base de datos no disponible.

## 4. Pruebas

Desde `backend`, con el entorno virtual activo:

```powershell
pytest                          # 62 pruebas (SQLite en memoria; no tocan SQL Server)
python scripts/check_models.py  # verifica la capa de datos contra SQL Server (no deja datos)
```

## Solución de problemas

| Síntoma | Solución |
|---|---|
| `uvicorn` no se reconoce | Activa el entorno virtual: `venv\Scripts\Activate.ps1` |
| `Named Pipes Provider ... could not open a connection` | Revisa `DB_SERVER`, que el servicio de SQL Server esté en ejecución y, con instancias con nombre, que **SQL Server Browser** esté activo |
| `Login failed for user` | Usa `DB_TRUSTED_CONNECTION=yes` (autenticación de Windows) |
| El catálogo dice «Sin conexión con la API» | `uvicorn` no está en ejecución o abriste el HTML directamente desde el explorador de archivos |
| Las tildes salen como `Ã­` en SSMS | Abre los `.sql` con *File → Open* (están en UTF-8 con BOM) |

## Control de versiones

Los cambios se registran en commits pequeños y descriptivos (`feat`, `fix`, `test`, `docs`, `refactor`). El historial muestra la evolución del proyecto.
