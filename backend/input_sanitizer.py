"""
Módulo de Sanitización y Validación de Inputs
Protección contra XSS, SQL Injection y otros ataques
"""
import bleach
import re
from typing import Optional, Union
from fastapi import HTTPException, status

# Configuración de bleach para sanitización HTML
ALLOWED_TAGS = []  # No permitir ningún tag HTML
ALLOWED_ATTRIBUTES = {}
ALLOWED_PROTOCOLS = []

def sanitize_html(text: str) -> str:
    """
    Sanitizar texto eliminando todos los tags HTML.
    Usado para campos como custom_label.
    """
    if not text:
        return ""
    
    # Eliminar todos los tags HTML
    cleaned = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # Eliminar tags en lugar de escaparlos
    )
    
    return cleaned.strip()

def validate_alphanumeric_spaces(text: str, field_name: str, max_length: int = 100) -> str:
    """
    Validar que el texto solo contenga letras, números, espacios y algunos caracteres especiales seguros.
    Usado para municipio, estado, nombres, etc.
    
    Caracteres permitidos:
    - Letras (a-z, A-Z) incluyen acentos
    - Números (0-9)
    - Espacios
    - Guiones (-), puntos (.), paréntesis (), comas (,)
    """
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{field_name}' es requerido"
        )
    
    # Verificar longitud
    if len(text) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{field_name}' excede el límite de {max_length} caracteres"
        )
    
    # Permitir letras (incluyendo acentos), números, espacios y caracteres seguros
    # Pattern: letras con acentos, números, espacio, guión, punto, paréntesis, coma
    pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s\-.,()]+$'
    
    if not re.match(pattern, text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{field_name}' contiene caracteres no permitidos. "
                   f"Solo se permiten letras, números, espacios y algunos signos de puntuación básicos."
        )
    
    return text.strip()

def validate_email_format(email: str) -> str:
    """
    Validación básica de formato de email.
    Pydantic EmailStr ya valida, pero agregamos capa extra.
    """
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email es requerido"
        )
    
    # Pattern básico de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de email inválido"
        )
    
    # Limitar longitud
    if len(email) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email demasiado largo (máx. 255 caracteres)"
        )
    
    return email.lower().strip()

def validate_positive_number(value: Union[int, float], field_name: str, allow_zero: bool = False) -> Union[int, float]:
    """
    Validar que un número sea positivo (o cero si se permite).
    Usado para aforo_autorizado, costos, etc.
    """
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{field_name}' es requerido"
        )
    
    min_value = 0 if allow_zero else 0.01
    
    if value < min_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{field_name}' debe ser {'positivo' if not allow_zero else 'mayor o igual a cero'}"
        )
    
    # Verificar límites razonables
    if value > 1_000_000_000:  # 1 billón
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{field_name}' excede el límite máximo permitido"
        )
    
    return value

def validate_integer_range(value: int, field_name: str, min_val: int = 0, max_val: int = 1_000_000) -> int:
    """
    Validar que un entero esté dentro de un rango específico.
    """
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{field_name}' es requerido"
        )
    
    if not isinstance(value, int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{field_name}' debe ser un número entero"
        )
    
    if value < min_val or value > max_val:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{field_name}' debe estar entre {min_val} y {max_val}"
        )
    
    return value

def sanitize_filename(filename: str) -> str:
    """
    Sanitizar nombres de archivo para prevenir path traversal.
    """
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo requerido"
        )
    
    # Eliminar caracteres peligrosos
    safe_chars = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Prevenir path traversal
    safe_chars = safe_chars.replace('..', '')
    safe_chars = safe_chars.replace('/', '')
    safe_chars = safe_chars.replace('\\', '')
    
    # Limitar longitud
    if len(safe_chars) > 255:
        safe_chars = safe_chars[:255]
    
    return safe_chars

def validate_password_strength(password: str) -> str:
    """
    Validar fortaleza de contraseña.
    Requisitos:
    - Mínimo 6 caracteres
    - Al menos una letra
    - Al menos un número (opcional pero recomendado)
    """
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es requerida"
        )
    
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 6 caracteres"
        )
    
    if len(password) > 128:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es demasiado larga (máx. 128 caracteres)"
        )
    
    # Validar que tenga al menos una letra
    if not re.search(r'[a-zA-Z]', password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos una letra"
        )
    
    # Opcional: validar que tenga al menos un número (comentado por ahora)
    # if not re.search(r'[0-9]', password):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="La contraseña debe contener al menos un número"
    #     )
    
    return password

def validate_role(role: str) -> str:
    """
    Validar que el rol sea uno de los permitidos.
    """
    ALLOWED_ROLES = ["admin", "consultor", "cliente"]
    
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Roles permitidos: {', '.join(ALLOWED_ROLES)}"
        )
    
    return role

# Función helper para sanitizar datos de análisis
def sanitize_analysis_input(data: dict) -> dict:
    """
    Sanitizar todos los campos de un análisis antes de procesarlo.
    """
    sanitized = {}
    
    # Campos de texto
    if 'municipio' in data:
        sanitized['municipio'] = validate_alphanumeric_spaces(data['municipio'], 'municipio', 100)
    
    if 'estado' in data:
        sanitized['estado'] = validate_alphanumeric_spaces(data['estado'], 'estado', 50)
    
    if 'tipo_inmueble' in data:
        sanitized['tipo_inmueble'] = validate_alphanumeric_spaces(data['tipo_inmueble'], 'tipo_inmueble', 100)
    
    if 'custom_label' in data and data['custom_label']:
        # Sanitizar HTML y validar alfanuméricos
        cleaned_html = sanitize_html(data['custom_label'])
        sanitized['custom_label'] = validate_alphanumeric_spaces(cleaned_html, 'custom_label', 200)
    
    # Campos numéricos
    if 'aforo_autorizado' in data:
        sanitized['aforo_autorizado'] = validate_positive_number(data['aforo_autorizado'], 'aforo_autorizado', allow_zero=False)
    
    return sanitized

# Exportar funciones públicas
__all__ = [
    'sanitize_html',
    'validate_alphanumeric_spaces',
    'validate_email_format',
    'validate_positive_number',
    'validate_integer_range',
    'sanitize_filename',
    'validate_password_strength',
    'validate_role',
    'sanitize_analysis_input'
]
