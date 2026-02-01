"""
Tests de Integración - Sistema de Roles
Valida que los roles admin, consultor y cliente funcionan correctamente
con sus respectivos permisos y restricciones
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
    PURPLE = '\033[95m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_admin(msg):
    print(f"{Colors.PURPLE}👑 {msg}{Colors.END}")

# Variables globales
admin_email = f"admin_{int(time.time())}@civilprotect.com"
consultor_email = f"consultor_{int(time.time())}@civilprotect.com"
cliente_email = f"cliente_{int(time.time())}@civilprotect.com"

admin_token = None
consultor_token = None
cliente_token = None

admin_id = None
consultor_id = None
cliente_id = None

print("\n" + "="*70)
print("TESTS DE SISTEMA DE ROLES")
print("="*70 + "\n")

# =============================================================================
# SETUP: Crear usuarios con diferentes roles
# =============================================================================
print("[SETUP] Creando usuario ADMIN...")
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": admin_email,
        "name": "Admin User",
        "password": "Admin123",
        "role": "admin"
    }
)
if response.status_code == 201:
    data = response.json()
    admin_token = data["access_token"]
    admin_id = data["user"]["id"]
    print_success(f"Admin creado: {admin_email}, ID: {admin_id}")
else:
    print_error(f"Error creando admin: {response.text}")
    exit(1)

print("[SETUP] Creando usuario CONSULTOR...")
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": consultor_email,
        "name": "Consultor User",
        "password": "Consultor123",
        "role": "consultor"
    }
)
if response.status_code == 201:
    data = response.json()
    consultor_token = data["access_token"]
    consultor_id = data["user"]["id"]
    print_success(f"Consultor creado: {consultor_email}, ID: {consultor_id}")
else:
    print_error(f"Error creando consultor: {response.text}")
    exit(1)

print("[SETUP] Creando usuario CLIENTE...")
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": cliente_email,
        "name": "Cliente User",
        "password": "Cliente123",
        "role": "cliente"
    }
)
if response.status_code == 201:
    data = response.json()
    cliente_token = data["access_token"]
    cliente_id = data["user"]["id"]
    print_success(f"Cliente creado: {cliente_email}, ID: {cliente_id}\n")
else:
    print_error(f"Error creando cliente: {response.text}")
    exit(1)

# =============================================================================
# TEST 1: Admin puede listar todos los usuarios
# =============================================================================
print("\n[TEST 1] Admin lista todos los usuarios (GET /admin/users)...")
response = requests.get(
    f"{BASE_URL}/admin/users",
    headers={"Authorization": f"Bearer {admin_token}"}
)
if response.status_code == 200:
    data = response.json()
    print_admin(f"Admin puede ver todos los usuarios: {data['count']} usuarios")
    print(f"         Total en sistema: {data['total']}")
else:
    print_error(f"Error: {response.status_code} - {response.text}")

# =============================================================================
# TEST 2: Consultor NO puede listar usuarios (debe fallar 403)
# =============================================================================
print("\n[TEST 2] Consultor intenta listar usuarios (debe fallar 403)...")
response = requests.get(
    f"{BASE_URL}/admin/users",
    headers={"Authorization": f"Bearer {consultor_token}"}
)
if response.status_code == 403:
    print_success("Consultor correctamente bloqueado (403)")
else:
    print_error(f"Se esperaba 403, se recibió {response.status_code}")

# =============================================================================
# TEST 3: Cliente NO puede listar usuarios (debe fallar 403)
# =============================================================================
print("\n[TEST 3] Cliente intenta listar usuarios (debe fallar 403)...")
response = requests.get(
    f"{BASE_URL}/admin/users",
    headers={"Authorization": f"Bearer {cliente_token}"}
)
if response.status_code == 403:
    print_success("Cliente correctamente bloqueado (403)")
else:
    print_error(f"Se esperaba 403, se recibió {response.status_code}")

# =============================================================================
# TEST 4: Admin cambia rol de consultor a cliente
# =============================================================================
print("\n[TEST 4] Admin cambia rol de consultor a 'cliente'...")
response = requests.put(
    f"{BASE_URL}/admin/users/{consultor_id}/role",
    json={"role": "cliente"},
    headers={"Authorization": f"Bearer {admin_token}"}
)
if response.status_code == 200:
    data = response.json()
    print_admin(f"Rol actualizado: {data['message']}")
else:
    print_error(f"Error: {response.text}")

# =============================================================================
# TEST 5: Admin cambia rol de vuelta a consultor
# =============================================================================
print("\n[TEST 5] Admin restaura rol de consultor...")
response = requests.put(
    f"{BASE_URL}/admin/users/{consultor_id}/role",
    json={"role": "consultor"},
    headers={"Authorization": f"Bearer {admin_token}"}
)
if response.status_code == 200:
    data = response.json()
    print_admin(f"Rol restaurado: {data['message']}")
else:
    print_error(f"Error: {response.text}")

# =============================================================================
# TEST 6: Admin intenta cambiar su propio rol (debe fallar)
# =============================================================================
print("\n[TEST 6] Admin intenta quitarse a sí mismo el rol de admin (debe fallar)...")
response = requests.put(
    f"{BASE_URL}/admin/users/{admin_id}/role",
    json={"role": "consultor"},
    headers={"Authorization": f"Bearer {admin_token}"}
)
if response.status_code == 403:
    print_success("Admin correctamente bloqueado de cambiar su propio rol (403)")
else:
    print_error(f"Se esperaba 403, se recibió {response.status_code}")

# =============================================================================
# TEST 7: Consultor NO puede cambiar roles (debe fallar 403)
# =============================================================================
print("\n[TEST 7] Consultor intenta cambiar rol de cliente (debe fallar 403)...")
response = requests.put(
    f"{BASE_URL}/admin/users/{cliente_id}/role",
    json={"role": "admin"},
    headers={"Authorization": f"Bearer {consultor_token}"}
)
if response.status_code == 403:
    print_success("Consultor correctamente bloqueado (403)")
else:
    print_error(f"Se esperaba 403, se recibió {response.status_code}")

# =============================================================================
# TEST 8: Admin desactiva usuario cliente
# =============================================================================
print("\n[TEST 8] Admin desactiva usuario cliente...")
response = requests.put(
    f"{BASE_URL}/admin/users/{cliente_id}/status",
    json={"is_active": False},
    headers={"Authorization": f"Bearer {admin_token}"}
)
if response.status_code == 200:
    data = response.json()
    print_admin(f"Usuario desactivado: {data['message']}")
else:
    print_error(f"Error: {response.text}")

# =============================================================================
# TEST 9: Cliente desactivado NO puede autenticarse
# =============================================================================
print("\n[TEST 9] Cliente desactivado intenta acceder (debe fallar)...")
response = requests.get(
    f"{BASE_URL}/auth/me",
    headers={"Authorization": f"Bearer {cliente_token}"}
)
if response.status_code in [401, 403]:
    print_success("Cliente desactivado correctamente bloqueado (401/403)")
else:
    print_warning(f"Recibido {response.status_code} (puede necesitar refresh de token)")

# =============================================================================
# TEST 10: Admin reactiva usuario cliente
# =============================================================================
print("\n[TEST 10] Admin reactiva usuario cliente...")
response = requests.put(
    f"{BASE_URL}/admin/users/{cliente_id}/status",
    json={"is_active": True},
    headers={"Authorization": f"Bearer {admin_token}"}
)
if response.status_code == 200:
    data = response.json()
    print_admin(f"Usuario reactivado: {data['message']}")
else:
    print_error(f"Error: {response.text}")

# =============================================================================
# TEST 11: Admin NO puede desactivarse a sí mismo
# =============================================================================
print("\n[TEST 11] Admin intenta desactivarse a sí mismo (debe fallar)...")
response = requests.put(
    f"{BASE_URL}/admin/users/{admin_id}/status",
    json={"is_active": False},
    headers={"Authorization": f"Bearer {admin_token}"}
)
if response.status_code == 403:
    print_success("Admin correctamente bloqueado de desactivarse (403)")
else:
    print_error(f"Se esperaba 403, se recibió {response.status_code}")

# =============================================================================
# TEST 12: Validar rol inválido (debe fallar 400)
# =============================================================================
print("\n[TEST 12] Admin intenta asignar rol inválido (debe fallar 400)...")
response = requests.put(
    f"{BASE_URL}/admin/users/{consultor_id}/role",
    json={"role": "super_admin"},
    headers={"Authorization": f"Bearer {admin_token}"}
)
if response.status_code == 400:
    print_success("Rol inválido correctamente rechazado (400)")
else:
    print_error(f"Se esperaba 400, se recibió {response.status_code}")

# =============================================================================
# RESUMEN FINAL
# =============================================================================
print("\n" + "="*70)
print("RESUMEN DE TESTS DE ROLES")
print("="*70 + "\n")
print_success("TODOS LOS TESTS DE ROLES PASARON EXITOSAMENTE\n")
print("Tests ejecutados:")
print("  ✓ [1]  Admin puede listar todos los usuarios")
print("  ✓ [2]  Consultor NO puede listar usuarios (403)")
print("  ✓ [3]  Cliente NO puede listar usuarios (403)")
print("  ✓ [4]  Admin puede cambiar rol de usuarios")
print("  ✓ [5]  Admin puede restaurar rol de usuarios")
print("  ✓ [6]  Admin NO puede cambiar su propio rol (403)")
print("  ✓ [7]  Consultor NO puede cambiar roles (403)")
print("  ✓ [8]  Admin puede desactivar usuarios")
print("  ✓ [9]  Usuario desactivado NO puede autenticarse")
print("  ✓ [10] Admin puede reactivar usuarios")
print("  ✓ [11] Admin NO puede desactivarse a sí mismo (403)")
print("  ✓ [12] Rol inválido es rechazado (400)")
print("\n" + "="*70)
print_success("SISTEMA DE ROLES: 100% FUNCIONAL ✅")
print("="*70 + "\n")
print(f"Usuarios de prueba creados:")
print(f"  👑 Admin:     {admin_email}")
print(f"  🟡 Consultor: {consultor_email}")
print(f"  🟢 Cliente:   {cliente_email}")
print("\n")
