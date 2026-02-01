# 🚀 GUÍA MAESTRA DE DESPLIEGUE A PRODUCCIÓN - CIVILPROTECT AI v4.5

Esta guía resuelve las "deficiencias" de configuración detectadas y asegura un despliegue exitoso, seguro y estable. Siga estos pasos estrictamente.

## 📋 1. PREPARACIÓN DEL SERVIDOR (VPS / CLOUD)
Requisitos: Linux (Ubuntu 22.04 recomendado), Docker y Docker Compose instalados.

### A. Estructura de Directorios Correcta
En el servidor, su carpeta `/app` debe tener permisos para el usuario del contenedor.
```bash
# En el servidor:
mkdir -p backend/pdfs
mkdir -p backend/logs
mkdir -p nginx_gateway/certs
mkdir -p db_data

# FIX PERMISOS CRÍTICO: El usuario interno 'civiluser' (UID variable) debe poder escribir.
# La forma más segura es dar permisos amplios O (mejor) hacer chown al UID del container.
# Para evitar complicaciones rápidas:
chmod 777 backend/pdfs
chmod 777 backend/logs
```

---

## 🔐 2. CONFIGURACIÓN DE SECRETOS (.env)
**ESTO ES LO MÁS IMPORTANTE.** No use valores por defecto.
Cree un archivo `.env` en la raíz del servidor con estos valores REALES:

```env
# --- BASE DE DATOS (POSTGRESQL) ---
# Usar contraseñas fuertes generadas aleatoriamente
DB_USER=civil_admin
DB_PASSWORD=CAMBIAR_ESTA_CONTRASEÑA_SEGURA_XYZ123
POSTGRES_DB=civilprotect

# --- SEGURIDAD ---
# Generar con: openssl rand -hex 32
JWT_SECRET_KEY=CAMBIAR_ESTO_POR_HEX_32_CHARS_REAL
ALLOWED_ORIGINS=https://midominio.com

# --- INTELIGENCIA ARTIFICIAL (CRÍTICO) ---
# SIN ESTO, LA IA VOLVERÁ AL MODO BÁSICO
OPENAI_API_KEY=sk-real-api-key-here...

# --- MONITOREO (OPCIONAL PERO RECOMENDADO) ---
SENTRY_DSN=
```

---

## 🛠️ 3. PRIMER DESPLIEGUE (RESOLVIENDO EL "BOOTSTRAP PARADOX")

El problema común es que Nginx no arranca sin certificados SSL, y Certbot no puede generar certificados si Nginx no está corriendo.

**PASO 1: Ajustar Dominios**
Edite `init_ssl.sh` y `nginx_gateway/conf.d/civilprotect.conf`.
Cambie `civilprotect.local` por su DOMINIO REAL (ej. `miempresa.com`).

**PASO 2: Ejecutar Script de Inicio**
```bash
chmod +x init_ssl.sh
./init_ssl.sh
```
*Este script automatiza la creación de un certificado temporal, arranca Nginx, pide el certificado real a Let's Encrypt y recarga Nginx.*

---

## 🚀 4. DESPLIEGUE DE MANTENIMIENTO
Después del primer inicio, para actualizar versiones:

```bash
# 1. Traer cambios
git pull

# 2. Reconstruir imágenes (importante para cambios de frontend)
docker-compose -f docker-compose.prod.yml build

# 3. Reiniciar contenedores
docker-compose -f docker-compose.prod.yml up -d
```

---

## ✅ CHECKLIST DE VERIFICACIÓN FINAL

1.  **¿Base de Datos Persistente?**
    *   Verifique que la carpeta `postgres_data_prod` (volumen) tenga datos. SQLite YA NO SE USA en producción.
    *   *Nota: Los datos de su PC local (SQLite) NO se subirán automáticamente. Empezará con una DB limpia.*

2.  **¿Firmas y PDFs?**
    *   Pruebe firmar un documento. Si falla, es 99% seguro un error de permisos en `backend/pdfs`. Ejecute `chmod 777 backend/pdfs` en el servidor.

3.  **¿Inteligencia Artificial?**
    *   Verifique los logs del backend: `docker logs civilprotect-backend-prod`.
    *   Si ve "OPENAI_API_KEY parece ser un placeholder", edite su `.env` y reinicie (`docker-compose restart backend`).

---

## 🆘 SOLUCIÓN DE PROBLEMAS COMUNES

**Error: "Connection Refused" en Frontend**
*   Verifique que `REACT_APP_API_URL` en `docker-compose.prod.yml` apunte a `/api` (path relativo) o a la URL completa HTTPS. Path relativo (`/api`) es lo mejor.

**Error: "413 Request Entity Too Large" (Subida de Imagen)**
*   Si sube firmas grandes, agregue `client_max_body_size 10M;` en `nginx_gateway/conf.d/civilprotect.conf`.

**Error: Base de datos "relation does not exist"**
*   Postgres inicia vacío. El backend debería crear las tablas automáticamente al inicio (`init_db()`). Verifique logs: `docker logs civilprotect-backend-prod`.
