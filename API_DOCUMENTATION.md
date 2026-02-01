# 📘 DOCUMENTACIÓN API - CIVILPROTECT V4.5
## ENDPOINTS DE AUTENTICACIÓN Y ADMINISTRACIÓN

**Versión:** V4.5  
**Base URL:** `http://localhost:8000`  
**Producción:** `https://civilprotect-api.lunaya.com`

---

## 📑 ÍNDICE

1. [Autenticación](#autenticación)
   - POST /auth/register
   - POST /auth/login
   - POST /auth/refresh
   - GET /auth/me
2. [Administración de Usuarios](#administración-de-usuarios)
   - GET /admin/users
   - PUT /admin/users/{id}/role
   - PUT /admin/users/{id}/status
3. [Análisis](#análisis)
   - POST /analyze
   - POST /save-analysis
   - GET /history
   - DELETE /analysis/{id}

---

## 🔐 AUTENTICACIÓN

Todos los endpoints protegidos requieren un token JWT en el header:
```
Authorization: Bearer {access_token}
```

### **Roles disponibles:**
- `admin` - Acceso total + gestión de usuarios
- `consultor` - Crear y gestionar sus propios análisis
- `cliente` - Solo lectura (futuro)

---

## 1️⃣ POST /auth/register
**Descripción:** Registrar un nuevo usuario en el sistema

**Acceso:** Público (no requiere autenticación)

**Request Body:**
```json
{
  "email": "string (required, unique)",
  "name": "string (required)",
  "password": "string (required, min 6 chars)",
  "role": "string (optional, default: consultor)"
}
```

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.perez@civilprotect.com",
    "name": "Juan Pérez",
    "password": "SecurePass123",
    "role": "consultor"
  }'
```

**Response 201 (Success):**
```json
{
  "status": "success",
  "message": "Usuario registrado exitosamente",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 5,
    "email": "juan.perez@civilprotect.com",
    "name": "Juan Pérez",
    "role": "consultor",
    "is_active": true,
    "created_at": "2026-01-30T19:30:00"
  }
}
```

**Error 400 (Email duplicado):**
```json
{
  "detail": "El email ya está registrado"
}
```

---

## 2️⃣ POST /auth/login
**Descripción:** Iniciar sesión con credenciales

**Acceso:** Público (no requiere autenticación)

**Request Body:**
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.perez@civilprotect.com",
    "password": "SecurePass123"
  }'
```

**Response 200 (Success):**
```json
{
  "status": "success",
  "message": "Login exitoso",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 5,
    "email": "juan.perez@civilprotect.com",
    "name": "Juan Pérez",
    "role": "consultor",
    "is_active": true,
    "created_at": "2026-01-30T19:30:00"
  }
}
```

**Error 401 (Credenciales inválidas):**
```json
{
  "detail": "Email o contraseña incorrectos"
}
```

**Error 403 (Usuario desactivado):**
```json
{
  "detail": "Usuario desactivado. Contacte al administrador"
}
```

---

## 3️⃣ POST /auth/refresh
**Descripción:** Renovar access token usando refresh token

**Acceso:** Público (requiere refresh_token)

**Request Body:**
```json
{
  "refresh_token": "string (required)"
}
```

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response 200 (Success):**
```json
{
  "status": "success",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 5,
    "email": "juan.perez@civilprotect.com",
    "name": "Juan Pérez",
    "role": "consultor",
    "is_active": true,
    "created_at": "2026-01-30T19:30:00"
  }
}
```

**Error 401 (Token inválido):**
```json
{
  "detail": "Refresh token inválido o expirado"
}
```

---

## 4️⃣ GET /auth/me
**Descripción:** Obtener información del usuario autenticado

**Acceso:** Requiere autenticación (cualquier rol)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Ejemplo cURL:**
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response 200 (Success):**
```json
{
  "id": 5,
  "email": "juan.perez@civilprotect.com",
  "name": "Juan Pérez",
  "role": "consultor",
  "created_at": "2026-01-30T19:30:00"
}
```

**Error 401 (No autenticado):**
```json
{
  "detail": "No autenticado"
}
```

---

## 📊 ADMINISTRACIÓN DE USUARIOS

Estos endpoints solo están disponibles para usuarios con rol `admin`.

---

## 5️⃣ GET /admin/users
**Descripción:** Listar todos los usuarios del sistema

**Acceso:** Solo `admin`

**Query Parameters:**
- `limit` (int, optional, default=100) - Límite de resultados
- `offset` (int, optional, default=0) - Desplazamiento para paginación

**Ejemplo cURL:**
```bash
curl -X GET "http://localhost:8000/admin/users?limit=10&offset=0" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response 200 (Success):**
```json
{
  "status": "success",
  "total": 25,
  "count": 10,
  "users": [
    {
      "id": 1,
      "email": "admin@civilprotect.com",
      "name": "Administrador",
      "role": "admin",
      "is_active": true,
      "created_at": "2026-01-15T10:00:00",
      "analyses_count": 15
    },
    {
      "id": 2,
      "email": "consultor1@civilprotect.com",
      "name": "Consultor 1",
      "role": "consultor",
      "is_active": true,
      "created_at": "2026-01-20T14:30:00",
      "analyses_count": 8
    }
  ]
}
```

**Error 403 (No autorizado):**
```json
{
  "detail": "Acceso denegado. Roles requeridos: admin"
}
```

---

## 6️⃣ PUT /admin/users/{user_id}/role
**Descripción:** Cambiar el rol de un usuario

**Acceso:** Solo `admin`

**Path Parameters:**
- `user_id` (int, required) - ID del usuario

**Request Body:**
```json
{
  "role": "string (required: admin, consultor, cliente)"
}
```

**Ejemplo cURL:**
```bash
curl -X PUT http://localhost:8000/admin/users/5/role \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "role": "admin"
  }'
```

**Response 200 (Success):**
```json
{
  "status": "success",
  "message": "Rol actualizado de 'consultor' a 'admin'",
  "user": {
    "id": 5,
    "email": "juan.perez@civilprotect.com",
    "name": "Juan Pérez",
    "role": "admin",
    "is_active": true
  }
}
```

**Error 400 (Rol inválido):**
```json
{
  "detail": "Rol inválido. Roles permitidos: admin, consultor, cliente"
}
```

**Error 403 (Auto-modificación):**
```json
{
  "detail": "No puedes cambiar tu propio rol"
}
```

**Error 404 (Usuario no encontrado):**
```json
{
  "detail": "Usuario no encontrado"
}
```

---

## 7️⃣ PUT /admin/users/{user_id}/status
**Descripción:** Activar o desactivar un usuario

**Acceso:** Solo `admin`

**Path Parameters:**
- `user_id` (int, required) - ID del usuario

**Request Body:**
```json
{
  "is_active": "boolean (required)"
}
```

**Ejemplo cURL (Desactivar):**
```bash
curl -X PUT http://localhost:8000/admin/users/5/status \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

**Ejemplo cURL (Activar):**
```bash
curl -X PUT http://localhost:8000/admin/users/5/status \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": true
  }'
```

**Response 200 (Success - Desactivado):**
```json
{
  "status": "success",
  "message": "Usuario desactivado correctamente",
  "user": {
    "id": 5,
    "email": "juan.perez@civilprotect.com",
    "name": "Juan Pérez",
    "role": "consultor",
    "is_active": false
  }
}
```

**Response 200 (Success - Activado):**
```json
{
  "status": "success",
  "message": "Usuario activado correctamente",
  "user": {
    "id": 5,
    "email": "juan.perez@civilprotect.com",
    "name": "Juan Pérez",
    "role": "consultor",
    "is_active": true
  }
}
```

**Error 403 (Auto-desactivación):**
```json
{
  "detail": "No puedes desactivarte a ti mismo"
}
```

---

## 📝 ANÁLISIS (Endpoints principales)

---

## 8️⃣ POST /analyze
**Descripción:** Generar análisis normativo

**Acceso:** Requiere autenticación (`consultor` o `admin`)

**Request Body:**
```json
{
  "municipio": "string",
  "estado": "string",
  "tipo_inmueble": "string",
  "aforo_autorizado": "number"
}
```

**Ejemplo cURL:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "municipio": "Guadalajara",
    "estado": "Jalisco",
    "tipo_inmueble": "Centro Comercial",
    "aforo_autorizado": 500
  }'
```

**Response incluirá:** Análisis normativo completo, leyes aplicables, checklist, presupuesto estimado.

---

## 9️⃣ GET /history
**Descripción:** Obtener historial de análisis del usuario autenticado

**Acceso:** Requiere autenticación

**Ejemplo cURL:**
```bash
curl -X GET http://localhost:8000/history \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response 200:**
```json
{
  "status": "success",
  "total": 15,
  "history": [
    {
      "id": 42,
      "municipio": "Guadalajara",
      "estado": "Jalisco",
      "tipo_inmueble": "Centro Comercial",
      "created_at": "2026-01-30T18:00:00",
      "has_pdf": true,
      "pdf_path": "/pdfs/analisis_42.pdf"
    }
  ]
}
```

---

## 🔟 DELETE /analysis/{id}
**Descripción:** Eliminar un análisis (solo el propietario)

**Acceso:** Requiere autenticación + ownership

**Ejemplo cURL:**
```bash
curl -X DELETE http://localhost:8000/analysis/42 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response 200:**
```json
{
  "status": "success",
  "message": "Análisis eliminado correctamente"
}
```

**Error 403 (No es el propietario):**
```json
{
  "detail": "No tienes permiso para eliminar este análisis"
}
```

---

## 🔑 FLUJOS COMPLETOS

### **Flujo 1: Registro y Login**
```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "Test123",
    "role": "consultor"
  }'

# Guardar access_token de la respuesta
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 2. Verificar perfil
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 3. Crear análisis
curl -X POST http://localhost:8000/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "municipio": "CDMX",
    "estado": "Ciudad de México",
    "tipo_inmueble": "Hospital",
    "aforo_autorizado": 1000
  }'
```

### **Flujo 2: Administración de Usuarios (Admin)**
```bash
# 1. Login como admin
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@civilprotect.com",
    "password": "Admin123"
  }'

export ADMIN_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 2. Listar usuarios
curl -X GET http://localhost:8000/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. Cambiar rol de usuario 5 a admin
curl -X PUT http://localhost:8000/admin/users/5/role \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}'

# 4. Desactivar usuario 6
curl -X PUT http://localhost:8000/admin/users/6/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

---

## 🛡️ CÓDIGOS DE ESTADO HTTP

| Código | Significado | Cuándo se usa |
|--------|-------------|---------------|
| 200 | OK | Operación exitosa |
| 201 | Created | Registro exitoso |
| 400 | Bad Request | Datos inválidos o faltantes |
| 401 | Unauthorized | Token inválido o faltante |
| 403 | Forbidden | No tiene permisos para esta acción |
| 404 | Not Found | Recurso no encontrado |
| 500 | Server Error | Error interno del servidor |

---

## 🔐 SEGURIDAD

### **Tokens JWT:**
- **Access Token:** Válido por 24 horas
- **Refresh Token:** Válido por 7 días
- Algoritmo: HS256
- Secret Key: Configurado en `.env`

### **Headers requeridos:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

### **Variables de entorno:**
```env
SECRET_KEY=tu_clave_secreta_muy_segura
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 📞 SOPORTE

**Documentación adicional:**
- `INFORME_FINAL_FASE_1.1.1.md` - Setup de autenticación
- `INFORME_FINAL_FASE_1.1.3.md` - Sistema de roles
- `INFORME_FINAL_FASE_1.1.4.md` - Protección de endpoints

**Tests:**
- `backend/test_auth_integration.py` - 13 tests de autenticación
- `backend/test_roles_system.py` - 12 tests de roles
- `backend/test_endpoint_protection.py` - 10 tests de protección

---

**Versión:** V4.5  
**Última actualización:** 30 de Enero 2026  
**Autor:** CivilProtect Development Team
