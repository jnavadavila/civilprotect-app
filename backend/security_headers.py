"""
Middleware de Seguridad - Security Headers
Implementa headers de seguridad HTTP para protección contra ataques comunes
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware que agrega headers de seguridad HTTP a todas las respuestas.
    
    Headers implementados:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security (HSTS)
    - Content-Security-Policy (CSP)
    - X-Permitted-Cross-Domain-Policies: none
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: restricciones de features del browser
    """
    
    def __init__(self, app, enable_hsts: bool = True, hsts_max_age: int = 31536000):
        """
        Inicializar middleware de seguridad.
        
        Args:
            app: Aplicación FastAPI
            enable_hsts: Si True, habilita HSTS (solo para HTTPS)
            hsts_max_age: Tiempo en segundos para HSTS (default: 1 año)
        """
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        logger.info("SecurityHeadersMiddleware inicializado")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesar request y agregar headers de seguridad a la respuesta.
        
        Args:
            request: Request HTTP entrante
            call_next: Siguiente middleware/endpoint
            
        Returns:
            Response con headers de seguridad agregados
        """
        # Procesar la request normalmente
        response = await call_next(request)
        
        # ==================== PROTECCIÓN XSS ====================
        # X-XSS-Protection: Habilitar filtro XSS del browser
        # mode=block: Bloquear página completa si se detecta XSS
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # ==================== PROTECCIÓN CLICKJACKING ====================
        # X-Frame-Options: Prevenir que la página sea embebida en iframe
        # DENY: No permitir ningún iframe
        # Alternativa: SAMEORIGIN (permitir solo mismo dominio)
        response.headers["X-Frame-Options"] = "DENY"
        
        # ==================== PROTECCIÓN MIME SNIFFING ====================
        # X-Content-Type-Options: Prevenir MIME sniffing
        # nosniff: Browser debe respetar el Content-Type declarado
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # ==================== HSTS (HTTP Strict Transport Security) ====================
        # Solo agregar HSTS si:
        # 1. Está habilitado
        # 2. La conexión es HTTPS (o en desarrollo)
        if self.enable_hsts:
            # Verificar si la request es HTTPS
            is_https = request.url.scheme == "https" or \
                      request.headers.get("X-Forwarded-Proto") == "https"
            
            if is_https:
                # max-age: Tiempo que el browser debe recordar usar solo HTTPS
                # includeSubDomains: Aplicar a todos los subdominios
                # preload: Permitir inclusión en listas de preload de browsers
                hsts_value = f"max-age={self.hsts_max_age}; includeSubDomains; preload"
                response.headers["Strict-Transport-Security"] = hsts_value
        
        # ==================== CONTENT SECURITY POLICY ====================
        # CSP: Define qué recursos puede cargar la página
        # Política restrictiva para máxima seguridad
        csp_directives = [
            "default-src 'self'",  # Por defecto, solo recursos del mismo origen
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Scripts (React necesita unsafe-inline/eval)
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",  # Estilos
            "font-src 'self' https://fonts.gstatic.com data:",  # Fuentes
            "img-src 'self' data: https:",  # Imágenes (data: para base64, https: para CDNs)
            "connect-src 'self' https://api.openai.com",  # API calls
            "frame-ancestors 'none'",  # No permitir iframes (complementa X-Frame-Options)
            "base-uri 'self'",  # Restringir <base> tag
            "form-action 'self'",  # Solo enviar forms al mismo origen
            "object-src 'none'",  # Bloquear <object>, <embed>, <applet>
            "upgrade-insecure-requests",  # Auto-upgrade HTTP → HTTPS
        ]
        
        csp_value = "; ".join(csp_directives)
        response.headers["Content-Security-Policy"] = csp_value
        
        # ==================== REFERRER POLICY ====================
        # Controlar qué información se envía en el Referer header
        # strict-origin-when-cross-origin: 
        #   - Same-origin: URL completa
        #   - Cross-origin HTTPS→HTTPS: Solo origin
        #   - HTTPS→HTTP: No enviar
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # ==================== CROSS-DOMAIN POLICIES ====================
        # X-Permitted-Cross-Domain-Policies: Controlar acceso de Flash/PDF
        # none: No permitir cross-domain policies
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        
        # ==================== PERMISSIONS POLICY ====================
        # Permissions-Policy: Controlar features del browser
        # Deshabilitar features peligrosas o innecesarias
        permissions_directives = [
            "geolocation=()",  # Deshabilitar geolocalización
            "microphone=()",  # Deshabilitar micrófono
            "camera=()",  # Deshabilitar cámara
            "payment=()",  # Deshabilitar Payment Request API
            "usb=()",  # Deshabilitar USB
            "magnetometer=()",  # Deshabilitar magnetómetro
            "gyroscope=()",  # Deshabilitar giroscopio
            "accelerometer=()",  # Deshabilitar acelerómetro
        ]
        
        permissions_value = ", ".join(permissions_directives)
        response.headers["Permissions-Policy"] = permissions_value
        
        # ==================== CUSTOM SECURITY HEADERS ====================
        # X-Powered-By: Eliminar si existe (no revelar tecnología)
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]
        
        # Server: Eliminar o minimizar (no revelar versión de servidor)
        if "Server" in response.headers:
            response.headers["Server"] = "CivilProtect"
        
        return response


def get_security_headers_config() -> dict:
    """
    Obtener configuración de headers de seguridad para documentación.
    
    Returns:
        dict: Diccionario con todos los headers y sus valores
    """
    return {
        "X-XSS-Protection": {
            "value": "1; mode=block",
            "description": "Habilita filtro XSS del browser y bloquea la página si detecta ataque",
            "protection": "Cross-Site Scripting (XSS)"
        },
        "X-Frame-Options": {
            "value": "DENY",
            "description": "Previene que la página sea embebida en iframes",
            "protection": "Clickjacking"
        },
        "X-Content-Type-Options": {
            "value": "nosniff",
            "description": "Previene MIME sniffing, fuerza respetar Content-Type",
            "protection": "MIME Type Confusion"
        },
        "Strict-Transport-Security": {
            "value": "max-age=31536000; includeSubDomains; preload",
            "description": "Fuerza uso de HTTPS por 1 año, incluyendo subdominios",
            "protection": "Man-in-the-Middle, Protocol Downgrade"
        },
        "Content-Security-Policy": {
            "value": "default-src 'self'; ...",
            "description": "Controla qué recursos puede cargar la página",
            "protection": "XSS, Data Injection, Malicious Scripts"
        },
        "Referrer-Policy": {
            "value": "strict-origin-when-cross-origin",
            "description": "Controla información enviada en Referer header",
            "protection": "Information Disclosure"
        },
        "X-Permitted-Cross-Domain-Policies": {
            "value": "none",
            "description": "Bloquea cross-domain policies de Flash/PDF",
            "protection": "Cross-Domain Data Leakage"
        },
        "Permissions-Policy": {
            "value": "geolocation=(), camera=(), ...",
            "description": "Deshabilita features peligrosas del browser",
            "protection": "Unauthorized Feature Access"
        }
    }


def validate_security_headers(response_headers: dict) -> dict:
    """
    Validar que todos los headers de seguridad estén presentes.
    
    Args:
        response_headers: Headers de una respuesta HTTP
        
    Returns:
        dict: Resultado de validación con headers presentes/faltantes
    """
    required_headers = [
        "X-XSS-Protection",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Content-Security-Policy",
        "Referrer-Policy",
        "X-Permitted-Cross-Domain-Policies",
        "Permissions-Policy"
    ]
    
    optional_headers = [
        "Strict-Transport-Security"  # Solo en HTTPS
    ]
    
    present = []
    missing = []
    
    for header in required_headers:
        if header in response_headers:
            present.append(header)
        else:
            missing.append(header)
    
    for header in optional_headers:
        if header in response_headers:
            present.append(header)
    
    return {
        "total_required": len(required_headers),
        "present": present,
        "missing": missing,
        "coverage": len(present) / (len(required_headers) + len(optional_headers)) * 100
    }


# Exportar funciones y clase
__all__ = [
    'SecurityHeadersMiddleware',
    'get_security_headers_config',
    'validate_security_headers'
]
