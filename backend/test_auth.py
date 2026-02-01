"""
Script de Prueba de Endpoints de Autenticación
Prueba el flujo completo: register, login, get profile
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "="*60)
print("PRUEBA DE AUTENTICACIÓN - CivilProtect V4.5")
print("="*60 + "\n")

# Test 1: Verificar que el servidor está funcionando
print("[1] Verificando servidor...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   Estado: {response.status_code} - OK")
    print(f"   Respuesta: {response.json()}")
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 2: Registro de usuario nuevo
print("\n[2] Registrando nuevo usuario...")
register_data = {
    "email": "admin@civilprotect.com",
    "name": "Administrator",
    "password": "Admin123SecurePass",
    "role": "admin"
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Estado: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"   [OK] Usuario registrado exitosamente")
        print(f"   ID: {data['user']['id']}")
        print(f"   Email: {data['user']['email']}")
        print(f"   Nombre: {data['user']['name']}")
        print(f"   Rol: {data['user']['role']}")
        print(f"   Access Token: {data['access_token'][:50]}...")
        access_token = data['access_token']
    else:
        print(f"   Respuesta: {response.json()}")
        # Si ya existe, intentar login
        print("\n   El usuario ya existe, intentando login...")
        
        # Test 3: Login
        print("\n[3] Iniciando sesión con usuario existente...")
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Login exitoso")
            print(f"   Usuario: {data['user']['name']}")
            print(f"   Rol: {data['user']['role']}")
            print(f"   Access Token: {data['access_token'][:50]}...")
            access_token = data['access_token']
        else:
            print(f"   ERROR: {response.json()}")
            exit(1)
            
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test 4: Obtener perfil de usuario autenticado
print("\n[4] Obteniendo perfil de usuario autenticado...")
try:
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] Perfil obtenido exitosamente")
        print(f"   ID: {data['id']}")
        print(f"   Email: {data['email']}")
        print(f"   Nombre: {data['name']}")
        print(f"   Rol: {data['role']}")
        print(f"   Creado: {data['created_at']}")
    else:
        print(f"   ERROR: {response.json()}")
        
except Exception as e:
    print(f"   ERROR: {e}")

# Test 5: Intentar acceder sin autenticación (debe fallar)
print("\n[5] Intentando acceder sin token (debe fallar)...")
try:
    response = requests.get(f"{BASE_URL}/auth/me")
    
    if response.status_code == 403 or response.status_code == 401:
        print(f"   [OK] Acceso denegado correctamente (sin token)")
        print(f"   Estado: {response.status_code}")
    else:
        print(f"   ERROR INESPERADO: {response.status_code}")
        
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "="*60)
print("PRUEBAS COMPLETADAS")
print("="*60 + "\n")
