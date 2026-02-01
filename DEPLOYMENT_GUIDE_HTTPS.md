# 🔐 GUÍA DE DEPLOYMENT CON HTTPS
## CIVILPROTECT V4.5 - CONFIGURACIÓN DE PRODUCCIÓN CON SSL/TLS

**Versión:** V4.5  
**Fecha:** 30 de Enero 2026  
**Estado:** Guía Completa de Deployment

---

## 📋 ÍNDICE

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración del Servidor](#configuración-del-servidor)
3. [Instalación de Nginx](#instalación-de-nginx)
4. [Obtención de Certificados SSL Let's Encrypt)](#obtención-de-certificados-ssl)
5. [Configuración de Nginx](#configuración-de-nginx)
6. [Despliegue del Backend](#despliegue-del-backend)
7. [Verificación y Testing](#verificación-y-testing)
8. [Renovación Automática de Certificados](#renovación-automática)
9. [Monitoreo y Logs](#monitoreo-y-logs)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 REQUISITOS PREVIOS

### **Servidor:**
- ✅ Ubuntu 20.04/22.04 LTS o Debian 11/12 (recomendado)
- ✅ CentOS/RHEL 8+ (alternativa)
- ✅ Mínimo 2GB RAM, 2 CPU cores
- ✅ 20GB de espacio en disco
- ✅ Acceso root o sudo

### **Dominio:**
- ✅ Dominio registrado (ej: api.civilprotect.com)
- ✅ DNS configurado apuntando al servidor (A record)
- ✅ Acceso al panel de control del dominio

### **Software:**
- ✅ Python 3.9+
- ✅ Nginx 1.18+
- ✅ Certbot (Let's Encrypt client)
- ✅ Git

### **Puertos:**
- ✅ Puerto 80 (HTTP) - abierto temporalmente para verificación
- ✅ Puerto 443 (HTTPS) - abierto permanentemente
- ✅ Puerto 8000 (Backend) - solo localhost

---

## 🖥️ CONFIGURACIÓN DEL SERVIDOR

### **1. Actualizar Sistema**

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### **2. Crear Usuario de Aplicación**

```bash
# Crear usuario dedicado (mejor práctica de seguridad)
sudo adduser civilprotect
sudo usermod -aG sudo civilprotect

# Cambiar a ese usuario
su - civilprotect
```

### **3. Configurar Firewall (UFW - Ubuntu)**

```bash
# Instalar UFW si no está
sudo apt install ufw

# Configurar reglas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp    # HTTP (temporal para Let's Encrypt)
sudo ufw allow 443/tcp   # HTTPS

# Habilitar firewall
sudo ufw enable
sudo ufw status
```

### **4. Configurar Firewall (firewalld - CentOS)**

```bash
# Configurar reglas
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

---

## 📦 INSTALACIÓN DE NGINX

### **Ubuntu/Debian:**

```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

### **CentOS/RHEL:**

```bash
sudo yum install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

### **Verificar Instalación:**

```bash
nginx -v
# Salida esperada: nginx version: nginx/1.18.0

curl http://localhost
# Debería mostrar la página de bienvenida de nginx
```

---

## 🔐 OBTENCIÓN DE CERTIFICADOS SSL (LET'S ENCRYPT)

### **1. Instalar Certbot**

**Ubuntu/Debian:**
```bash
sudo apt install certbot python3-certbot-nginx -y
```

**CentOS/RHEL:**
```bash
sudo yum install certbot python3-certbot-nginx -y
```

### **2. Verificar DNS**

Antes de continuar, verifica que tu dominio apunte al servidor:

```bash
dig +short api.civilprotect.com
# Debe mostrar la IP de tu servidor

# O con nslookup
nslookup api.civilprotect.com
```

### **3. Obtener Certificado SSL**

**Método 1: Automático con plugin de nginx**

```bash
# Reemplazar api.civilprotect.com con tu dominio
sudo certbot --nginx -d api.civilprotect.com -d www.api.civilprotect.com

# Certbot preguntará:
# - Email (para notificaciones de expiración)
# - Aceptar terms of service
# - Compartir email (opcional)
# - Redirect HTTP → HTTPS (elegir: 2 - Redirect)
```

**Método 2: Standalone (si nginx aún no está configurado)**

```bash
# Detener nginx temporalmente
sudo systemctl stop nginx

# Obtener certificado
sudo certbot certonly --standalone -d api.civilprotect.com -d www.api.civilprotect.com

# Reiniciar nginx
sudo systemctl start nginx
```

### **4. Verificar Certificados**

```bash
# Certificados se guardan en:
sudo ls -la /etc/letsencrypt/live/api.civilprotect.com/

# Archivos importantes:
# - fullchain.pem (certificado + cadena)
# - privkey.pem (clave privada)
# - chain.pem (cadena de certificación)
# - cert.pem (solo certificado)
```

### **5. Test de Renovación**

```bash
# Probar renovación (dry-run)
sudo certbot renew --dry-run

# Si todo está OK, verás:
# Congratulations, all simulated renewals succeeded
```

---

## ⚙️ CONFIGURACIÓN DE NGINX

### **1. Clonar Proyecto**

```bash
cd /home/civilprotect
git clone https://github.com/tu-usuario/civilprotect-app.git
cd civilprotect-app
```

### **2. Copiar Configuración de Nginx**

```bash
# Copiar archivo de configuración
sudo cp nginx.conf /etc/nginx/sites-available/civilprotect

# IMPORTANTE: Editar el archivo para reemplazar dominios
sudo nano /etc/nginx/sites-available/civilprotect

# Buscar y reemplazar:
# api.civilprotect.com → tu-dominio.com
```

### **3. Crear Enlace Simbólico**

```bash
# Activar configuración
sudo ln -s /etc/nginx/sites-available/civilprotect /etc/nginx/sites-enabled/

# Eliminar configuración default (opcional)
sudo rm /etc/nginx/sites-enabled/default
```

### **4. Verificar Configuración**

```bash
# Test de sintaxis
sudo nginx -t

# Salida esperada:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### **5. Recargar Nginx**

```bash
sudo systemctl reload nginx

# O reiniciar completamente
sudo systemctl restart nginx

# Verificar estado
sudo systemctl status nginx
```

---

## 🚀 DESPLIEGUE DEL BACKEND

### **1. Instalar Dependencias**

```bash
cd /home/civilprotect/civilprotect-app/backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### **2. Configurar Variables de Entorno**

```bash
# Copiar template
cp .env.example .env

# Editar .env con valores de producción
nano .env

# IMPORTANTE: Configurar:
# - JWT_SECRET_KEY (generar nuevo con: python -c "import secrets; print(secrets.token_hex(32))")
# - OPENAI_API_KEY
# - ACCESS_TOKEN_EXPIRE_MINUTES=30
# - DEBUG=False
# - ENV=production
```

### **3. Verificar Configuración**

```bash
# Ejecutar script de verificación
python check_env.py

# Debe mostrar:
# ✅ 6/7 checks pasados
# ⚠️  CONFIGURACIÓN FUNCIONAL CON ADVERTENCIAS
```

### **4. Crear Servicio Systemd**

```bash
sudo nano /etc/systemd/system/civilprotect.service
```

**Contenido:**
```ini
[Unit]
Description=CivilProtect API
After=network.target

[Service]
Type=notify
User=civilprotect
Group=civilprotect
WorkingDirectory=/home/civilprotect/civilprotect-app/backend
Environment="PATH=/home/civilprotect/civilprotect-app/backend/venv/bin"
ExecStart=/home/civilprotect/civilprotect-app/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4

# Restart
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=append:/var/log/civilprotect/app.log
StandardError=append:/var/log/civilprotect/error.log

[Install]
WantedBy=multi-user.target
```

### **5. Crear Directorio de Logs**

```bash
sudo mkdir -p /var/log/civilprotect
sudo chown civilprotect:civilprotect /var/log/civilprotect
```

### **6. Habilitar e Iniciar Servicio**

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable civilprotect

# Iniciar servicio
sudo systemctl start civilprotect

# Verificar estado
sudo systemctl status civilprotect

# Ver logs en tiempo real
sudo journalctl -u civilprotect -f
```

---

## ✅ VERIFICACIÓN Y TESTING

### **1. Test de Conectividad**

```bash
# Test local
curl http://localhost:8000

# Test HTTPS
curl https://api.civilprotect.com

# Debe retornar JSON del API
```

### **2. Test de Security Headers**

```bash
# Desde el servidor
curl -I https://api.civilprotect.com

# Verificar headers:
# - Strict-Transport-Security
# - X-Frame-Options
# - X-Content-Type-Options
# - Content-Security-Policy
```

### **3. Test de SSL**

```bash
# Verificar configuración SSL
openssl s_client -connect api.civilprotect.com:443 -servername api.civilprotect.com

# O usar herramientas online:
# https://www.ssllabs.com/ssltest/
# (Objetivo: Grado A o A+)
```

### **4. Test de Security Headers Online**

```bash
# Verificar en:
# https://securityheaders.com/?q=https://api.civilprotect.com

# Objetivo: Grado A
```

### **5. Test de Redirect HTTP→HTTPS**

```bash
# Debe redirigir automáticamente
curl -I http://api.civilprotect.com

# Verificar:
# HTTP/1.1 301 Moved Permanently
# Location: https://api.civilprotect.com/
```

### **6. Test de API Endpoints**

```bash
# Health check
curl https://api.civilprotect.com/

# Login
curl -X POST https://api.civilprotect.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

---

## 🔄 RENOVACIÓN AUTOMÁTICA DE CERTIFICADOS

### **1. Configurar Cron Job**

Let's Encrypt configura automáticamente la renovación, pero verifica:

```bash
# Ver timer de certbot
sudo systemctl list-timers | grep certbot

# Debería mostrar:
# certbot.timer ... left ... ago certbot.service
```

### **2. Renovación Manual (si es necesario)**

```bash
# Renovar certificados
sudo certbot renew

# Recargar nginx después
sudo systemctl reload nginx
```

### **3. Hook Post-Renovación**

Para recargar nginx automáticamente después de renovar:

```bash
sudo nano /etc/letsencrypt/renewal-hooks/post/reload-nginx.sh
```

**Contenido:**
```bash
#!/bin/bash
systemctl reload nginx
```

```bash
# Hacer ejecutable
sudo chmod +x /etc/letsencrypt/renewal-hooks/post/reload-nginx.sh
```

---

## 📊 MONITOREO Y LOGS

### **1. Logs de Nginx**

```bash
# Access log
sudo tail -f /var/log/nginx/civilprotect_access.log

# Error log
sudo tail -f /var/log/nginx/civilprotect_error.log

# Analizar logs
sudo cat /var/log/nginx/civilprotect_access.log | grep "429" | wc -l
# Cuenta requests con rate limit
```

### **2. Logs de la Aplicación**

```bash
# App log
sudo tail -f /var/log/civilprotect/app.log

# Error log
sudo tail -f /var/log/civilprotect/error.log

# Systemd journal
sudo journalctl -u civilprotect -n 100 --no-pager
```

### **3. Monitoreo de Recursos**

```bash
# CPU y memoria
htop

# Nginx
sudo systemctl status nginx

# Backend
sudo systemctl status civilprotect

# Conexiones activas
sudo netstat -tunlp | grep nginx
sudo netstat -tunlp | grep 8000
```

### **4. Configurar Alertas (Opcional)**

Usar herramientas como:
- **Uptime Robot** (gratuito): https://uptimerobot.com/
- **StatusCake** (gratuito): https://www.statuscake.com/
- **Prometheus + Grafana** (avanzado)

---

## 🔧 TROUBLESHOOTING

### **Problema 1: Nginx no inicia**

```bash
# Ver errores
sudo nginx -t
sudo journalctl -xe

# Verificar configuración
sudo nginx -T | less

# Verificar permisos de certificados
sudo ls -la /etc/letsencrypt/live/api.civilprotect.com/
```

### **Problema 2: 502 Bad Gateway**

```bash
# Verificar que el backend esté corriendo
sudo systemctl status civilprotect
curl http://localhost:8000

# Ver logs del backend
sudo journalctl -u civilprotect -n 50

# Reiniciar backend
sudo systemctl restart civilprotect
```

### **Problema 3: Certificado no válido**

```bash
# Renovar certificado
sudo certbot renew --force-renewal

# Verificar fechas
sudo certbot certificates

# Verificar con openssl
echo | openssl s_client -servername api.civilprotect.com -connect api.civilprotect.com:443 2>/dev/null | openssl x509 -noout -dates
```

### **Problema 4: CORS errors**

```bash
# Verificar configuración de CORS en .env
cat /home/civilprotect/civilprotect-app/backend/.env | grep ALLOWED_ORIGINS

# Debe incluir el dominio del frontend
ALLOWED_ORIGINS=https://civilprotect.com,https://app.civilprotect.com

# Reiniciar backend
sudo systemctl restart civilprotect
```

### **Problema 5: Rate limiting muy agresivo**

```bash
# Editar rate limits en nginx.conf
sudo nano /etc/nginx/sites-available/civilprotect

# Buscar: limit_req_zone
# Ajustar el rate (ej: rate=100r/m → rate=200r/m)

# Recargar nginx
sudo nginx -t && sudo systemctl reload nginx
```

---

## 📚 RECURSOS ADICIONALES

### **Documentación:**
- Nginx: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/docs/
- Certbot: https://certbot.eff.org/
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

### **Herramientas de Testing:**
- SSL Labs: https://www.ssllabs.com/ssltest/
- Security Headers: https://securityheaders.com/
- HTTP Security: https://httpsecurityreport.com/

### **Mejores Prácticas:**
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Mozilla SSL Config: https://ssl-config.mozilla.org/

---

## ✅ CHECKLIST DE DEPLOYMENT

- [ ] Servidor configurado y actualizado
- [ ] Firewall configurado (puertos 80, 443)
- [ ] Nginx instalado y corriendo
- [ ] Dominio apuntando al servidor (DNS)
- [ ] Certificados SSL obtenidos de Let's Encrypt
- [ ] nginx.conf configurado y testeado
- [ ] Backend desplegado con systemd
- [ ] Variables de entorno configuradas (.env)
- [ ] Servicio civilprotect iniciado y habilitado
- [ ] Test de HTTPS exitoso
- [ ] Test de redirect HTTP→HTTPS exitoso
- [ ] Test de security headers exitoso (Grado A)
- [ ] Test de SSL exitoso (Grado A/A+)
- [ ] Logs configurados y monitoreados
- [ ] Renovación automática de certificados verificada
- [ ] Backup configurado (base de datos, .env)
- [ ] Monitoreo/alertas configurado

---

## 🎯 RESULTADO ESPERADO

Después de seguir esta guía, deberías tener:

✅ API accesible vía HTTPS en tu dominio  
✅ Certificado SSL válido y confiable  
✅ Grado A en SSL Labs y Security Headers  
✅ Redirect automático HTTP→HTTPS  
✅ Security headers implementados  
✅ Rate limiting activo  
✅ Logs configurados y monitoreados  
✅ Renovación automática de certificados  
✅ Backend corriendo como servicio systemd  

---

**Versión:** CivilProtect V4.5  
**Última actualización:** 30 de Enero 2026  
**Autor:** CivilProtect DevOps Team
