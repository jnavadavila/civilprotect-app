"""
Test simple para verificar que el hash_password funciona correctamente
"""
import sys
import os

# Disable bytecode caching
sys.dont_write_bytecode = True

# Clear any cached modules
if 'auth.hash_handler' in sys.modules:
    del sys.modules['auth.hash_handler']
if 'auth' in sys.modules:
    del sys.modules['auth']

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n[TEST] Probando hash_password con límite de 72 bytes...\n")

from auth.hash_handler import hash_password, verify_password

# Test 1: Password normal
print("Test 1: Password normal (11 chars)")
password1 = "TestPass123"
print(f"  Password: {password1}")
print(f"  Longitud en bytes: {len(password1.encode('utf-8'))}")

try:
    hash1 = hash_password(password1)
    print(f"  Hash generado: {hash1[:50]}...")
    
    # Verificar
    if verify_password(password1, hash1):
        print("  ✅ Verificación exitosa\n")
    else:
        print("  ❌ Verificación falló\n")
except Exception as e:
    print(f"  ❌ ERROR: {e}\n")

# Test 2: Password largo (más de 72 bytes)
print("Test 2: Password muy largo (más de 72 bytes)")
password2 = "A" * 100  # 100 caracteres
print(f"  Password: {'A' * 20}... (100 caracteres)")
print(f"  Longitud en bytes: {len(password2.encode('utf-8'))}")

try:
    hash2 = hash_password(password2)
    print(f"  Hash generado: {hash2[:50]}...")
    
    # Verificar con password original
    if verify_password(password2, hash2):
        print("  ✅ Verificación exitosa (password truncado automáticamente)\n")
    else:
        print("  ❌ Verificación falló\n")
except Exception as e:
    print(f"  ❌ ERROR: {e}\n")

# Test 3: Password con caracteres Unicode
print("Test 3: Password con caracteres Unicode")
password3 = "Contraseña123"
print(f"  Password: {password3}")
print(f"  Longitud en bytes: {len(password3.encode('utf-8'))}")

try:
    hash3 = hash_password(password3)
    print(f"  Hash generado: {hash3[:50]}...")
    
    if verify_password(password3, hash3):
        print("  ✅ Verificación exitosa\n")
    else:
        print("  ❌ Verificación falló\n")
except Exception as e:
    print(f"  ❌ ERROR: {e}\n")

print("=" * 60)
print("TESTS COMPLETADOS")
print("=" * 60)
