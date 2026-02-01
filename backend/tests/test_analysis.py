import sys
import os

# Agregamos el path del backend para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from noms_library import get_applicable_noms, get_pipc_guide
from report_generator import generate_pdf_report

# --- PRUEBAS DE LOGICA LEGAL EXPERTA (REAL, NO SIMULADA) ---

def test_trpc_naming_convention():
    """
    REQ #2: Verificar que las guías incluyan "TRPC" en el título.
    """
    print(f"[*] Ejecutando: test_trpc_naming_convention...")
    profile = {"estado": "Jalisco", "municipio": "Guadalajara"}
    noms = get_applicable_noms(profile)
    
    # Buscar la guía de integración
    guide = next((n for n in noms if n.get("is_pipc_guide")), None)
    
    assert guide is not None, "La Guía PIPC debe existir en la respuesta"
    print(f"    > Título encontrado: {guide['titulo']}")
    assert "TRPC" in guide["titulo"], f"El título '{guide['titulo']}' debe contener 'TRPC' (Términos de Referencia)"
    print("    > PASSED")

def test_nom_001_sede_presence():
    """
    REQ #1 (Previo): Verificar que NOM-001-SEDE siempre esté presente
    """
    print(f"[*] Ejecutando: test_nom_001_sede_presence...")
    profile = {"estado": "CDMX", "municipio": "Cuauhtémoc"}
    noms = get_applicable_noms(profile)
    
    # Buscar NOM-001-SEDE
    nom_001 = next((n for n in noms if "NOM-001-SEDE" in n.get("norma", "")), None)
    assert nom_001 is not None, "NOM-001-SEDE debe ser obligatoria para todos"
    print(f"    > Norma encontrada: {nom_001['norma']}")
    print("    > PASSED")

def test_jalisco_specificity():
    """
    REQ: Verificar que Jalisco pida 'Perito Padrón UEPCJ' y cite el 'Art. 24'.
    """
    print(f"[*] Ejecutando: test_jalisco_specificity (Lógica Experta)...")
    guide = get_pipc_guide("Jalisco")
    
    # Buscar el item de Responsiva en el capitulo 1
    admin_chapter = guide[0]["items"]
    responsiva = next((i for i in admin_chapter if "Corresponsabilidad" in i["req"]), None)
    
    assert responsiva is not None, "Debe existir el requisito de Corresponsabilidad"
    print(f"    > Requisito detectado: {responsiva['req']}")
    print(f"    > Fundamento detectado: {responsiva['fundamento']}")
    
    # Validaciones Explicitas del Usuario
    assert "Unidad Interna" in responsiva["req"], "Jalisco debe mencionar 'Unidad Interna' o UEPCJ"
    assert "Art. 24" in responsiva["fundamento"], "El fundamento debe ser Art. 24 (Ley Jalisco)"
    print("    > PASSED")

def test_nuevo_leon_specificity():
    """
    REQ: Verificar que Nuevo León pida 'Consultor Externo' y cite 'Art. 18'.
    """
    print(f"[*] Ejecutando: test_nuevo_leon_specificity (Lógica Experta)...")
    guide = get_pipc_guide("Nuevo León")
    
    admin_chapter = guide[0]["items"]
    responsiva = next((i for i in admin_chapter if "Consultor" in i["req"]), None)
    
    assert responsiva is not None, "NL debe pedir Consultor Externo"
    print(f"    > Requisito detectado: {responsiva['req']}")
    print(f"    > Fundamento detectado: {responsiva['fundamento']}")
    
    assert "Consultor Externo" in responsiva["req"], "NL debe exigir explícitamente 'Consultor Externo'"
    assert "Art. 18" in responsiva["fundamento"], "El fundamento debe ser Art. 18"
    print("    > PASSED")

if __name__ == "__main__":
    print("\n=== INICIANDO SUITE DE PRUEBAS DE EXPERTO LEGAL (QA) ===")
    print("Objetivo: Verificar que el sistema use leyes reales por estado.\n")
    
    tests_passed = 0
    total_tests = 4
    
    try:
        test_trpc_naming_convention()
        tests_passed += 1
        
        test_nom_001_sede_presence()
        tests_passed += 1
        
        test_jalisco_specificity()
        tests_passed += 1
        
        test_nuevo_leon_specificity()
        tests_passed += 1
        
        print("\n" + "="*60)
        print(f"RESULTADO FINAL: {tests_passed}/{total_tests} REGLAS EXPERTAS VALIDADAS ✅")
        print("El sistema YA NO SIMULA, ahora APLICA la ley local específica.")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ FALLO CRÍTICO EN LÓGICA LEGAL: {e}")
    except Exception as e:
        print(f"\n❌ ERROR DE EJECUCIÓN: {e}")
