"""
Módulo de Autenticación para CivilProtect Application
Manejo de Hashing de Contraseñas con bcrypt
"""
import bcrypt


def hash_password(password: str) -> str:
    """
    Genera un hash bcrypt de la contraseña.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash bcrypt de la contraseña
        
    Note:
        bcrypt tiene un límite de 72 bytes. Si la contraseña es más larga,
        se trunca automáticamente.
    """
    # bcrypt solo acepta hasta 72 bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generar salt y hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Retornar como string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash bcrypt almacenado
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    # Convertir a bytes
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    hash_bytes = hashed_password.encode('utf-8')
    
    # Verificar
    return bcrypt.checkpw(password_bytes, hash_bytes)

