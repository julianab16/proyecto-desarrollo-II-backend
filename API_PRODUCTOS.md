# API de Productos - Documentación para Vendedores

## Funcionalidad Implementada ✅

Como vendedor, ahora puedes:
- ✅ Crear productos y guardarlos en la base de datos
- ✅ Ver todos tus productos
- ✅ Editar **SOLO** tus propios productos
- ✅ Eliminar **SOLO** tus propios productos
- ✅ Subir imágenes de productos

## ⚠️ Importante: Seguridad y Permisos

- ✅ **Vendedores:** Pueden crear y gestionar solo sus propios productos
- ✅ **Administradores:** Pueden gestionar todos los productos
- 🔒 **NO puedes editar ni eliminar productos de otros vendedores** (recibirás error 403)
- 🔒 Cada producto está vinculado a su creador mediante el campo `owner_id`

## Endpoints Disponibles

### 1. **Crear un Producto** (POST)
```
POST /api/products/
```

**Headers requeridos:**
```json
{
  "Authorization": "Bearer <tu_token_jwt>",
  "Content-Type": "application/json"
}
```

**Cuerpo de la petición (JSON):**
```json
{
  "code": "PROD-001",
  "name": "Mi Producto",
  "description": "Descripción del producto",
  "comment": "Comentarios adicionales",
  "price": "99.99",
  "stock": 10,
  "is_active": true
}
```

**Respuesta exitosa (201 Created):**
```json
{
  "id": 1,
  "code": "PROD-001",
  "name": "Mi Producto",
  "slug": "mi-producto",
  "description": "Descripción del producto",
  "comment": "Comentarios adicionales",
  "image": null,
  "price": "99.99",
  "stock": 10,
  "is_active": true,
  "created_at": "2025-12-14T00:00:00Z",
  "updated_at": "2025-12-14T00:00:00Z",
  "owner": 1
}
```

---

### 2. **Ver Mis Productos** (GET)
```
GET /api/products/my_products/
```

**Headers requeridos:**
```json
{
  "Authorization": "Bearer <tu_token_jwt>"
}
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "code": "PROD-001",
    "name": "Mi Producto",
    "slug": "mi-producto",
    "price": "99.99",
    "stock": 10,
    ...
  },
  {
    "id": 2,
    "code": "PROD-002",
    "name": "Otro Producto",
    ...
  }
]
```

---

### 3. **Ver Todos los Productos** (GET - Público)
```
GET /api/products/
```

**No requiere autenticación** - Muestra solo productos activos para usuarios no autenticados.

---

### 4. **Ver un Producto Específico** (GET)

**Opción 1: Por Slug** (Recomendado - URLs amigables)
```
GET /api/products/<slug>/
```

**Opción 2: Por ID** (Compatibilidad con frontend existente)
```
GET /api/products/<id>/
```

**Ejemplos:**
- `GET /api/products/mi-producto/` ✅ Usando slug
- `GET /api/products/123/` ✅ Usando ID

**⚠️ Nota:** Ambos métodos funcionan. Puedes usar el que prefieras según tu frontend.

---

### 5. **Actualizar un Producto** (PUT/PATCH)

**Opción 1: Por Slug**
```
PUT /api/products/<slug>/
PATCH /api/products/<slug>/
```

**Opción 2: Por ID**
```
PUT /api/products/<id>/
PATCH /api/products/<id>/
```

**Headers requeridos:**
```json
{
  "Authorization": "Bearer <tu_token_jwt>",
  "Content-Type": "application/json"
}
```

**⚠️ IMPORTANTE: Solo puedes actualizar tus propios productos.**
- Si intentas editar un producto de otro vendedor, recibirás: **403 Forbidden**
- Solo el propietario o un administrador puede editar productos

---

### 6. **Eliminar un Producto** (DELETE)

**Opción 1: Por Slug**
```
DELETE /api/products/<slug>/
```

**Opción 2: Por ID**
```
DELETE /api/products/<id>/
```

**Headers requeridos:**
```json
{
  "Authorization": "Bearer <tu_token_jwt>"
}
```

**⚠️ IMPORTANTE: Solo puedes eliminar tus propios productos.**
- Si intentas eliminar un producto de otro vendedor, recibirás: **403 Forbidden**
- Solo el propietario o un administrador puede eliminar productos

**Solo puedes eliminar tus propios productos.**

---

### 7. **Subir Imagen de Producto** (POST/PUT con multipart/form-data)

Para subir una imagen, usa `Content-Type: multipart/form-data`:

```
POST /api/products/
```

**Form Data:**
```
code: PROD-001
name: Mi Producto
description: Descripción
price: 99.99
stock: 10
image: [archivo de imagen]
```

---

## Autenticación

Para usar estos endpoints, primero debes autenticarte:

### 1. Registrarse
```
POST /api/auth/register/
```

```json
{
  "email": "vendedor@example.com",
  "username": "vendedor1",
  "password": "password123",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

### 2. Iniciar Sesión
```
POST /api/auth/login/
```

```json
{
  "email": "vendedor@example.com",
  "password": "password123"
}
```

**Respuesta:**
```json
{
  "access": "<tu_token_jwt>",
  "refresh": "<refresh_token>"
}
```

### 3. Usar el Token

Incluye el token en todas las peticiones protegidas:
```
Authorization: Bearer <tu_token_jwt>
```

---

## Campos del Producto

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `code` | string | Sí | Código único del producto (mayúsculas, números y guiones) |
| `name` | string | Sí | Nombre del producto |
| `description` | text | No | Descripción detallada |
| `comment` | text | No | Comentarios adicionales |
| `image` | file | No | Imagen del producto |
| `price` | decimal | No | Precio (por defecto 0.00) |
| `stock` | integer | No | Cantidad en stock (por defecto 0) |
| `is_active` | boolean | No | Si el producto está activo (por defecto true) |
| `owner` | integer | Auto | Se asigna automáticamente al usuario autenticado |
| `slug` | string | Auto | Se genera automáticamente del nombre |

---

## Ejemplos con curl

### Crear un producto:
```bash
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "PROD-001",
    "name": "Producto de Prueba",
    "description": "Esta es una prueba",
    "price": "50.00",
    "stock": 5
  }'
```

### Ver mis productos:
```bash
curl -X GET http://127.0.0.1:8000/api/products/my_products/ \
  -H "Authorization: Bearer <tu_token>"
```

---

## Notas Importantes

1. ✅ **Cualquier usuario autenticado puede crear productos** (vendedores y administradores)
2. ✅ **Los productos se guardan automáticamente con el usuario como propietario**
3. 🔒 **Solo puedes editar/eliminar tus propios productos** (o ser administrador)
4. 🔒 **Intentar modificar productos ajenos devuelve error 403 Forbidden**
5. 🔄 **Compatibilidad dual: ID y Slug** - Puedes acceder a productos por ID o por slug
6. ⚠️ El campo `code` debe ser único en toda la base de datos
7. ⚠️ El código se convierte automáticamente a mayúsculas
8. ⚠️ El slug se genera automáticamente del nombre y es único
9. ⚠️ Los vendedores NO tienen permisos de administrador (is_staff=False)

## Rutas de Acceso a Productos

El API soporta **dos formas de acceder a productos individuales**:

| Método | Ejemplo | Uso |
|--------|---------|-----|
| **Por Slug** | `/api/products/mi-producto/` | URLs amigables y legibles (recomendado) |
| **Por ID** | `/api/products/123/` | Compatibilidad con frontend existente |

Ambos métodos funcionan de manera idéntica. Usa el que mejor se adapte a tu aplicación.

## Códigos de Respuesta

| Código | Descripción |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Producto creado exitosamente |
| 204 | No Content - Producto eliminado |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado |
| 403 | **Forbidden - No tienes permisos (intentaste editar producto ajeno)** |
| 404 | Not Found - Producto no encontrado |
5. ⚠️ El código se convierte automáticamente a mayúsculas
6. ⚠️ El slug se genera automáticamente del nombre y es único

---

## Servidor en Ejecución

El servidor está corriendo en: **http://127.0.0.1:8000/**

Para probar la API puedes usar:
- Postman
- Thunder Client (extensión de VS Code)
- curl
- fetch/axios desde tu frontend
