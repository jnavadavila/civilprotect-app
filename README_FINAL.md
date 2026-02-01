# PROYECTO FINALIZADO: CIVILPROTECT AI 2.0

La herramienta ha sido completamente modernizada y ahora cuenta con arquitectura de producción e Inteligencia Artificial Híbrida.

## 🚀 Cómo Iniciar
Tienes dos opciones para ejecutar el sistema:

### Opción A: Modo Producción (Recomendado)
Usa este modo si tienes **Docker Desktop** instalado y corriendo. Es la versión más estable y segura.
1. Ejecuta el archivo: `RUN_PRODUCTION.bat`
2. Accede a `http://localhost:3000`
3. **NUEVO:** El sistema levantará automáticamente una base de datos **PostgreSQL**.

### Opción B: Modo Local Híbrido (Sin Docker)
Usa este modo para pruebas rápidas o si Docker no funciona en tu PC.
1. Ejecuta el archivo: `RUN_LOCAL_HYBRID.bat`
2. Esto instalará dependencias Python/Node y levantará ambos servidores manualmente.
3. *Nota:* En este modo puedes usar **PostgreSQL local** (asegúrate de que corra en puerto 5432) o **SQLite** (configurando `backend/.env`).

---

## 🧠 Nuevas Capacidades (Phase 2 Completed)

### 1. Cerebro Híbrido (`ai_service.py`)
- **Lógica Exacta**: El sistema sigue usando el motor matemático para cálculos de extintores y aforos (Cero errores).
- **Lógica Generativa**: Se conecta a la IA (OpenAI) para redactar la **Justificación Jurídica** del dictamen PDF, haciéndolo único para cada inmueble.
- *Nota: Debes poner tu API KEY en `backend/.env` para ver textos reales. Si no, verás textos de plantilla.*

### 2. Infraestructura Sólida
- **Backend**: FastAPI con saneamiento de inputs y arquitectura de servicios (`DataProvider`).
- **Frontend**: React conectado dinámicamente al API (ya no usa datos falsos pegados en código).
- **Seguridad**: Configuración CORS lista para despliegue real.
- **Base de Datos**: Migración a **PostgreSQL** con soporte para campos JSONB y alta concurrencia.

### 3. Vigilancia Normativa (`legal_crawler_bot.py`)
- Se ha implementado la base del robot que verifica disponibilidad de fuentes oficiales (DOF, Periódicos Estatales) a las 2:00 AM diariamente.

---

## 🛠️ Troubleshooting Base de Datos (PostgreSQL)

Si encuentras problemas al levantar con Docker:

1. **Puerto Ocupado:** Si el puerto 5432 está en uso, detén tu servicio local de Postgres o cambia el mapeo en `docker-compose.yml`.
2. **Conexión Rechazada en Backend:**
   - Asegúrate de que el contenedor `db` esté 'healthy'. El backend esperará a que la BD esté lista.
   - Verifica las credenciales en el archivo `.env` (Usuario: `user`, Pass: `pass`).
3. **Persistencia:** Los datos se guardan en el volumen `postgres_data`. Si necesitas resetear la BD, ejecuta: `docker volume rm civilprotect-app_postgres_data`.

---

## 📂 Estructura Final
- `/backend`: API Python, Motor de Cálculo, Servicio de IA, Migraciones DB.
- `/frontend`: Interfaz React, Cliente de API, Generación Visual de Reportes.
- `docker-compose.yml`: Orquestación Full Stack (App + DB).
