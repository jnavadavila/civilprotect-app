# 🔐 SISTEMA DE AUTENTICACIÓN FRONTEND - CIVILPROTECT V4.5

## 📋 DESCRIPCIÓN

Sistema completo de autenticación frontend con React, incluyendo login, registro, gestión de sesión, almacenamiento de tokens y auto-refresh.

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
frontend/src/
├── contexts/
│   └── AuthContext.jsx         # Contexto global de autenticación
├── hooks/
│   └── useAuth.js              # Hook personalizado para usar auth
├── pages/
│   ├── LoginPage.jsx           # Página de inicio de sesión
│   └── RegisterPage.jsx        # Página de registro
├── utils/
│   └── axios.js                # Instancia de axios con interceptors
├── App.js                      # Aplicación principal con Auth Provider
├── CivilProtectForm.jsx       # Usa axios configurado
└── HistoryView.jsx            # Usa axios configurado
```

---

## 🚀 CARACTERÍSTICAS IMPLEMENTADAS

### ✅ **1. Contexto de Autenticación (AuthContext)**

**Funcionalidades:**
- ✅ Almacenamiento de usuario en estado global
- ✅ Persistencia de sesión con localStorage
- ✅ Auto-carga de usuario al iniciar app
- ✅ Funciones de login/register/logout
- ✅ Refresh de tokens automático

**Uso:**
```javascript
import { useAuth } from './hooks/useAuth';

function MyComponent() {
    const { user, login, logout, isAuthenticated } = useAuth();
    
    // user contiene: { id, email, name, role, created_at }
    // isAuthenticated es boolean
}
```

---

### ✅ **2. Páginas de Login y Registro**

**LoginPage.jsx:**
- Diseño premium con gradientes
- Validación de formulario
- Manejo de errores
- Loading states
- Switch a registro

**RegisterPage.jsx:**
- Formulario completo con validación
- Selección de rol (consultor/cliente)
- Confirmación de contraseña
- Validación de email
- Mensajes de error claros

---

### ✅ **3. Axios Interceptors**

**Configuración automática (`utils/axios.js`):**

```javascript
import axios from './utils/axios';

// NO hay que incluir headers manualmente
axios.get('/analyze'); // Token incluido automáticamente

// Si token expira, se auto-refresh y reintentar
```

**Interceptor de Request:**
- Auto-incluye `Authorization: Bearer {token}` en TODAS las peticiones

**Interceptor de Response:**
- Detecta errores 401 (token expirado)
- Intenta refresh automático
- Reintenta request original con nuevo token
- Si refresh falla, redirige a login

---

### ✅ **4. Gestión de Tokens**

**Storage en localStorage:**
```
access_token    → Token JWT principal (24h)
refresh_token   → Token para renovación (7 días)
user            → Datos del usuario en JSON
```

**Auto-refresh:**
- Cuando una petición retorna 401
- Usa refresh_token para obtener nuevo access_token
- Actualiza localStorage automáticamente
- Reintenta request original
- Si falla, limpia sesión y redirige

---

### ✅ **5. Flujo Completo**

```
1. Usuario abre app
   ├─ AuthContext verifica localStorage
   ├─ Si hay token, valida con GET /auth/me
   ├─ Si válido → carga MainApp
   └─ Si inválido → muestra LoginPage

2. Usuario hace login
   ├─ POST /auth/login
   ├─ Recibe access_token + refresh_token + user
   ├─ Guarda en localStorage
   ├─ Actualiza contexto
   └─ Redirige a MainApp

3. Usuario hace request
   ├─ Axios interceptor añade token
   ├─ Si 401 → auto-refresh
   ├─ Si refresh OK → reintenta
   └─ Si refresh falla → logout

4. Usuario hace logout
   ├─ Limpia localStorage
   ├─ Limpia contexto
   └─ Redirige a LoginPage
```

---

## 🔧 CONFIGURACIÓN

### **Variables de Entorno**

Crear archivo `.env` en `/frontend`:

```env
REACT_APP_API_URL=http://localhost:8000
```

---

## 📊 TESTING DEL FLUJO

### **Test Manual:**

1. **Login:**
   ```
   Email: admin@civilprotect.com
   Password: Admin123
   ```

2. **Verificar localStorage:**
   ```javascript
   // En DevTools Console
   localStorage.getItem('access_token')
   localStorage.getItem('user')
   ```

3. **Hacer request autenticado:**
   ```javascript
   // No hay que incluir token manualmente
   axios.get('/history')
   ```

4. **Test de auto-refresh:**
   ```javascript
   // 1. Eliminar access_token
   localStorage.removeItem('access_token')
   
   // 2. Hacer request
   axios.get('/history')
   
   // ✅ Debe auto-refresh y funcionar
   ```

5. **Test de logout:**
   ```javascript
   // Verificar que se limpió todo
   localStorage.getItem('access_token')  // null
   localStorage.getItem('user')         // null
   ```

---

## ⚙️ INTEGRACIÓN CON COMPONENTES EXISTENTES

### **CivilProtectForm.jsx**
```javascript
// ANTES
import axios from 'axios';

// DESPUÉS
import axios from './utils/axios';

// Ya no hay que incluir token manualmente
```

### **HistoryView.jsx**
```javascript
// ANTES
import axios from 'axios';

// DESPUÉS
import axios from './utils/axios';

// Ya no hay que incluir token manualmente
```

---

## 🚨 SEGURIDAD

### **Protecciones Implementadas:**
- ✅ Tokens almacenados en localStorage (no en cookies por CORS)
- ✅ Validación automática de tokens al cargar app
- ✅ Auto-logout si token inválido
- ✅ Auto-refresh si token expirado
- ✅ Limpieza completa de sesión al logout
- ✅ Contraseñas enviadas solo por HTTPS (producción)

### **Consideraciones:**
- localStorage es vulnerable a XSS → sanitizar inputs
- Tokens JWT no se pueden invalidar → usar refresh de corta duración
- No almacenar datos sensibles en localStorage

---

## 📈 MEJORAS FUTURAS

- [ ] Recordar sesión (checkbox "Recordarme")
- [ ] Recuperación de contraseña
- [ ] Verificación de email
- [ ] 2FA (Two-Factor Authentication)
- [ ] Roles granulares (permisos específicos)
- [ ] Session timeout con alerta
- [ ] httpOnly cookies (si backend soporta same-origin)

---

## 📝 DOCUMENTACIÓN ADICIONAL

- `contexts/AuthContext.jsx` - Contexto completo documentado
- `utils/axios.js` - Interceptors documentados
- `pages/LoginPage.jsx` - Componente documentado
- `pages/RegisterPage.jsx` - Componente documentado

---

**Versión:** V4.5  
**Fecha:** 30 de Enero 2026  
**Estado:** ✅ COMPLETADO Y FUNCIONAL
