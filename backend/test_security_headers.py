"""
Test de Security Headers
Verifica que todos los headers de seguridad estén implementados correctamente
"""
import requests
from security_headers import get_security_headers_config, validate_security_headers

BASE_URL = "http://localhost:8000"

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")


def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def test_security_headers():
    """Test principal de security headers"""
    print_header("TEST DE SECURITY HEADERS")
    print_info("CivilProtect V4.5 - Security Headers Validator")
    
    try:
        # Hacer request al API
        print_info(f"Haciendo request a: {BASE_URL}/")
        response = requests.get(BASE_URL)
        headers = dict(response.headers)
        
        print_success(f"Respuesta recibida: {response.status_code}")
        
        # Obtener configuración esperada
        expected_config = get_security_headers_config()
        
        # Validar headers
        validation = validate_security_headers(headers)
        
        print(f"\n{Colors.BOLD}Headers de Seguridad Presentes:{Colors.END}")
        print(f"Total esperados: {validation['total_required'] + 1}")  # +1 para HSTS opcional
        print(f"Presentes: {len(validation['present'])}")
        print(f"Faltantes: {len(validation['missing'])}")
        print(f"Cobertura: {validation['coverage']:.1f}%\n")
        
        # ==================== VERIFICACIÓN HEADER POR HEADER ====================
        
        # 1. X-XSS-Protection
        print_info("\n[1/8] X-XSS-Protection")
        if "X-XSS-Protection" in headers:
            value = headers["X-XSS-Protection"]
            expected = "1; mode=block"
            if value == expected:
                print_success(f"Presente y correcto: {value}")
            else:
                print_warning(f"Presente pero incorrecto: {value} (esperado: {expected})")
        else:
            print_error("FALTANTE - Protección XSS no activa")
        
        # 2. X-Frame-Options
        print_info("\n[2/8] X-Frame-Options")
        if "X-Frame-Options" in headers or "x-frame-options" in headers:
            value = headers.get("X-Frame-Options", headers.get("x-frame-options"))
            expected = "DENY"
            if value == expected:
                print_success(f"Presente y correcto: {value}")
            else:
                print_warning(f"Presente: {value} (esperado: {expected})")
        else:
            print_error("FALTANTE - Protección clickjacking no activa")
        
        # 3. X-Content-Type-Options
        print_info("\n[3/8] X-Content-Type-Options")
        if "X-Content-Type-Options" in headers or "x-content-type-options" in headers:
            value = headers.get("X-Content-Type-Options", headers.get("x-content-type-options"))
            expected = "nosniff"
            if value == expected:
                print_success(f"Presente y correcto: {value}")
            else:
                print_warning(f"Presente pero incorrecto: {value}")
        else:
            print_error("FALTANTE - Protección MIME sniffing no activa")
        
        # 4. Strict-Transport-Security (HSTS)
        print_info("\n[4/8] Strict-Transport-Security (HSTS)")
        if "Strict-Transport-Security" in headers or "strict-transport-security" in headers:
            value = headers.get("Strict-Transport-Security", headers.get("strict-transport-security"))
            print_success(f"Presente: {value}")
            if "max-age" in value and "includeSubDomains" in value:
                print_success("  - incluye max-age y includeSubDomains ✓")
        else:
            print_warning("FALTANTE - Solo se aplica en conexiones HTTPS")
            print_info("  En producción con HTTPS, este header estará presente")
        
        # 5. Content-Security-Policy
        print_info("\n[5/8] Content-Security-Policy")
        if "Content-Security-Policy" in headers or "content-security-policy" in headers:
            value = headers.get("Content-Security-Policy", headers.get("content-security-policy"))
            print_success(f"Presente (longitud: {len(value)} chars)")
            
            # Verificar directivas clave
            key_directives = [
                "default-src",
                "script-src",
                "style-src",
                "frame-ancestors",
                "upgrade-insecure-requests"
            ]
            
            for directive in key_directives:
                if directive in value:
                    print_success(f"  - {directive} ✓")
                else:
                    print_warning(f"  - {directive} faltante")
        else:
            print_error("FALTANTE - Protección CSP no activa")
        
        # 6. Referrer-Policy
        print_info("\n[6/8] Referrer-Policy")
        if "Referrer-Policy" in headers or "referrer-policy" in headers:
            value = headers.get("Referrer-Policy", headers.get("referrer-policy"))
            expected = "strict-origin-when-cross-origin"
            if value == expected:
                print_success(f"Presente y correcto: {value}")
            else:
                print_success(f"Presente: {value}")
        else:
            print_error("FALTANTE")
        
        # 7. X-Permitted-Cross-Domain-Policies
        print_info("\n[7/8] X-Permitted-Cross-Domain-Policies")
        if "X-Permitted-Cross-Domain-Policies" in headers:
            value = headers["X-Permitted-Cross-Domain-Policies"]
            expected = "none"
            if value == expected:
                print_success(f"Presente y correcto: {value}")
            else:
                print_warning(f"Presente: {value}")
        else:
            print_error("FALTANTE")
        
        # 8. Permissions-Policy
        print_info("\n[8/8] Permissions-Policy")
        if "Permissions-Policy" in headers or "permissions-policy" in headers:
            value = headers.get("Permissions-Policy", headers.get("permissions-policy"))
            print_success(f"Presente (longitud: {len(value)} chars)")
            
            # Verificar features deshabilitadas
            disabled_features = [
                "geolocation",
                "camera",
                "microphone",
                "payment"
            ]
            
            for feature in disabled_features:
                if f"{feature}=()" in value:
                    print_success(f"  - {feature} deshabilitado ✓")
        else:
            print_error("FALTANTE")
        
        # ==================== HEADERS QUE NO DEBEN ESTAR ====================
        print_info("\n[VERIFICACIÓN] Headers que NO deben estar presentes:")
        
        dangerous_headers = {
            "X-Powered-By": "Revela tecnología del servidor",
            "Server": "Debe estar minimizado o removido"
        }
        
        for header, reason in dangerous_headers.items():
            if header in headers:
                value = headers[header]
                if header == "Server" and value == "CivilProtect":
                    print_success(f"{header}: {value} (minimizado ✓)")
                else:
                    print_warning(f"{header}: {value} ({reason})")
            else:
                print_success(f"{header}: No presente ✓")
        
        # ==================== RESUMEN FINAL ====================
        print_header("RESUMEN DE VALIDACIÓN")
        
        total_critical = 7  # Headers críticos (sin HSTS que es opcional)
        present_critical = len([h for h in validation['present'] if h != "Strict-Transport-Security"])
        
        if present_critical == total_critical:
            print_success(f"Todos los headers críticos presentes ({present_critical}/{total_critical})")
            print_success("\n🎉 CONFIGURACIÓN DE SECURITY HEADERS COMPLETA 🎉")
            return 0
        elif present_critical >= total_critical * 0.8:
            print_warning(f"Mayoría de headers presentes ({present_critical}/{total_critical})")
            print_warning("\n⚠️  CONFIGURACIÓN FUNCIONAL CON ADVERTENCIAS")
            return 0
        else:
            print_error(f"Headers insuficientes ({present_critical}/{total_critical})")
            print_error("\n❌ CONFIGURACIÓN INCOMPLETA")
            return 1
        
    except requests.exceptions.ConnectionError:
        print_error("No se puede conectar al servidor")
        print_info("Asegúrate de que el servidor esté corriendo:")
        print_info("  cd backend")
        print_info("  uvicorn main:app --reload")
        return 1
    except Exception as e:
        print_error(f"Error durante el test: {e}")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = test_security_headers()
    sys.exit(exit_code)
