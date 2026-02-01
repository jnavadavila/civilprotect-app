# Manual de Despliegue - CivilProtect AI (Producción)

Este sistema ahora cuenta con una arquitectura de grado industrial (Dockerizado) y un motor de Inteligencia Artificial Híbrido.

## 1. Configuración de Secretos
Antes de iniciar, configura tus llaves en los archivos `.env`.
*   **Backend**: Renombra `backend/.env.example` a `backend/.env` y coloca tu `OPENAI_API_KEY`.
*   **Frontend**: Renombra `frontend/.env.example` a `frontend/.env` (si cambias el puerto).

## 2. Iniciar en Modo Producción
Para levantar la versión final (no de desarrollo), usa el archivo `prod`:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

Esto levantará:
1.  **Backend (Port 8000)**: Servidor Gunicorn robusto con 4 workers concurrentes.
    *   Endpoint AI: `/analyze` (ahora conecta con OpenAI si hay key).
2.  **Frontend (Port 3000)**: Servidor Nginx de alto rendimiento sirviendo la React App compilada (Build).

## 3. Características de la "Herramienta Real"
-   **Análisis Híbrido**: Combina certeza matemática (extintores) con redacción jurídica por IA (justificación legal).
-   **Seguridad**: CORS restringido, usuario no-root en contenedores.
-   **Escalabilidad**: Listo para recibir tráfico real sin caerse (gracias a Gunicorn/Nginx).

## 4. Solución de Problemas
Si la IA dice "Texto generado por plantilla", significa que no has puesto una API Key válida en `backend/.env`. El sistema funcionará perfectamente, pero usando textos predefinidos para seguridad.
