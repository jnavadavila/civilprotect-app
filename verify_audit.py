
import sys
import os

# Adjust path to find backend modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.calculator_engine import CivilProtectionCalculator

def test_audit_fixes():
    engine = CivilProtectionCalculator()
    errors = []

    # 1. TEST CDMX - Dirección Electrónica
    print("Testing CDMX Requirements...")
    data_cdmx = {
        "m2_construccion": 1000,
        "tipo_inmueble": "Oficina",
        "niveles": 2,
        "trabajadores": 20,
        "estado": "Ciudad de México",
        "municipio": "Cuauhtémoc"
    }
    result_cdmx = engine.analyze_full_compliance(data_cdmx)
    items_cdmx = [item['concepto'] for item in result_cdmx['presupuesto_inicial']]
    
    found_digital = any("Registro de Dirección Electrónica" in item for item in items_cdmx)
    if not found_digital:
        errors.append("FAIL: CDMX missing 'Registro de Dirección Electrónica'")
    else:
        print("PASS: CDMX includes 'Registro de Dirección Electrónica'")

    # 2. TEST NATIONAL (Rest of Country) - Structural Safety
    print("\nTesting National Requirements (Oaxaca)...")
    data_national = {
        "m2_construccion": 1000,
        "tipo_inmueble": "Oficina",
        "niveles": 2,
        "trabajadores": 20,
        "estado": "Oaxaca",  # Not CDMX, NL, Jal, or Center
        "municipio": "Oaxaca de Juárez"
    }
    result_national = engine.analyze_full_compliance(data_national)
    items_national = [item['concepto'] for item in result_national['presupuesto_inicial']]
    
    found_structural = any("Dictamen de Estabilidad" in item for item in items_national)
    found_vobo = any("Visto Bueno de Seguridad" in item for item in items_national)
    
    if not found_structural:
        errors.append("FAIL: National missing 'Dictamen de Estabilidad/Seguridad Estructural'")
    else:
        print("PASS: National includes 'Dictamen de Estabilidad'")
        
    if not found_vobo:
        errors.append("FAIL: National missing 'Visto Bueno de Seguridad'")
    else:
        print("PASS: National includes 'Visto Bueno de Seguridad'")

    # Report
    if errors:
        print("\nERRORS FOUND:")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("\nALL SYSTEM CHECKS PASSED. LOGIC IS FLAWLESS.")
        sys.exit(0)

if __name__ == "__main__":
    test_audit_fixes()
