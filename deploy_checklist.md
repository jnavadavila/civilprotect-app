# Checklist de Despliegue a Producción

## 1. Seguridad
- [ ] **SECRET_KEY**: Cambiar valor por defecto en `.env`.
- [ ] **DB Passwords**: Usar contraseñas fuertes para PostgreSQL.
- [ ] **DEBUG**: Asegurar que `DEBUG=False` en backend.
- [ ] **SSL**: Reemplazar certificados self-signed en `nginx_gateway/certs/` por certificados reales (LetsEncrypt).

## 2. Configuración
- [ ] **Sentry DSN**: Configurar DSNs reales para monitoring.
- [ ] **OpenAI Key**: Asegurar que la API Key tiene cuota.
- [ ] **CORS**: Verificar `ALLOWED_ORIGINS` coincida con el dominio final.

## 3. Infraestructura
- [ ] **Volúmenes**: Asegurar estrategia de backup para `postgres_data_prod` y `backend/pdfs`.
- [ ] **Docker**: Verificar versión de Docker Engine en servidor.

## 4. Pasos de Deploy
1. Clonar repositorio.
2. Crear `.env` con secretos de producción.
3. Generar certificados SSL en `nginx_gateway/certs/` (fullchain.pem y privkey.pem).
4. Ejecutar: `docker compose -f docker-compose.prod.yml up -d --build`.
   - Esto compilará el frontend optimizado y el backend.
5. Ejecutar migraciones de base de datos: 
   `docker exec civilprotect-backend-prod alembic upgrade head`
6. Verificar logs:
   `docker compose -f docker-compose.prod.yml logs -f`
