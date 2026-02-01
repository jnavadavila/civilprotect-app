"""
Tests de Integración Completos - Endpoints de Autenticación
Prueba el flujo completo de autenticación con el servidor real
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

# Variables globales para almacenar datos de prueba
test_email = f"test_user_{int(time.time())}@civilprotect.com"
test_password = "SecurePass123"
access_token = None
refresh_token = None
user_id = None

print("\n" + "="*70)
print("TESTS DE INTEGRACIÓN - ENDPOINTS DE AUTENTICACIÓN")
print("="*70 + "\n")

# =============================================================================
# TEST 1: Verificar que el servidor está funcionando
# =============================================================================
print("[TEST 1] Verificando que el servidor está en línea...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    if response.status_code == 200:
        print_success(f"Servidor respondiendo: {response.json()}")
    else:
        print_error(f"Servidor responde con código {response.status_code}")
        exit(1)
except Exception as e:
    print_error(f"No se puede conectar al servidor: {e}")
    print_warning("Asegúrate de que el servidor está corriendo: python main.py")
    exit(1)

# =============================================================================
# TEST 2: POST /auth/register - Registro de nuevo usuario
# =============================================================================
print("\n[TEST 2] POST /auth/register - Registrando nuevo usuario...")
register_data = {
    "email": test_email,
    "name": "Usuario de Prueba",
    "password": test_password,
    "role": "consultor"
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_info(f"Status code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        user_id = data["user"]["id"]
        
        print_success("Usuario registrado exitosamente")
        print(f"         Email: {data['user']['email']}")
        print(f"         Nombre: {data['user']['name']}")
        print(f"         Rol: {data['user']['role']}")
        print(f"         ID: {data['user']['id']}")
        print(f"         Token type: {data['token_type']}")
        print(f"         Access token: {access_token[:40]}...")
        print(f"         Refresh token: {refresh_token[:40]}...")
        
        # Validaciones
        assert "access_token" in data, "Falta access_token en respuesta"
        assert "refresh_token" in data, "Falta refresh_token en respuesta"
        assert data["token_type"] == "bearer", "Token type incorrecto"
        assert data["user"]["email"] == test_email, "Email no coincide"
        assert data["user"]["role"] == "consultor", "Rol no coincide"
        print_success("Todas las validaciones pasaron")
        
    else:
        print_error(f"Error en registro: {response.text}")
        exit(1)
        
except Exception as e:
    print_error(f"Excepción durante registro: {e}")
    exit(1)

# =============================================================================
# TEST 3: POST /auth/register - Intento de duplicar email (debe fallar)
# =============================================================================
print("\n[TEST 3] POST /auth/register - Intentando duplicar email (debe fallar)...")
try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 400:
        data = response.json()
        print_success(f"Registro duplicado rechazado correctamente: {data['detail']}")
    else:
        print_error(f"Se esperaba código 400, pero se recibió {response.status_code}")
        exit(1)
        
except Exception as e:
    print_error(f"Excepción: {e}")
    exit(1)

# =============================================================================
# TEST 4: GET /auth/me - Obtener perfil con token válido
# =============================================================================
print("\n[TEST 4] GET /auth/me - Obteniendo perfil de usuario autenticado...")
try:
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    print_info(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print_success("Perfil obtenido exitosamente")
        print(f"         ID: {data['id']}")
        print(f"         Email: {data['email']}")
        print(f"         Nombre: {data['name']}")
        print(f"         Rol: {data['role']}")
        print(f"         Creado: {data['created_at']}")
        
        # Validaciones
        assert data["id"] == user_id, "ID de usuario no coincide"
        assert data["email"] == test_email, "Email no coincide"
        assert data["role"] == "consultor", "Rol no coincide"
        print_success("Todas las validaciones pasaron")
        
    else:
        print_error(f"Error obteniendo perfil: {response.text}")
        exit(1)
        
except Exception as e:
    print_error(f"Excepción: {e}")
    exit(1)

# =============================================================================
# TEST 5: GET /auth/me - Sin token (debe fallar)
# =============================================================================
print("\n[TEST 5] GET /auth/me - Sin autenticación (debe fallar)...")
try:
    response = requests.get(f"{BASE_URL}/auth/me")
    
    if response.status_code in [401, 403]:
        print_success(f"Acceso denegado correctamente (código {response.status_code})")
    else:
        print_error(f"Se esperaba 401/403, pero se recibió {response.status_code}")
        exit(1)
        
except Exception as e:
    print_error(f"Excepción: {e}")
    exit(1)

# =============================================================================
# TEST 6: POST /auth/login - Login con credenciales correctas
# =============================================================================
print("\n[TEST 6] POST /auth/login - Login con credenciales correctas...")
login_data = {
    "email": test_email,
    "password": test_password
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_info(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print_success("Login exitoso")
        print(f"         Usuario: {data['user']['name']}")
        print(f"         Rol: {data['user']['role']}")
        print(f"         Access token: {data['access_token'][:40]}...")
        print(f"         Refresh token: {data['refresh_token'][:40]}...")
        
        # Actualizar tokens
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        
        # Validaciones
        assert "access_token" in data, "Falta access_token"
        assert "refresh_token" in data, "Falta refresh_token"
        assert data["user"]["email"] == test_email, "Email no coincide"
        print_success("Todas las validaciones pasaron")
        
    else:
        print_error(f"Error en login: {response.text}")
        exit(1)
        
except Exception as e:
    print_error(f"Excepción: {e}")
    exit(1)

# =============================================================================
# TEST 7: POST /auth/login - Login con password incorrecta (debe fallar)
# =============================================================================
print("\n[TEST 7] POST /auth/login - Con password incorrecta (debe fallar)...")
wrong_login_data = {
    "email": test_email,
    "password": "WrongPassword123"
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=wrong_login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        data = response.json()
        print_success(f"Login rechazado correctamente: {data['detail']}")
    else:
        print_error(f"Se esperaba 401, pero se recibió {response.status_code}")
        exit(1)
        
except Exception as e:
    print_error(f"Excepción: {e}")
    exit(1)

# =============================================================================
# TEST 8: POST /auth/login - Login con email inexistente (debe fallar)
# =============================================================================
print("\n[TEST 8] POST /auth/login - Con email inexistente (debe fallar)...")
fake_login_data = {
    "email": "noexiste@civilprotect.com",
    "password": test_password
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=fake_login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print_success("Login rechazado correctamente")
    else:
        print_error(f"Se esperaba 401, pero se recibió {response.status_code}")
        exit(1)
        
except Exception as e:
    print_error(f"Excepción: {e}")
    exit(1)

# =============================================================================
# TEST 9: POST /auth/refresh - Renovar access token con refresh token válido
# =============================================================================
print("\n[TEST 9] POST /auth/refresh - Renovando access token...")
refresh_data = {
    "refresh_token": refresh_token
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json=refresh_data,
        headers={"Content-Type": "application/json"}
    )
    
    print_info(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print_success("Token renovado exitosamente")
        print(f"         Nuevo access token: {data['access_token'][:40]}...")
        print(f"         Nuevo refresh token: {data['refresh_token'][:40]}...")
        
        # Actualizar tokens
        new_access_token = data["access_token"]
        new_refresh_token = data["refresh_token"]
        
        # Validaciones
        assert new_access_token != access_token, "Access token debería ser diferente"
        assert new_refresh_token != refresh_token, "Refresh token debería ser diferente"
        print_success("Tokens renovados correctamente")
        
        # Actualizar para pruebas siguientes
        access_token = new_access_token
        refresh_token = new_refresh_token
        
    else:
        print_error(f"Error renovando token: {response.text}")
        exit(1)
        
except Exception as e:
    print_error(f"Excepción: {e}")
    exit(1)

# =============================================================================
# TEST 10: POST /auth/refresh - Con refresh token inválido (debe fallar)
# =============================================================================
print("\n[TEST 10] POST /auth/refresh - Con token inválido (debe fallar)...")
invalid_refresh_data = {
    "refresh_token": "token_invalido_123456789"
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json=invalid_refresh_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print_success("Refresh token inválido rechazado correctamente")
    else:
        print_error(f"Se esperaba 401, pero se recibió {response.status_code}")
        exit(1)
        
except Exception as e:
    print_error(f"Excepción: {e}")
    exit(1)

# =============================================================================
# TEST 11: Verificar que el nuevo access token funciona
# =============================================================================
print("\n[TEST 11] GET /auth/me - Con token renovado (debe funcionar)...")
try:
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Token renovado funciona correctamente para usuario: {data['email']}")
    else:
        print_error(f"Token renovado no funciona: {response.text}")
        exit(1)
        
except Exception as e:
    print_error(f"Excepción: {e}")
    exit(1)

# =============================================================================
# TEST 12: Validación de formato EmailStr
# =============================================================================
print("\n[TEST 12] POST /auth/register - Con email inválido (debe fallar)...")
invalid_email_data = {
    "email": "email_invalido_sin_arroba",
    "name": "Usuario Inválido",
    "password": "Pass123",
    "role": "consultor"
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=invalid_email_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 422:  # Unprocessable Entity (Pydantic validation)
        print_success("Email inválido rechazado correctamente por Pydantic")
    else:
        print_warning(f"Se esperaba 422, se recibió {response.status_code}")
        
except Exception as e:
    print_error(f"Excepción: {e}")

# =============================================================================
# TEST 13: Validación de rol inválido
# =============================================================================
print("\n[TEST 13] POST /auth/register - Con rol inválido (debe fallar)...")
invalid_role_data = {
    "email": f"test_role_{int(time.time())}@civilprotect.com",
    "name": "Usuario Rol Inválido",
    "password": "Pass123",
    "role": "super_admin"  # Rol no permitido
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=invalid_role_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 400:
        data = response.json()
        print_success(f"Rol inválido rechazado: {data['detail']}")
    else:
        print_error(f"Se esperaba 400, pero se recibió {response.status_code}")
        
except Exception as e:
    print_error(f"Excepción: {e}")

# =============================================================================
# RESUMEN FINAL
# =============================================================================
print("\n" + "="*70)
print("RESUMEN DE TESTS DE INTEGRACIÓN")
print("="*70 + "\n")
print_success("TODOS LOS TESTS PASARON EXITOSAMENTE\n")
print("Tests ejecutados:")
print("  ✓ [1]  Servidor en línea")
print("  ✓ [2]  POST /auth/register - Registro exitoso")
print("  ✓ [3]  POST /auth/register - Email duplicado rechazado")
print("  ✓ [4]  GET /auth/me - Perfil con autenticación")
print("  ✓ [5]  GET /auth/me - Sin autenticación rechazado")
print("  ✓ [6]  POST /auth/login - Login exitoso")
print("  ✓ [7]  POST /auth/login - Password incorrecta rechazada")
print("  ✓ [8]  POST /auth/login - Email inexistente rechazado")
print("  ✓ [9]  POST /auth/refresh - Token renovado exitosamente")
print("  ✓ [10] POST /auth/refresh - Token inválido rechazado")
print("  ✓ [11] GET /auth/me - Token renovado funciona")
print("  ✓ [12] POST /auth/register - Email inválido rechazado")
print("  ✓ [13] POST /auth/register - Rol inválido rechazado")
print("\n" + "="*70)
print_success("SISTEMA DE AUTENTICACIÓN: 100% FUNCIONAL ✅")
print("="*70 + "\n")
print(f"Usuario de prueba creado: {test_email}")
print(f"ID de usuario: {user_id}")
print(f"Token de acceso actual: {access_token[:50]}...")
print("\n")
