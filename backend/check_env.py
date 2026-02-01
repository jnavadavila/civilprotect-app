"""
Script de Verificación de Variables de Entorno
Valida que todas las variables requeridas estén configuradas correctamente
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import re

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Imprimir header con formato"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")


def print_success(text: str):
    """Imprimir mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """Imprimir mensaje de error"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    """Imprimir mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str):
    """Imprimir mensaje informativo"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def check_env_file_exists() -> bool:
    """Verificar que el archivo .env existe"""
    env_path = Path(".env")
    if not env_path.exists():
        print_error("Archivo .env no encontrado")
        print_info("Copia .env.example a .env y configura las variables")
        print_info("  cp .env.example .env")
        return False
    
    print_success("Archivo .env encontrado")
    return True


def load_env_file() -> Dict[str, str]:
    """Cargar variables del archivo .env"""
    env_vars = {}
    
    try:
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Ignorar comentarios y líneas vacías
                if not line or line.startswith("#"):
                    continue
                
                # Parsear KEY=VALUE
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
        
        print_success(f"Cargadas {len(env_vars)} variables del archivo .env")
        return env_vars
    except Exception as e:
        print_error(f"Error leyendo .env: {e}")
        return {}


def check_required_variables(env_vars: Dict[str, str]) -> Tuple[List[str], List[str]]:
    """
    Verificar que todas las variables requeridas estén presentes
    
    Returns:
        Tuple[List[str], List[str]]: (variables_ok, variables_faltantes)
    """
    # Variables REQUERIDAS
    required_vars = [
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "REFRESH_TOKEN_EXPIRE_DAYS",
        "ALLOWED_ORIGINS"
    ]
    
    missing = []
    found = []
    
    print_info("Verificando variables requeridas...")
    
    for var in required_vars:
        if var in env_vars and env_vars[var]:
            found.append(var)
            print_success(f"{var:40} = {mask_value(var, env_vars[var])}")
        else:
            missing.append(var)
            print_error(f"{var:40} = [FALTANTE]")
    
    return found, missing


def check_optional_variables(env_vars: Dict[str, str]) -> List[str]:
    """Verificar variables opcionales"""
    optional_vars = [
        "RATE_LIMIT_ANALYZE",
        "RATE_LIMIT_LOGIN",
        "RATE_LIMIT_REGISTER",
        "DEBUG",
        "SECURITY_LOGGING",
        "LOG_LEVEL",
        "SERVER_HOST",
        "SERVER_PORT",
        "WORKERS",
        "ENV",
        "APP_NAME",
        "APP_VERSION",
        "ENABLE_AI_ENRICHMENT",
        "ENABLE_LEGISLATIVE_MONITOR",
        "ENABLE_PDF_GENERATION",
        "ENABLE_HTML_REPORTS",
        "PDF_OUTPUT_DIR",
        "DATA_DIR",
        "LOG_DIR"
    ]
    
    found = []
    
    print_info("\nVerificando variables opcionales (usan defaults si no están)...")
    
    for var in optional_vars:
        if var in env_vars and env_vars[var]:
            found.append(var)
            print_success(f"{var:40} = {env_vars[var]}")
        else:
            print_warning(f"{var:40} = [Usando default]")
    
    return found


def mask_value(key: str, value: str) -> str:
    """
    Enmascarar valores sensibles para evitar exponer secretos en logs
    
    Args:
        key: Nombre de la variable
        value: Valor de la variable
    
    Returns:
        str: Valor enmascarado si es sensible, sino el valor original
    """
    sensitive_keys = ["SECRET", "KEY", "PASSWORD", "TOKEN"]
    
    # Si la clave contiene palabras sensibles, enmascrar
    if any(word in key.upper() for word in sensitive_keys):
        if len(value) > 8:
            return f"{value[:4]}...{value[-4:]}"
        else:
            return "*" * len(value)
    
    return value


def validate_jwt_secret(jwt_secret: str) -> bool:
    """Validar que JWT_SECRET_KEY sea seguro"""
    print_info("\nValidando JWT_SECRET_KEY...")
    
    issues = []
    
    # Verificar longitud mínima
    if len(jwt_secret) < 32:
        issues.append(f"Demasiado corto ({len(jwt_secret)} chars). Mínimo: 32")
    
    # Verificar que no sea un placeholder
    placeholders = ["placeholder", "change-this", "your-", "example", "test"]
    if any(word in jwt_secret.lower() for word in placeholders):
        issues.append("Contiene placeholder. Genera una clave real")
    
    # Verificar que tenga suficiente entropía (variedad de caracteres)
    unique_chars = len(set(jwt_secret))
    if unique_chars < 16:
        issues.append(f"Baja entropía (solo {unique_chars} caracteres únicos)")
    
    if issues:
        for issue in issues:
            print_error(f"  {issue}")
        print_warning("Genera una clave segura con:")
        print_info('  python -c "import secrets; print(secrets.token_hex(32))"')
        return False
    
    print_success(f"JWT_SECRET_KEY es seguro ({len(jwt_secret)} chars, {unique_chars} únicos)")
    return True


def validate_openai_key(api_key: str) -> bool:
    """Validar formato de OPENAI_API_KEY"""
    print_info("\nValidando OPENAI_API_KEY...")
    
    # Verificar que no sea placeholder
    if "placeholder" in api_key.lower() or api_key.startswith("your-"):
        print_warning("OPENAI_API_KEY parece ser un placeholder")
        print_warning("Las funcionalidades de IA no funcionarán")
        print_info("Obtén una clave en: https://platform.openai.com/api-keys")
        return False
    
    # Verificar formato básico (debe empezar con sk-)
    if not api_key.startswith("sk-"):
        print_warning("OPENAI_API_KEY no tiene el formato esperado (debe empezar con 'sk-')")
        return False
    
    print_success("OPENAI_API_KEY tiene formato válido")
    return True


def validate_cors_origins(origins: str, env: str) -> bool:
    """Validar configuración de CORS"""
    print_info("\nValidando ALLOWED_ORIGINS...")
    
    if "*" in origins:
        if env == "production":
            print_error("CORS permite cualquier origen (*) en PRODUCCIÓN")
            print_warning("Esto es un RIESGO DE SEGURIDAD")
            print_info("Configura dominios específicos")
            return False
        else:
            print_warning("CORS permite cualquier origen (*)")
            print_info("Está bien para desarrollo, pero NO para producción")
    
    origins_list = [o.strip() for o in origins.split(",")]
    print_success(f"CORS configurado para {len(origins_list)} origen(es):")
    for origin in origins_list:
        print_info(f"  - {origin}")
    
    return True


def validate_security_settings(env_vars: Dict[str, str]) -> List[str]:
    """Validar configuraciones de seguridad"""
    print_info("\nValidando configuraciones de seguridad...")
    
    warnings = []
    
    env = env_vars.get("ENV", "production").lower()
    debug = env_vars.get("DEBUG", "False").lower() == "true"
    token_minutes = int(env_vars.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # DEBUG en producción
    if env == "production" and debug:
        warnings.append("DEBUG=True en PRODUCCIÓN (expone información sensible)")
    
    # Token expiry muy largo en producción
    if env == "production" and token_minutes > 60:
        warnings.append(f"ACCESS_TOKEN_EXPIRE_MINUTES={token_minutes} muy alto para producción (recomendado: 30)")
    
    if warnings:
        for warning in warnings:
            print_warning(warning)
    else:
        print_success("Configuraciones de seguridad OK")
    
    return warnings


def test_import_config() -> bool:
    """Intentar importar el módulo config.py"""
    print_info("\nProbando importación de config.py...")
    
    try:
        from config import settings
        print_success("Módulo config.py cargado exitosamente")
        print_success(f"App: {settings.app_name} v{settings.app_version}")
        print_success(f"Entorno: {settings.env.upper()}")
        return True
    except Exception as e:
        print_error(f"Error importando config.py: {e}")
        print_info("Verifica que todas las variables requeridas estén configuradas")
        return False


def print_summary(results: Dict):
    """Imprimir resumen final"""
    print_header("RESUMEN DE VERIFICACIÓN")
    
    total_checks = 7
    passed_checks = 0
    
    # 1. Archivo .env existe
    if results['env_file_exists']:
        print_success("1. Archivo .env existe")
        passed_checks += 1
    else:
        print_error("1. Archivo .env NO existe")
    
    # 2. Variables requeridas
    found = len(results['required_found'])
    total = found + len(results['required_missing'])
    if len(results['required_missing']) == 0:
        print_success(f"2. Variables requeridas completas ({found}/{total})")
        passed_checks += 1
    else:
        print_error(f"2. Faltan {len(results['required_missing'])} variables requeridas")
    
    # 3. JWT Secret
    if results['jwt_valid']:
        print_success("3. JWT_SECRET_KEY es seguro")
        passed_checks += 1
    else:
        print_error("3. JWT_SECRET_KEY NO es seguro")
    
    # 4. OpenAI Key
    if results['openai_valid']:
        print_success("4. OPENAI_API_KEY es válido")
        passed_checks += 1
    else:
        print_warning("4. OPENAI_API_KEY no es válido (funcional pero limitado)")
        passed_checks += 0.5
    
    # 5. CORS
    if results['cors_valid']:
        print_success("5. CORS configurado correctamente")
        passed_checks += 1
    else:
        print_warning("5. CORS tiene problemas de seguridad")
        passed_checks += 0.5
    
    # 6. Seguridad
    if len(results['security_warnings']) == 0:
        print_success("6. Configuración de seguridad OK")
        passed_checks += 1
    else:
        print_warning(f"6. {len(results['security_warnings'])} advertencias de seguridad")
        passed_checks += 0.5
    
    # 7. Import test
    if results['config_imports']:
        print_success("7. Config.py se importa correctamente")
        passed_checks += 1
    else:
        print_error("7. Config.py NO se puede importar")
    
    print(f"\n{Colors.BOLD}Resultado: {int(passed_checks)}/{total_checks} checks pasados{Colors.END}")
    
    if passed_checks == total_checks:
        print_success("\n🎉 CONFIGURACIÓN COMPLETA Y VÁLIDA 🎉")
        return True
    elif passed_checks >= total_checks * 0.7:
        print_warning("\n⚠️  CONFIGURACIÓN FUNCIONAL CON ADVERTENCIAS")
        return True
    else:
        print_error("\n❌ CONFIGURACIÓN INCOMPLETA O INVÁLIDA")
        return False


def main():
    """Función principal"""
    print_header("VERIFICACIÓN DE VARIABLES DE ENTORNO")
    print_info("CivilProtect V4.5 - Environment Checker")
    
    results = {
        'env_file_exists': False,
        'required_found': [],
        'required_missing': [],
        'optional_found': [],
        'jwt_valid': False,
        'openai_valid': False,
        'cors_valid': False,
        'security_warnings': [],
        'config_imports': False
    }
    
    # 1. Verificar que .env existe
    results['env_file_exists'] = check_env_file_exists()
    if not results['env_file_exists']:
        print_summary(results)
        return sys.exit(1)
    
    # 2. Cargar variables
    env_vars = load_env_file()
    
    # 3. Verificar variables requeridas
    found, missing = check_required_variables(env_vars)
    results['required_found'] = found
    results['required_missing'] = missing
    
    # 4. Verificar variables opcionales
    results['optional_found'] = check_optional_variables(env_vars)
    
    # 5. Validar JWT Secret
    if "JWT_SECRET_KEY" in env_vars:
        results['jwt_valid'] = validate_jwt_secret(env_vars["JWT_SECRET_KEY"])
    
    # 6. Validar OpenAI Key
    if "OPENAI_API_KEY" in env_vars:
        results['openai_valid'] = validate_openai_key(env_vars["OPENAI_API_KEY"])
    
    # 7. Validar CORS
    if "ALLOWED_ORIGINS" in env_vars:
        env_type = env_vars.get("ENV", "production")
        results['cors_valid'] = validate_cors_origins(env_vars["ALLOWED_ORIGINS"], env_type)
    
    # 8. Validar seguridad
    results['security_warnings'] = validate_security_settings(env_vars)
    
    # 9. Test import
    results['config_imports'] = test_import_config()
    
    # 10. Resumen
    is_valid = print_summary(results)
    
    if is_valid:
        return sys.exit(0)
    else:
        return sys.exit(1)


if __name__ == "__main__":
    main()
