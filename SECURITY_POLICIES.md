# 🔒 POLÍTICAS DE SEGURIDAD - CIVILPROTECT V4.5
## DOCUMENTACIÓN COMPLETA DE HARDENING Y RATE LIMITING

**Versión:** V4.5  
**Fecha:** 30 de Enero 2026  
**Estado:** ✅ Implementado y Activo

---

## 📋 ÍNDICE

1. [Rate Limiting](#rate-limiting)
2. [CORS Restrictivo](#cors-restrictivo)
3. [Sanitización de Inputs](#sanitización-de-inputs)
4. [Políticas de Passwords](#políticas-de-passwords)
5. [Detección de Abusos](#detección-de-abusos)
6. [IPs Bloqueadas](#ips-bloqueadas)
7. [Mantenimiento y Monitoreo](#mantenimiento-y-monitoreo)

---

## 🚦 RATE LIMITING

### **Configuración Implementada:**

| Endpoint | Límite | Identificador | Objetivo |
|----------|--------|---------------|----------|
| `/auth/register` | 3 requests/hora | IP | Prevenir spam de cuentas |
| `/auth/login` | 5 requests/15min | IP | Prevenir brute force |
| `/auth/refresh` | 100 requests/hora | user_id | Prevenir abuso de tokens |
| `/analyze` | 10 requests/hora | user_id | Proteger recursos costosos |
| `/history` | 30 requests/hora | user_id | Prevenir scraping |
|  `/download` | 20 requests/hora | user_id | Proteger bandwidth |
| `Global autenticado` | 100 requests/hora | user_id | Límite general |
| `Global público` | 50 requests/hora | IP | Límite para endpoints sin auth |

### **Identificadores:**

1. **Usuario Autenticado:** `user:{user_id}`  
   - Extraído del token JWT
   - Más granular y preciso
   
2. **IP Pública:** `ip:{remote_address}`  
   - Fallback cuando no hay autenticación
   - Usado en login/register

### **Respuesta 429 (Rate Limit Exceeded):**

```json
{
  "error": "rate_limit_exceeded",
  "message": "Demasiadas peticiones. Por favor espera antes de intentar nuevamente.",
  "identifier": "user:15",
  "endpoint": "/analyze",
  "retry_after": 60
}
```

**Headers incluidos:**
- `Retry-After`: Segundos hasta que se pueda reintentar

### **Configuración (.env):**

```bash
RATE_LIMIT_ANALYZE=10/hour
RATE_LIMIT_LOGIN=5/15minute
RATE_LIMIT_REGISTER=3/hour
```

**Archivo de configuración:** `backend/rate_limit_config.py`

---

## 🌐 CORS RESTRICTIVO

### **Política Implementada:**

**ANTES (Inseguro):**
```python
allow_origins=["*"]  # ❌ Permite CUALQUIER dominio
allow_methods=["*"]   # ❌ Permite CUALQUIER método
allow_headers=["*"]   # ❌ Permite CUALQUIER header
```

**AHORA (Seguro):**
```python
allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000"
    # Agregar dominios de producción
]
allow_credentials=True  # Permite cookies/auth
allow_methods=["GET", "POST", "PUT", "DELETE"]
allow_headers=["Authorization", "Content-Type"]
```

### **Configuración (env):**

```bash
# Desarrollo
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000

# Producción (descomentar y modificar)
# ALLOWED_ORIGINS=https://app.lunaya.com,https://civilprotect.lunaya.com
```

### **Reglas:**

1. ✅ Lista blanca de dominios específicos
2. ✅ NUNCA usar `"*"` en producción
3. ✅ Validar origen en cada request
4. ✅ Solo métodos HTTP necesarios
5. ✅ Solo headers necesarios

---

## 🧹 SANITIZACIÓN DE INPUTS

### **Protecciones Implementadas:**

#### **1. XSS (Cross-Site Scripting)**

**Biblioteca:** `bleach v6.0+`

**Campos sanitizados:**
- `custom_label` - Elimina TODOS los tags HTML
- `name` - Validación alfanumérica + caracteres seguros
- `municipio` - Solo letras, números, espacios
- `estado` - Solo letras, números, espacios

**Ejemplo:**
```python
# Input malicioso
name = "<script>alert('XSS')</script>Test User"

# Después de sanitización
name = "alert('XSS')Test User"  # Tags eliminados
# Y luego validación alfanumérica rechaza caracteres especiales
# RESULTADO: ❌ Rejected
```

#### **2. SQL Injection**

**Protección:** SQLAlchemy usa prepared statements automáticamente

**ORM en lugar de SQL directo:**
```python
# ✅ Seguro (parameterizado)
db.query(User).filter(User.email == email).first()

# ❌ Vulnerable (NO usar)
# db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

#### **3. Path Traversal**

**Sanitización de nombres de archivo:**
```python
# Input malicioso
filename = "../../etc/passwd"

# Después de sanitización
filename = "___etc_passwd"  # Caracteres peligrosos reemplazados
```

### **Validaciones Implementadas:**

| Campo | Validación | Max Length | Pattern |
|-------|------------|------------|---------|
| `email` | Email format | 255 | `^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$` |
| `name` | Alfanumérico + seguros | 100 | `^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s\-.,()]+$` |
| `municipio` | Alfanumérico + seguros | 100 | `^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s\-.,()]+$` |
| `estado` | Alfanumérico + seguros | 50 | `^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s\-.,()]+$` |
| `password` | Longitud + letra | 6-128 | Mínimo 6 caracteres, al menos 1 letra |
| `aforo_autorizado` | Positivo | N/A | > 0, ≤ 1,000,000,000 |
| `role` | Enum | N/A | `admin`, `consultor`, `cliente` |

**Archivo:** `backend/input_sanitizer.py`

---

## 🔐 POLÍTICAS DE PASSWORDS

### **Requisitos Mínimos:**

✅ Mínimo **6 caracteres**  
✅ Al menos **1 letra** (a-z, A-Z)  
✅ Máximo **128 caracteres**  
⚠️ Número recomendado pero no obligatorio (puede habilitarse)

### **Almacenamiento:**

- **Hash:** `bcrypt` con **12 rounds**
- **NO almacenar** passwords en texto plano
- **NO logger** passwords en logs
- **NO enviar** passwords en URLs

### **Ejemplo de hash:**

```python
password = "SecurePass123"
hashed = "$2b$12$OmKmO7x.OfKvr4Qkz3bG2e..."  # 60 caracteres
```

---

## 🚨 DETECCIÓN DE ABUSOS

### **Logging de Seguridad:**

**Archivo:** `security_abuse.log`

**Formato:**
```
2026-01-30 14:30:15 - abuse_detector - WARNING - 
RATE LIMIT EXCEEDED - Identifier: ip:192.168.1.100, Endpoint: /auth/login, Method: POST, Time: 2026-01-30T14:30:15
```

**Qué se logea:**
- ✅ Todos los intentos de rate limit exceeded
- ✅ Identificador (user_id o IP)
- ✅ Endpoint afectado
- ✅ Timestamp preciso
- ✅ Método HTTP

### **Análisis de Patrones:**

**Función:** `get_blocked_ips()`

Analiza el log y retorna IPs con ≥10 violaciones:

```python
{
    "192.168.1.100": 15,  # 15 violaciones
    "10.0.0.50": 12       # 12 violaciones
}
```

**Acción recomendada:** Revisar y considerar blacklist permanente

---

## 🚫 IPS BLOQUEADAS

### **Proceso de Bl oqueo:**

1. **Detección Automática:**  
   - Script analiza `security_abuse.log`
   - Identifica IPs con ≥10 violaciones
   
2. **Revisión Manual:**  
   - Admin revisa lista de IPs sospechosas
   - Verifica si son ataques reales o falsos positivos
   
3. **Blacklist (Futuro):**  
   - Implementar firewall de aplicación
   - Bloquear IPs a nivel de middleware

### **Comando de Análisis:**

```bash
python -c "from rate_limit_config import get_blocked_ips; print(get_blocked_ips())"
```

### **Whitelist (Excepciones):**

**IPs confiables (nunca bloquear):**
- `127.0.0.1` - Localhost
- `::1` - Localhost IPv6
- IPs de servidores de monitoreo
- IPs de oficinas corporativas

---

## 🛠️ MANTENIMIENTO Y MONITOREO

### **Tareas Diarias:**

- [ ] Revisar `security_abuse.log` para patrones anormales
- [ ] Verificar que el servidor esté respondiendo
- [ ] Monitorear tiempos de respuesta

### **Tareas Semanales:**

- [ ] Ejecutar `test_security_hardening.py`
- [ ] Revisar lista de IPs con múltiples violaciones
- [ ] Analizar tendencias de uso de endpoints

### **Tareas Mensuales:**

- [ ] Actualizar dependencias de seguridad (`slowapi`, `bleach`)
- [ ] Revisar y actualizar lista de ALLOWED_ORIGINS
- [ ] Auditoría completa de logs de seguridad
- [ ] Rotar logs antiguos (> 30 días)

### **Comandos Útiles:**

```bash
# Ver últimas 50 líneas del log de abusos
tail -n 50 backend/security_abuse.log

# Contar total de rate limits por endpoint
grep "RATE LIMIT EXCEEDED" backend/security_abuse.log | grep -oP 'Endpoint: \K[^ ]+' | sort | uniq -c

# IPs más frecuentes bloqueadas
grep "RATE LIMIT EXCEEDED" backend/security_abuse.log | grep -oP 'ip:\K[0-9.]+' | sort | uniq -c | sort -rn

# Ejecutar tests de seguridad
cd backend
python test_security_hardening.py
```

---

## 📊 MÉTRICAS DE SEGURIDAD

### **Indicadores Clave (KPIs):**

1. **Rate Limit Hit Rate:**
   - Objetivo: < 5% de requests totales
   - Alertar si > 10%

2. **Failed Login Attempts:**
   - Normal: < 10 por hora
   - Alertar si > 50 por hora (posible ataque)

3. **IPs con múltiples violaciones:**
   - Objetivo: 0 IPs con >10 violaciones
   - Revisar diariamente

4. **Tiempo de respuesta promedio:**
   - Objetivo: < 200ms
   - Alertar si > 500ms (posible DDoS)

---

## 🔄 ACTUALIZACIONES FUTURAS

### **Mejoras Planificadas:**

- [ ] **WAF (Web Application Firewall):**
  - Implementar Cloudflare o AWS WAF
  - Protección adicional contra DDoS
  
- [ ] **2FA (Two-Factor Authentication):**
  - SMS o app de autenticación
  - Para usuarios admin
  
- [ ] **Captcha en Login/Register:**
  - Google reCAPTCHA v3
  - Después de 3 intentos fallidos
  
- [ ] **Geo-blocking:**
  - Bloquear países con alto riesgo
  - Whitelist para países permitidos
  
- [ ] **IP Reputation Service:**
  - Integración con servicios como IPQualityScore
  - Bloqueo automático de IPs maliciosas conocidas

---

## 📞 CONTACTO Y SOPORTE

**En caso de incidente de seguridad:**

1. Detener el servidor inmediatamente
2. Revisar logs de seguridad
3. Identificar el vector de ataque
4. Aplicar parche de emergencia
5. Documentar el incidente
6. Notificar a usuarios afectados (si aplicable)

**Equipo de Seguridad:**  
- Email: security@lunaya.com
- Emergencias: [Número de contacto]

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] slowapi instalado y configurado
- [x] bleach instalado y configurado
- [x] Rate limits aplicados a endpoints críticos
- [x] CORS configurado restrictivamente
- [x] Sanitización de inputs implementada
- [x] Logging de abusos activado
- [x] Validaciones de passwords
- [x] Validaciones de tipos numéricos
- [x] Tests de seguridad creados
- [x] Documentación completa
- [x] Variables de entorno configuradas
- [x] .env.example actualizado
- [x] requirements.txt actualizado

---

**Estado del Hardening:** 🟢 **100% COMPLETADO Y ACTIVO**

---

**Versión:** V4.5  
**Última actualización:** 30 de Enero 2026, 10:15 PM CST  
**Autor:** CivilProtect Security Team
