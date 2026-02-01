"""
Test simple para diagnosticar el error 500
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("\n[DEBUG] Probando POST /auth/register con verbose output...\n")

register_data = {
    "email": "debug_test@civilprotect.com",
    "name": "Debug User",
    "password": "TestPass123",
    "role": "consultor"
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
