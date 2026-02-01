"""
Configuración de Rate Limiting y Seguridad
slowapi para limitar requests por usuario/IP
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
import logging
from datetime import datetime
import os

# Configurar logging de intentos de abuso
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_abuse.log'),
        logging.StreamHandler()
    ]
)

abuse_logger = logging.getLogger('abuse_detector')

# Función para obtener identificador único del usuario
def get_user_identifier(request: Request) -> str:
    """
    Obtener identificador único para rate limiting.
    Prioriza user_id si está autenticado, sino usa IP.
    """
    # Intentar obtener user_id del token JWT
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            from auth import verify_token
            payload = verify_token(token)
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except:
            pass  # Si el token es inválido, usar IP
    
    # Fallback a IP
    return f"ip:{get_remote_address(request)}"

# Configurar limiter con función personalizada
limiter = Limiter(key_func=get_user_identifier)

# Handler personalizado para rate limit exceeded
def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handler personalizado que:
    1. Logea el intento de abuso
    2. Retorna respuesta 429 con Retry-After header
    """
    identifier = get_user_identifier(request)
    endpoint = request.url.path
    
    # Logear intento de abuso
    abuse_logger.warning(
        f"RATE LIMIT EXCEEDED - Identifier: {identifier}, "
        f"Endpoint: {endpoint}, Method: {request.method}, "
        f"Time: {datetime.now().isoformat()}"
    )
    
    # Extraer tiempo de retry del mensaje de error
    retry_after = 60  # Default 60 segundos
    
    return {
        "error": "rate_limit_exceeded",
        "message": "Demasiadas peticiones. Por favor espera antes de intentar nuevamente.",
        "identifier": identifier,
        "endpoint": endpoint,
        "retry_after": retry_after
    }, 429, {"Retry-After": str(retry_after)}

# Límites específicos por endpoint (constantes)
RATE_LIMITS = {
    "analyze": "10/hour",           # Generar análisis
    "login": "5/15minute",          # Login
    "register": "3/hour",           # Registro
    "global_auth": "100/hour",      # Global para usuarios autenticados
    "global_public": "50/hour",     # Global para IPs públicas
    "admin": "200/hour",            # Endpoints de admin
    "download": "20/hour",          # Descargas de PDFs
    "history": "30/hour"            # Historial
}

# Función para obtener política de rate limit
def get_rate_limit(limit_name: str) -> str:
    """Obtener límite configurado o default"""
    return RATE_LIMITS.get(limit_name, RATE_LIMITS["global_public"])

# Función para logear acceso exitoso (opcional, para métricas)
def log_success_access(request: Request, endpoint: str):
    """Logear accesos exitosos para análisis de patrones"""
    identifier = get_user_identifier(request)
    logging.info(
        f"ACCESS - Identifier: {identifier}, "
        f"Endpoint: {endpoint}, Time: {datetime.now().isoformat()}"
    )

# Función para obtener IPs bloqueadas del log
def get_blocked_ips():
    """
    Leer el log de abusos y retornar lista de IPs con múltiples violaciones.
    Esta función puede ser llamada periódicamente para actualizar una blacklist.
    """
    blocked = {}
    try:
        with open('security_abuse.log', 'r') as f:
            for line in f:
                if 'RATE LIMIT EXCEEDED' in line and 'ip:' in line:
                    # Extraer IP del log
                    parts = line.split('ip:')
                    if len(parts) > 1:
                        ip = parts[1].split(',')[0].strip()
                        blocked[ip] = blocked.get(ip, 0) + 1
    except FileNotFoundError:
        return {}
    
    # Retornar solo IPs con más de 10 violaciones
    return {ip: count for ip, count in blocked.items() if count >= 10}

# Exportar configuraciones
__all__ = [
    'limiter',
    'custom_rate_limit_handler',
    'get_rate_limit',
    'get_user_identifier',
    'log_success_access',
    'get_blocked_ips',
    'RATE_LIMITS'
]
