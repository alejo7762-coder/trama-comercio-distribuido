# Trama — Sistema transaccional de comercio electrónico

Proyecto académico de **Sistemas Transaccionales**, Universidad Manuela Beltrán (UMB).

Trama es un prototipo de comercio electrónico con una API REST en FastAPI, SQL Server como base de datos prevista para ejecución local y una interfaz web servida por la misma API. El alcance funcional implementado actualmente es el catálogo: consulta y filtrado de productos, consulta/creación de categorías, registro de productos y actualización parcial de inventario.

> **Estado y límites:** las páginas de catálogo y administración funcionan sin autenticación. No se deben exponer en Internet ni usar con datos reales hasta implementar y verificar autenticación/autorización, gestión segura de credenciales y los flujos transaccionales restantes. Carrito, pedidos, pagos reales, facturación, notificaciones, Saga, mensajería y asistente IA forman parte del diseño/alcance futuro; no se deben presentar como funciones ya implementadas.

## Estructura

```text
trama-comercio-distribuido/
├── database/
│   ├── schema.sql
│   └── seed.sql
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── enums.py
│   │   ├── exceptions.py
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── routers/
│   ├── tests/
│   ├── scripts/check_env.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── catalogo.html
│   ├── admin.html
│   ├── css/estilos.css
│   └── js/
└── README.md
```

## Requisitos

- Python 3.10 o superior.
- SQL Server / SQL Server Express y un driver ODBC compatible (el ejemplo usa ODBC Driver 18).
- Git y una terminal.

## 1. Preparar la base de datos

1. Abre SQL Server Management Studio (SSMS) o Azure Data Studio y conéctate a tu instancia.
2. Ejecuta `database/schema.sql`.
3. Para cargar datos de demostración, revisa y ejecuta `database/seed.sql` **una sola vez** sobre una base limpia. El script de seed puede fallar si ya existen registros con las mismas claves/correos.
4. Comprueba las tablas y los datos con consultas SELECT.

No uses las credenciales de ejemplo del seed en un sistema real. Los valores de contraseña de demostración no son hashes válidos para autenticación.

## 2. Configurar y ejecutar la API

Desde la raíz del repositorio:

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# Windows CMD: .venv\\Scripts\\activate.bat
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copia `.env.example` como `.env` y configura servidor, base de datos, driver y método de autenticación según tu instalación. No subas el archivo `.env` ni secretos a GitHub.

En Windows:

```powershell
Copy-Item .env.example .env
python scripts/check_env.py
uvicorn app.main:app --reload
```

En macOS/Linux, usa `cp .env.example .env` en lugar de `Copy-Item`.

Direcciones locales después de iniciar Uvicorn:

- Interfaz: http://127.0.0.1:8000/app/
- Catálogo: http://127.0.0.1:8000/app/catalogo.html
- Administración de productos: http://127.0.0.1:8000/app/admin.html
- Documentación de API: http://127.0.0.1:8000/docs
- Estado de API: http://127.0.0.1:8000/health
- Estado de base de datos: http://127.0.0.1:8000/health/db

La comprobación `/health/db` requiere una conexión funcional a SQL Server y que exista `TramaDB`.

## 3. Ejecutar pruebas automatizadas

Las pruebas de catálogo usan SQLite en memoria; no necesitan conectarse a SQL Server, pero sí instalar las dependencias del archivo requirements.

Desde la carpeta `backend`, con el entorno virtual activo:

```bash
python -m pytest -q
```

Las pruebas deben ejecutarse en el entorno local antes de considerar validada una entrega. La existencia de pruebas en el repositorio no significa que hayan pasado en todas las máquinas.

## Endpoints del catálogo

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/categorias` | Listar categorías |
| POST | `/categorias` | Crear categoría |
| GET | `/productos` | Listar productos, con paginación y filtros |
| GET | `/productos/{producto_id}` | Consultar producto |
| POST | `/productos` | Crear producto |
| PATCH | `/productos/{producto_id}` | Actualizar campos del producto |
| GET | `/health` | Verificar proceso API |
| GET | `/health/db` | Verificar conexión con base de datos |

## Modelo de datos

El esquema relacional contempla Usuarios, Categorías, Productos, Carritos, elementos de carrito, Pedidos, elementos de pedido, Pagos, Facturas y Notificaciones. Las tablas existen en el diseño SQL; que estén definidas no implica que todos sus flujos de negocio estén implementados en la API.

## Consideraciones antes de una entrega

- Ejecutar las pruebas y registrar sus resultados reales.
- Probar la conexión con SQL Server usando la configuración local.
- No publicar credenciales reales ni utilizar hashes de demostración como credenciales funcionales.
- Proteger los endpoints de escritura con autenticación y autorización antes de desplegar.
- Documentar como implementadas únicamente las funciones verificadas; distinguir claramente los requisitos diseñados de los desarrollados.
