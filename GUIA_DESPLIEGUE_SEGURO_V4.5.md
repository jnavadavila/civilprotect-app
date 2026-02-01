# 🚀 Guía de Despliegue Seguro V4.5 (Sin Retrocesos)

Esta guía detalla el procedimiento exacto para desplegar la versión **V4.5 Authenticated & Hardened** de CivilProtect, garantizando la integridad de los datos históricos y la estabilidad del sistema.

---

## 📋 Prerrequisitos

1.  **Docker Desktop** instalado y corriendo.
2.  **Archivos de Datos**: Asegúrate de que `backend/data/civilprotect.db` (tu base de datos actual) existe.
3.  **Certificados SSL**:
    *   Si tienes un dominio real: Coloca `fullchain.pem` y `privkey.pem` en `nginx_gateway/certs/`.
    *   Si estás probando en local: El script generará certificados temporales automáticamente.

---

## 🛠️ Procedimiento Automático (Recomendado)

Hemos creado un script maestro que realiza todo el proceso de forma segura.

1.  Abre una terminal (PowerShell o CMD) en la carpeta del proyecto.
2.  Ejecuta el siguiente comando:

```cmd
.\SAFE_DEPLOY_V4.5.bat
```

### ¿Qué hace este script?
1.  **Validación**: Verifica que tengas los archivos necesarios.
2.  **Backup**: Crea una copia de seguridad automática de tu BD y PDFs en `civilprotect_shield_backups/`.
3.  **Infraestructura**: Levanta los contenedores Docker con las configuraciones de seguridad (IP masking, Healthchecks).
4.  **Esquema**: Inicializa la estructura de tablas en PostgreSQL.
5.  **ETL (Data)**: Ejecuta el script de migración que lee tu `civilprotect.db` (montada en solo lectura) e inserta los datos en PostgreSQL, preservando usuarios y análisis.

---

## 🔧 Procedimiento Manual (Paso a Paso)

Si prefieres tener control total o el script automático falla, sigue estos pasos:

### Paso 1: Backup
Copia manualmente `backend/data/civilprotect.db` a un lugar seguro fuera de la carpeta del proyecto.

### Paso 2: Limpieza
Detén cualquier contenedor anterior:
```bash
docker compose -f docker-compose.prod.yml down
```

### Paso 3: Despliegue de Infraestructura
Levanta los servicios en segundo plano:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Paso 4: Espera
Espera unos 30 segundos para asegurar que la base de datos PostgreSQL haya iniciado completamente. Puedes verificar con:
```bash
docker logs civilprotect-db-prod
```

### Paso 5: Inicialización y Migración
Ejecuta los comandos dentro del contenedor de backend:

1. **Crear Tablas:**
```bash
docker exec civilprotect-backend-prod python -c "from database import init_db; init_db()"
```

2. **Migrar Datos (ETL):**
```bash
docker exec civilprotect-backend-prod python etl_sqlite_to_postgres.py
```
*Deberías ver un mensaje como: "✅ ETL / Migración Completada Exitosamente."*

---

## 🔍 Verificación Post-Despliegue

1.  **Acceso Web**: Navega a `https://localhost`.
2.  **Login**: Intenta iniciar sesión con tus credenciales.
    *   Si no recuerdas tu password, el usuario admin por defecto es `admin@civilprotect.local` / `admin123` (o lo que hayas configurado en `config.py`).
3.  **Datos Históricos**: Ve a la pestaña "Historial". **Debes ver todos tus análisis anteriores.**
4.  **Nuevo Análisis**: Crea un nuevo análisis para verificar que la escritura en PostgreSQL funciona.

---

## 🆘 Solución de Problemas

*   **Error "502 Bad Gateway"**: Nginx inició antes que el Backend. Espera unos segundos y recarga la página. El nuevo Healthcheck debería prevenir esto en el futuro.
*   **Error de Certificado**: En local es normal ("La conexión no es privada"). Haz clic en Avanzado -> Continuar a localhost.
*   **Datos faltantes**: Si el historial está vacío, revisa los logs del paso de migración. Puedes re-ejecutar el script ETL sin miedo, ya que usa `ON CONFLICT DO NOTHING` (no duplicará datos).

---

**Versión del Documento:** 1.0  
**Fecha:** 31 de Enero 2026
