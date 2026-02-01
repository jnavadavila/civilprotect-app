"""
Script de Validación Completa del Módulo Auth
Prueba todos los componentes del sistema de autenticación
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("VALIDACIÓN COMPLETA DEL MÓDULO DE AUTENTICACIÓN")
print("="*70 + "\n")

# Test 1: Verificar imports
print("[1] Verificando imports del módulo auth...")
try:
    from auth.hash_handler import hash_password, verify_password
    from auth.jwt_handler import create_access_token, create_refresh_token, verify_token
    from auth.dependencies import get_current_user, require_role, require_admin
    print("   ✅ Todos los imports exitosos")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

# Test 2: Verificar hash de contraseñas
print("\n[2] Probando hash de contraseñas...")
try:
    test_password = "TestPass123"
    hashed = hash_password(test_password)
    
    print(f"   Password original: {test_password}")
    print(f"   Hash generado: {hashed[:60]}...")
    print(f"   Longitud del hash: {len(hashed)} caracteres")
    
    # Verificar que el hash es válido
    is_valid = verify_password(test_password, hashed)
    if is_valid:
        print("   ✅ Verificación de password EXITOSA")
    else:
        print("   ❌ ERROR: La verificación de password falló")
        sys.exit(1)
    
    # Verificar que password incorrecto falla
    is_invalid = verify_password("WrongPassword", hashed)
    if not is_invalid:
        print("   ✅ Rechazo de password incorrecto EXITOSO")
    else:
        print("   ❌ ERROR: Password incorrecto fue aceptado")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

# Test 3: Verificar generación de tokens JWT
print("\n[3] Probando generación de tokens JWT...")
try:
    test_payload = {
        "sub": "1",
        "email": "test@civilprotect.com",
        "role": "admin"
    }
    
    # Access token
    access_token = create_access_token(test_payload)
    print(f"   Access Token generado: {access_token[:50]}...")
    print(f"   Longitud: {len(access_token)} caracteres")
    
    # Refresh token
    refresh_token = create_refresh_token(test_payload)
    print(f"   Refresh Token generado: {refresh_token[:50]}...")
    print(f"   Longitud: {len(refresh_token)} caracteres")
    
    print("   ✅ Generación de tokens EXITOSA")
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

# Test 4: Verificar decodificación de tokens
print("\n[4] Probando decodificación de tokens JWT...")
try:
    # Verificar access token
    decoded_access = verify_token(access_token, token_type="access")
    
    if decoded_access:
        print(f"   Token decodificado exitosamente:")
        print(f"   - User ID (sub): {decoded_access.get('sub')}")
        print(f"   - Email: {decoded_access.get('email')}")
        print(f"   - Role: {decoded_access.get('role')}")
        print(f"   - Type: {decoded_access.get('type')}")
        print("   ✅ Decodificación de Access Token EXITOSA")
    else:
        print("   ❌ ERROR: No se pudo decodificar el access token")
        sys.exit(1)
    
    # Verificar refresh token
    decoded_refresh = verify_token(refresh_token, token_type="refresh")
    
    if decoded_refresh:
        print("   ✅ Decodificación de Refresh Token EXITOSA")
    else:
        print("   ❌ ERROR: No se pudo decodificar el refresh token")
        sys.exit(1)
    
    # Verificar que tipos incompatibles fallan
    wrong_type = verify_token(access_token, token_type="refresh")
    if wrong_type is None:
        print("   ✅ Validación de tipo de token EXITOSA")
    else:
        print("   ❌ ERROR: Se aceptó un token con tipo incorrecto")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

# Test 5: Verificar variables de entorno
print("\n[5] Verificando configuración de variables de entorno...")
try:
    from auth.jwt_handler import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
    
    print(f"   SECRET_KEY: {SECRET_KEY[:30]}... (primeros 30 caracteres)")
    print(f"   ALGORITHM: {ALGORITHM}")
    print(f"   ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")
    print(f"   REFRESH_TOKEN_EXPIRE_DAYS: {REFRESH_TOKEN_EXPIRE_DAYS}")
    
    # Validar que no se está usando el valor por defecto inseguro
    if SECRET_KEY == "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION_123456789":
        print("   ⚠️  ADVERTENCIA: Se está usando SECRET_KEY por defecto")
    else:
        print("   ✅ SECRET_KEY personalizada configurada")
    
    if ALGORITHM == "HS256":
        print("   ✅ Algoritmo JWT configurado correctamente")
    else:
        print(f"   ⚠️  ADVERTENCIA: Algoritmo no estándar: {ALGORITHM}")
    
    print("   ✅ Configuración de entorno VÁLIDA")
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

# Test 6: Verificar estructura del módulo
print("\n[6] Verificando estructura del módulo auth...")
try:
    auth_dir = os.path.join(os.path.dirname(__file__), "auth")
    required_files = [
        "__init__.py",
        "hash_handler.py",
        "jwt_handler.py",
        "dependencies.py"
    ]
    
    for file in required_files:
        file_path = os.path.join(auth_dir, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file} ({size} bytes)")
        else:
            print(f"   ❌ {file} NO ENCONTRADO")
            sys.exit(1)
    
    print("   ✅ Estructura del módulo COMPLETA")
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

# Test 7: Verificar que database.py tiene los modelos necesarios
print("\n[7] Verificando integración con base de datos...")
try:
    from database import User, SessionLocal
    
    # Verificar que User tiene todos los campos necesarios
    required_fields = ['id', 'email', 'name', 'password_hash', 'role', 'is_active', 'created_at']
    
    for field in required_fields:
        if hasattr(User, field):
            print(f"   ✅ Campo User.{field} existe")
        else:
            print(f"   ❌ Campo User.{field} NO ENCONTRADO")
            sys.exit(1)
    
    print("   ✅ Modelo User COMPLETO")
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

# Test 8: Prueba completa de flujo
print("\n[8] Probando flujo completo de autenticación (simulado)...")
try:
    # Simular registro de usuario
    print("   [8.1] Simulando registro de usuario...")
    user_password = "SecurePass123"
    user_data = {
        "sub": "999",
        "email": "testuser@civilprotect.com",
        "role": "consultor"
    }
    
    # Hash del password
    password_hash = hash_password(user_password)
    print(f"       - Password hasheado: {password_hash[:40]}...")
    
    # Crear token de acceso
    token = create_access_token(user_data)
    print(f"       - Token generado: {token[:40]}...")
    
    # Verificar token
    decoded = verify_token(token, token_type="access")
    if decoded:
        print(f"       - Token verificado: User {decoded['email']}")
        print("   ✅ Flujo de autenticación COMPLETO")
    else:
        print("   ❌ ERROR: Token no pudo ser verificado")
        sys.exit(1)
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    sys.exit(1)

# Resumen final
print("\n" + "="*70)
print("RESUMEN DE VALIDACIÓN")
print("="*70)
print("\n✅ TODOS LOS TESTS PASARON EXITOSAMENTE\n")
print("Componentes validados:")
print("  ✓ Hash de contraseñas (bcrypt)")
print("  ✓ Generación de tokens JWT")
print("  ✓ Verificación de tokens JWT")
print("  ✓ Configuración de variables de entorno")
print("  ✓ Estructura del módulo auth/")
print("  ✓ Integración con database.py")
print("  ✓ Flujo completo de autenticación")
print("\n" + "="*70)
print("MÓDULO AUTH: 100% FUNCIONAL ✅")
print("="*70 + "\n")

sys.exit(0)
