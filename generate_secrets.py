import secrets
import string
import os

def generate_key(length=50):
    # Caracteres seguros para URL/Env (evitamos comillas o espacios que rompan parsin)
    chars = string.ascii_letters + string.digits + "-_!@#%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_simple_pass(length=24):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

print("Generando secretos criptográficamente seguros...")

env_content = f"""# GENERADO AUTOMATICAMENTE POR HARDENING SCRIPT
# Fecha: {os.popen('date /t').read().strip()}

# --- BASE DE DATOS ---
DB_USER=civil_admin
DB_PASSWORD={generate_simple_pass()}
POSTGRES_DB=civilprotect_prod

# --- APP SECURITY ---
# Usada para firmar cookies/sesiones (si aplica)
SECRET_KEY={generate_key(64)}

# Usada para firmar JWTs (CRITICO)
JWT_SECRET_KEY={generate_key(64)}

# --- CONFIGURACION ---
ENV=production
DEBUG=False
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=https://civilprotect.local,https://app.tu-dominio.com

# --- EXTERNAL SERVICES ---
# (Rellenar con valores reales)
OPENAI_API_KEY=sk-....
SENTRY_DSN_BACKEND=https://example@sentry.io/1
SENTRY_DSN_FRONTEND=https://example@sentry.io/2
"""

output_file = ".env.prod"
with open(output_file, "w") as f:
    f.write(env_content)

print(f"\n[EXITO] Archivo '{output_file}' creado.")
print("INSTRUCCIONES:")
print("1. Revisa el archivo y agrega tus API Keys (OpenAI, Sentry).")
print("2. Renómbralo a '.env' antes de ejecutar docker-compose up.")
print("3. NUNCA comitees este archivo al repositorio git.")
