"""
Módulo de Autenticación para CivilProtect Application
FastAPI Dependencies para Protección de Endpoints
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os

# Agregar el directorio padre al path para imports relativos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, User
from auth.jwt_handler import verify_token

# Security scheme para Bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency que obtiene el usuario actual desde el token JWT.
    
    Args:
        credentials: Credenciales HTTP (Bearer token)
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe
    """
    # Extraer token
    token = credentials.credentials
    
    # Verificar y decodificar token
    payload = verify_token(token, token_type="access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer user_id del payload (sub es string, convertir a int)
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta identificador de usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: identificador de usuario mal formado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuario en base de datos
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency que verifica que el usuario está activo.
    (Wrapper de get_current_user para compatibilidad futura)
    """
    return current_user


def require_role(allowed_roles: list):
    """
    Dependency factory para requerir roles específicos.
    
    Args:
        allowed_roles: Lista de roles permitidos (["admin"], ["admin", "consultor"], etc.)
        
    Returns:
        Dependency function que verifica el rol
        
    Ejemplo:
        @app.get("/admin/users", dependencies=[Depends(require_role(["admin"]))])
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles requeridos: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


# Alias para roles específicos (convenience)
require_admin = require_role(["admin"])
require_admin_or_consultor = require_role(["admin", "consultor"])
