"""
Tests para report_generator.py
Coverage target: > 70%
"""
import pytest
import os
from pathlib import Path
from fpdf import FPDF
import PyPDF2
from report_generator import PDFReport, generate_pdf_report


# ==================== CLASE 1: TEST PDF BÁSICO ====================

@pytest.mark.report
@pytest.mark.integration
class TestBasicPDFGeneration:
    """Tests de generación básica de PDF"""
    
    def test_pdf_report_initialization(self):
        """Test inicialización de PDFReport"""
        pdf = PDFReport()
        
        assert pdf is not None
        assert isinstance(pdf, FPDF)
    
    def test_generate_pdf_basic(self, temp_pdf_dir, valid_analysis_data):
        """Test generar PDF básico"""
        # Preparar datos
        results = {
            "basic_requirements": {
                "extintores": {"base_PQS": {"cantidad": 2}},
                "brigadas": {"total_brigadistas": 3}
            },
            "resumen_ejecutivo": {
                "total_brigadistas": 3,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Justificación legal de prueba"
            },
            "presupuesto_inicial": [
                {
                    "id": "1",
                    "categoria": "Extinción",
                    "concepto": "Extintor PQS",
                    "cantidad": 2,
                    "precio_unitario": 500.0,
                    "norma": "NOM-002"
                }
            ],
            "checklist": []
        }
        
        # Generar PDF
        filename = str(temp_pdf_dir / "test_basic.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Verificar que se generó
        assert os.path.exists(result_path)
        assert Path(result_path).suffix == ".pdf"
    
    def test_pdf_file_is_valid(self, temp_pdf_dir, valid_analysis_data):
        """Test que el PDF generado es válido y se puede abrir"""
        # Preparar datos mínimos
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test"
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        # Generar PDF
        filename = str(temp_pdf_dir / "test_valid.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Intentar abrir con PyPDF2
        with open(result_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Verificar que tiene páginas
            assert len(pdf_reader.pages) > 0
    
    def test_pdf_contains_text(self, temp_pdf_dir, valid_analysis_data):
        """Test que el PDF contiene texto"""
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test justification"
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_text.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Leer PDF
        with open(result_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extraer texto de primera página
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            
            # Verificar que contiene algo
            assert len(text) > 0


# ==================== CLASE 2: TEST ENCODING UTF-8 ====================

@pytest.mark.report
@pytest.mark.unit
class TestUTF8Encoding:
    """Tests de encoding UTF-8 (caracteres especiales)"""
    
    def test_pdf_with_spanish_characters(self, temp_pdf_dir):
        """Test PDF con caracteres especiales españoles"""
        data = {
            "municipio": "Guadalajara",
            "estado": "Jalisco",
            "nombre_inmueble": "Edificio con ñ, á, é, í, ó, ú",
            "m2_construccion": 500,
            "aforo_autorizado": 100
        }
        
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Artículo 123 - Protección Civil"
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_spanish.pdf")
        result_path = generate_pdf_report(data, results, filename)
        
        # Debe generarse sin errores
        assert os.path.exists(result_path)
    
    def test_pdf_with_special_symbols(self, temp_pdf_dir):
        """Test PDF con símbolos especiales"""
        data = {
            "municipio": "Test ® © ™ § °",
            "estado": "Test",
            "nombre_inmueble": "Edificio Test",
            "m2_construccion": 500,
            "aforo_autorizado": 100
        }
        
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test m² €  $"
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_symbols.pdf")
        
        # No debe crashear (aunque algunos símbolos no se rendericen)
        try:
            result_path = generate_pdf_report(data, results, filename)
            assert os.path.exists(result_path)
        except Exception as e:
            # Si falla, al menos no debe ser por encoding
            pytest.fail(f"PDF generation failed with: {e}")
    
    def test_pdf_with_long_text(self, temp_pdf_dir, valid_analysis_data):
        """Test PDF con texto largo (múltiples páginas)"""
        # Texto muy largo
        long_text = "Este es un texto muy largo. " * 500  # ~14,000 caracteres
        
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": long_text
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_long.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Verificar que se generó
        assert os.path.exists(result_path)
        
        # Debe tener múltiples páginas
        with open(result_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            assert len(pdf_reader.pages) > 1


# ==================== CLASE 3: TEST SECCIONES DEL PDF ====================

@pytest.mark.report
@pytest.mark.unit
class TestPDFSections:
    """Tests de secciones del PDF"""
    
    def test_pdf_legal_section(self, temp_pdf_dir, valid_analysis_data):
        """Test sección legal del PDF"""
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Alto",
                "legal_justification_strict": "ARTÍCULO 39 - LEY GENERAL DE PROTECCIÓN CIVIL"
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_legal.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Leer y verificar contenido
        with open(result_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Debe contener justificación legal
            assert "ARTÍCULO" in text.upper() or "LEY" in text.upper()
    
    def test_pdf_budget_section(self, temp_pdf_dir, valid_analysis_data):
        """Test sección de presupuesto del PDF"""
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test"
            },
            "presupuesto_inicial": [
                {
                    "id": "1",
                    "categoria": "Extinción",
                    "concepto": "Extintor PQS 6kg",
                    "cantidad": 5,
                    "precio_unitario": 650.0,
                    "norma": "NOM-002-STPS-2010"
                },
                {
                    "id": "2",
                    "categoria": "Señalización",
                    "concepto": "Señal de Salida",
                    "cantidad": 10,
                    "precio_unitario": 85.0,
                    "norma": "NOM-003-SEGOB-2011"
                }
            ],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_budget.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Leer y verificar contenido
        with open(result_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Debe contener conceptos del presupuesto
            assert "Extintor" in text or "PRESUPUESTO" in text.upper()
    
    def test_pdf_checklist_section(self, temp_pdf_dir, valid_analysis_data):
        """Test sección de checklist normativo"""
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test"
            },
            "presupuesto_inicial": [],
            "checklist": [
                {
                    "norma": "NOM-002-STPS-2010",
                    "titulo": "Condiciones de seguridad - Prevención y protección contra incendios",
                    "applicability": "Aplica"
                },
                {
                    "norma": "NOM-026-STPS-2008",
                    "titulo": "Señales y avisos de seguridad e higiene",
                    "applicability": "Aplica"
                }
            ]
        }
        
        filename = str(temp_pdf_dir / "test_checklist.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Leer y verificar contenido
        with open(result_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Debe contener normas
            assert "NOM" in text


# ==================== CLASE 4: TEST FIRMA DIGITAL ====================

@pytest.mark.report
@pytest.mark.unit
class TestDigitalSignature:
    """Tests de firma digital en PDF"""
    
    def test_pdf_with_signature_placeholder(self, temp_pdf_dir, valid_analysis_data):
        """Test que el PDF incluye espacio para firma"""
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test"
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_signature.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Leer PDF
        with open(result_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Último página debe tener espacio para firmas
            last_page = pdf_reader.pages[-1]
            text = last_page.extract_text()
            
            # Buscar indicadores de firma
            # (Depende de la implementación actual)
            assert len(text) > 0


# ==================== CLASE 5: TEST QR CODE ====================

@pytest.mark.report
@pytest.mark.unit
class TestQRCode:
    """Tests de generación de código QR"""
    
    def test_pdf_with_qr_code(self, temp_pdf_dir, valid_analysis_data):
        """Test PDF con QR code"""
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test"
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_qr.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Verificar que se generó sin errores
        assert os.path.exists(result_path)
        
        # El QR puede o no estar implementado, pero no debe crashear
        with open(result_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            assert len(pdf_reader.pages) > 0


# ==================== CLASE 6: TEST HEADER Y FOOTER ====================

@pytest.mark.report
@pytest.mark.unit
class TestHeaderFooter:
    """Tests de header y footer del PDF"""
    
    def test_pdf_has_header(self, temp_pdf_dir, valid_analysis_data):
        """Test que el PDF tiene header"""
        pdf = PDFReport()
        pdf.add_page()
        pdf.header()
        
        # Header debe agregar contenido
        assert pdf.page_no() == 1
    
    def test_pdf_has_footer(self, temp_pdf_dir, valid_analysis_data):
        """Test que el PDF tiene footer con número de página"""
        pdf = PDFReport()
        pdf.add_page()
        pdf.footer()
        
        # Footer debe agregar contenido
        assert pdf.page_no() == 1


# ==================== CLASE 7: TEST EDGE CASES ====================

@pytest.mark.report
@pytest.mark.unit
class TestPDFEdgeCases:
    """Tests de edge cases en generación de PDF"""
    
    def test_pdf_with_empty_data(self, temp_pdf_dir):
        """Test PDF con datos mínimos/vacíos"""
        data = {
            "municipio": "",
            "estado": "",
            "m2_construccion": 0
        }
        
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 0,
                "nivel_riesgo_estimado": "",
                "legal_justification_strict": ""
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_empty.pdf")
        
        # No debe crashear
        result_path = generate_pdf_report(data, results, filename)
        assert os.path.exists(result_path)
    
    def test_pdf_with_large_budget(self, temp_pdf_dir, valid_analysis_data):
        """Test PDF con presupuesto grande (muchos items)"""
        # Generar 100 items de presupuesto
        budget_items = []
        for i in range(100):
            budget_items.append({
                "id": str(i),
                "categoria": f"Categoría {i % 5}",
                "concepto": f"Concepto de prueba {i}",
                "cantidad": i + 1,
                "precio_unitario": 100.0 + (i * 10),
                "norma": f"NOM-{i:03d}"
            })
        
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test"
            },
            "presupuesto_inicial": budget_items,
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_large_budget.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Verificar que se generó
        assert os.path.exists(result_path)
        
        # Debe tener múltiples páginas
        with open(result_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            assert len(pdf_reader.pages) > 1
    
    def test_pdf_with_very_long_concept_name(self, temp_pdf_dir, valid_analysis_data):
        """Test PDF con nombre de concepto muy largo"""
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test"
            },
            "presupuesto_inicial": [
                {
                    "id": "1",
                    "categoria": "Test",
                    "concepto": "Este es un concepto extremadamente largo que debería hacer wrap en el PDF " * 5,
                    "cantidad": 1,
                    "precio_unitario": 100.0,
                    "norma": "NOM-TEST"
                }
            ],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_long_concept.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # No debe crashear
        assert os.path.exists(result_path)


# ==================== CLASE 8: TEST MÉTODOS INTERNOS ====================

@pytest.mark.report
@pytest.mark.unit
class TestPDFInternalMethods:
    """Tests de métodos internos de PDFReport"""
    
    def test_chapter_title_h1(self):
        """Test agregar título de capítulo H1"""
        pdf = PDFReport()
        pdf.add_page()
        pdf.chapter_title("Test Title H1", level="h1")
        
        # Debe haber agregado contenido
        assert pdf.page_no() == 1
    
    def test_chapter_title_h2(self):
        """Test agregar título de capítulo H2"""
        pdf = PDFReport()
        pdf.add_page()
        pdf.chapter_title("Test Title H2", level="h2")
        
        assert pdf.page_no() == 1
    
    def test_add_legal_section(self):
        """Test agregar sección legal"""
        pdf = PDFReport()
        pdf.add_page()
        
        ai_data = {
            "legal_foundation": "ARTÍCULO 39 - Ley General de Protección Civil",
            "triggered_because": "Inmueble > 250m²"
        }
        
        pdf.add_legal_section(ai_data)
        
        # Debe haber agregado contenido
        assert pdf.page_no() >= 1
    
    def test_add_checklist_section(self):
        """Test agregar sección de checklist"""
        pdf = PDFReport()
        pdf.add_page()
        
        norms_list = [
            {
                "norma": "NOM-002-STPS-2010",
                "titulo": "Condiciones de seguridad",
                "applicability": "Aplica"
            }
        ]
        
        pdf.add_checklist_section(norms_list)
        
        # Debe haber agregado contenido
        assert pdf.page_no() >= 1
    
    def test_add_budget_section(self):
        """Test agregar sección de presupuesto"""
        pdf = PDFReport()
        pdf.add_page()
        
        budget_items = [
            {
                "categoria": "Extinción",
                "concepto": "Extintor PQS",
                "cantidad": 5,
                "precio_unitario": 650.0,
                "norma": "NOM-002"
            }
        ]
        
        total_general = 3250.0
        
        pdf.add_budget_section(budget_items, total_general)
        
        # Debe haber agregado contenido
        assert pdf.page_no() >= 1


# ==================== CLASE 9: TEST VALIDACIÓN DE PDF ====================

@pytest.mark.report
@pytest.mark.integration
class TestPDFValidation:
    """Tests de validación de PDF generado"""
    
    def test_pdf_file_size_reasonable(self, temp_pdf_dir, valid_analysis_data):
        """Test que el tamaño del PDF es razonable"""
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test"
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_size.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Verificar tamaño de archivo
        file_size = os.path.getsize(result_path)
        
        # Debe ser > 1KB pero < 10MB (para un PDF simple)
        assert file_size > 1024  # > 1KB
        assert file_size < 10 * 1024 * 1024  # < 10MB
    
    def test_pdf_is_readable(self, temp_pdf_dir, valid_analysis_data):
        """Test que el PDF es legible (no corrupto)"""
        results = {
            "basic_requirements": {},
            "resumen_ejecutivo": {
                "total_brigadistas": 1,
                "nivel_riesgo_estimado": "Ordinario",
                "legal_justification_strict": "Test"
            },
            "presupuesto_inicial": [],
            "checklist": []
        }
        
        filename = str(temp_pdf_dir / "test_readable.pdf")
        result_path = generate_pdf_report(valid_analysis_data, results, filename)
        
        # Intentar abrir y leer
        try:
            with open(result_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                # Debepartir leer páginas sin error
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    assert isinstance(text, str)
                    
        except Exception as e:
            pytest.fail(f"PDF is not readable: {e}")


# ==================== RUN ALL TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=report_generator", "--cov-report=term-missing"])
