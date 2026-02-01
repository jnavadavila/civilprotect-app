"""
Módulo de Autenticación para CivilProtect Application
Generación y Validación de Tokens JWT
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración JWT (desde variables de entorno)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION_123456789")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un Access Token JWT.
    
    Args:
        data: Datos a codificar en el token (generalmente user_id, email, role)
        expires_delta: Tiempo de expiración personalizado (opcional)
        
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Crea un Refresh Token JWT (validez más larga).
    
    Args:
        data: Datos a codificar en el token
        
    Returns:
        Refresh token JWT codificado
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
        token_type: Tipo de token esperado ("access" o "refresh")
        
    Returns:
        Payload del token si es válido, None en caso contrario
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificar que el tipo de token coincida
        if payload.get("type") != token_type:
            return None
            
        return payload
    except JWTError:
        return None


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica un token sin verificar tipo (para debugging).
    
    Args:
        token: Token JWT
        
    Returns:
        Payload decodificado o None si es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
