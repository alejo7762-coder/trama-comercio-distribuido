# Trama — Comercio electrónico transaccional

Proyecto académico de Sistemas Transaccionales, Universidad Manuela Beltrán (UMB). API REST FastAPI, SQLAlchemy y SQL Server; frontend HTML/CSS/JavaScript servido por la misma API.

## Funcionalidad implementada en esta rama

- Registro de clientes con nombre, correo, contraseña, teléfono y dirección.
- Contraseñas almacenadas como hashes Argon2; inicio de sesión con tokens JWT de vida limitada.
- Roles CLIENTE y ADMIN comprobados en el backend.
- Catálogo público, búsqueda por nombre y filtro por categoría.
- Carrito por usuario: agregar, cambiar cantidad y quitar productos.
- Checkout contraentrega con dirección y teléfono de entrega, pedido, detalle, registro de pago pendiente, factura interna y notificación.
- Descuento de stock en la misma transacción del pedido, con actualización condicional para impedir existencias negativas bajo compras concurrentes.
- Historial de pedidos por cliente.
- Panel de administrador para crear, editar y eliminar/desactivar productos. Los productos asociados a pedidos se desactivan para conservar el historial.
- Envío de correo de confirmación por SMTP opcional. Si SMTP no está configurado o falla, el pedido permanece registrado y la API informa que no se envió el correo.

**No se procesan tarjetas ni pagos en línea reales.** El pago contraentrega queda pendiente; el módulo de pago es un registro académico, no una pasarela. No se debe presentar la factura interna como factura electrónica validada por DIAN. El sistema todavía necesita controles adicionales antes de un despliegue público (limitación de intentos de login, verificación de correo, recuperación de contraseña, política de privacidad, monitoreo y configuración TLS).

## Estructura

- `backend/app/`: API, seguridad, modelos, esquemas, repositorios y routers.
- `backend/scripts/create_admin.py`: alta/promoción de cuenta administradora.
- `backend/tests/`: pruebas automatizadas.
- `database/schema.sql`: esquema para base de datos nueva.
- `database/migration_ecommerce.sql`: columnas nuevas para una base TramaDB creada con el esquema anterior.
- `database/seed.sql`: datos de demostración del catálogo.
- `frontend/`: inicio, catálogo, cuenta, carrito y panel de administración.

## Requisitos

- Python 3.10 o superior.
- SQL Server / SQL Server Express.
- Driver ODBC compatible con SQL Server (por defecto ODBC Driver 18).
- Cuenta de correo SMTP si se desea enviar confirmaciones reales.

## 1. Preparar SQL Server

Si es una base nueva, ejecuta `database/schema.sql` en SQL Server Management Studio. Para una base ya creada con el esquema anterior, ejecuta **una vez** `database/migration_ecommerce.sql` sobre TramaDB. No ejecutes los dos caminos sin revisar el estado de las columnas.

Después, carga `database/seed.sql` una sola vez para crear categorías y productos de demostración. El seed puede fallar si se repite sobre datos existentes. Las contraseñas de ejemplo que pueda contener el seed son marcadores, no credenciales utilizables.

## 2. Instalar y configurar backend

Desde la raíz del repositorio:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `backend/.env` y define la conexión de SQL Server. Reemplaza obligatoriamente `JWT_SECRET_KEY` por un secreto aleatorio de al menos 32 caracteres. Puedes generarlo con:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

No publiques `.env`, contraseñas ni secretos en GitHub. Para autenticación integrada de Windows, configura `DB_TRUSTED_CONNECTION=yes` según la documentación de `backend/.env.example`.

### Configurar correo SMTP

Completa `SMTP_HOST`, `SMTP_PORT`, `SMTP_STARTTLS`, `SMTP_USER`, `SMTP_PASSWORD` y `SMTP_FROM` con los datos del proveedor de correo. Para Gmail, por ejemplo, se suele necesitar una contraseña de aplicación y tener activado el acceso correspondiente; no uses la contraseña habitual de tu cuenta. No guardes credenciales reales en el repositorio.

### Crear cuenta administradora

El registro público crea únicamente usuarios CLIENTE; no existe una opción pública para autorregistrarse como ADMIN. Desde la carpeta `backend`, después de configurar `.env` y ejecutar la migración:

```powershell
$env:ADMIN_EMAIL="admin@tu-dominio.com"
$env:ADMIN_NAME="Administrador Trama"
python -m scripts.create_admin
```

El script solicitará la contraseña de forma oculta si no se establece `ADMIN_PASSWORD`. Usa una contraseña única de al menos 12 caracteres. Si se define `ADMIN_PASSWORD` en el entorno, elimínala de ese entorno al terminar.

## 3. Iniciar y usar

Desde `backend/`:

```powershell
uvicorn app.main:app --reload
```

Abre:

- Inicio: http://127.0.0.1:8000/app/
- Catálogo: http://127.0.0.1:8000/app/catalogo.html
- Registro / inicio de sesión: http://127.0.0.1:8000/app/cuenta.html
- Carrito y checkout: http://127.0.0.1:8000/app/carrito.html
- Panel de administración: http://127.0.0.1:8000/app/admin.html
- Documentación de API: http://127.0.0.1:8000/docs
- Estado de API: http://127.0.0.1:8000/health
- Estado de base de datos: http://127.0.0.1:8000/health/db

### Flujo de cliente

1. Abre Cuenta y registra nombre, correo, contraseña, teléfono y dirección.
2. Inicia sesión si no queda autenticado después del registro.
3. En Catálogo, agrega productos al carrito.
4. En Carrito, verifica cantidades y dirección y confirma contraentrega.
5. El backend comprueba stock y confirma pedido, detalles, pago pendiente, factura interna y notificación en una única transacción de base de datos.
6. El stock disminuye y el carrito se vacía solo cuando la transacción se confirma. El cliente puede consultar el historial desde Cuenta.

### Flujo de administrador

1. Ejecuta el script de creación/promoción de administrador.
2. Inicia sesión con esa cuenta.
3. Entra al panel de administración para crear, editar o eliminar/desactivar productos.
4. La API comprueba el rol ADMIN en cada operación; ocultar un enlace en la interfaz no se considera seguridad.

## Endpoints principales

| Método | Ruta | Acceso |
|---|---|---|
| POST | `/auth/register` | Público |
| POST | `/auth/login` | Público |
| GET/PATCH | `/auth/me` | Usuario autenticado |
| GET | `/categorias` | Público |
| POST | `/categorias` | ADMIN |
| GET | `/productos`, `/productos/{id}` | Público |
| POST/PATCH/DELETE | `/productos...` | ADMIN |
| GET/POST | `/carrito`, `/carrito/items` | Usuario autenticado |
| PATCH/DELETE | `/carrito/items/{producto_id}` | Usuario autenticado |
| POST | `/pedidos/checkout` | Usuario autenticado |
| GET | `/pedidos/mis-pedidos` | Usuario autenticado |
| GET | `/pedidos/` | ADMIN |
| GET | `/health`, `/health/db` | Público |

La autenticación usa `Authorization: Bearer <token>`; el token vence según `JWT_ACCESS_MINUTES`. El frontend conserva el token en `sessionStorage` durante la sesión de la pestaña.

## Pruebas

Desde `backend/` con el entorno virtual activo:

```powershell
python -m pytest -q
```

Las pruebas automatizadas deben ejecutarse después de instalar dependencias y antes de entregar. También prueba el flujo completo manualmente contra SQL Server y con SMTP de prueba. La existencia de tests no significa que hayan pasado en todos los entornos.

## Límites y seguridad

- Solo se implementó pago contraentrega; no se capturan tarjetas ni se conecta una pasarela.
- La confirmación de correo requiere SMTP válido; el pedido no se revierte si falla el correo.
- Los tokens se almacenan en `sessionStorage`; evita introducir scripts de terceros no confiables y despliega únicamente detrás de HTTPS.
- Antes de producción agrega rate limiting al login/registro, verificación de correo, recuperación de contraseña, auditoría, backups, gestión de privacidad y pruebas de concurrencia con SQL Server.
- Los datos de contacto son datos personales: limita su acceso y no uses datos reales para pruebas académicas sin autorización.
