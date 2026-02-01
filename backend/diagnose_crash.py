
import sys
import unittest
from fpdf import FPDF
try:
    from report_generator import generate_pdf_report, PDFReport
except ImportError:
    # Si falla el import directo, intentamos setup de path aunque estemos en el dir
    sys.path.append('.')
    from report_generator import generate_pdf_report, PDFReport

class TestCrash(unittest.TestCase):
    def test_pdf_generation_crash(self):
        print("\n--- TEST: PDF GENERATION ---")
        
        # Datos Mock similares a la captura del usuario
        input_data = {
            "estado": "Durango",
            "municipio": "Durango",
            "tipo_inmueble": "Hotel",
            "m2_construccion": 6000,
            "niveles": 4,
            "trabajadores": 220,
            "aforo": 890,
            "has_gas": True,
            "has_substation": True,
            "has_transformer": True,
            "has_machine_room": True
        }
        
        # Resultados Mock
        results = {
            "ai_analysis": {
                "legal_justification": "Justificación Mock",
                "normative_updates": ["Update 1"]
            },
            "checklist": [],
            "presupuesto_inicial": []
        }
        
        try:
            filename = "test_crash.pdf"
            print("Generando PDF...")
            generate_pdf_report(input_data, results, filename)
            print("PDF Generado OK.")
        except Exception as e:
            print(f"CRASH DETECTADO: {e}")
            raise e

if __name__ == "__main__":
    unittest.main()
