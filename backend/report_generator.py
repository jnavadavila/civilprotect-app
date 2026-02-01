from fpdf import FPDF
import os
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        # Skip header on first page (Cover Page handles its own header)
        if self.page_no() == 1:
            return

        # Fondo de encabezado
        self.set_fill_color(30, 60, 100) # Azul Institucional
        self.rect(0, 0, 210, 25, 'F')
        
        self.set_font('Arial', 'B', 14)
        self.set_text_color(255)
        self.set_y(8)
        self.cell(0, 10, 'ANALISIS TÉCNICO DE OBLIGATORIEDAD EN MATERIA DE P.C.', 0, 1, 'C')
        
        self.set_font('Arial', '', 9)
        self.cell(0, 5, 'Sistema Experto de Análisis Normativo (LY GIRRD PC AI V3.0)', 0, 1, 'C')
        
        self.ln(10)
        self.set_text_color(0)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100)
        self.cell(0, 6, f'Página {self.page_no()} | Generado el {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
        self.cell(0, 5, 'Este documento es una guía técnica pre-aprobatoria. No sustituye la revisión final de la autoridad. DR. JMND', 0, 0, 'C')

    def chapter_title(self, label, level='h1'):
        if level == 'h1':
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(240, 245, 255)
            self.set_text_color(0, 50, 120)
            # Usamos multi_cell para permitir ajuste a 2 líneas si es largo
            # Border=1 dibuja el recuadro automático
            self.multi_cell(0, 8, label.upper(), 1, 'L', True)
        elif level == 'h2':
            self.set_font('Arial', 'B', 11)
            self.set_text_color(0, 0, 0)
            self.cell(0, 8, label, 'B', 1, 'L')
        self.ln(4)
        self.set_text_color(0)

    def add_legal_section(self, ai_data):
        # NOTA: La justificación legal principal ya se imprime en la Portada (Página 1).
        # Aquí solo imprimimos actualizaciones normativas si existen, en una nueva hoja.
        
        if not ai_data.get("normative_updates"):
            return

        self.add_page()
        self.chapter_title("1.1 VIGILANCIA NORMATIVA LOCAL", 'h2')
        
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, "Actualizaciones y Decretos Relevantes:", 0, 1)
        self.set_font('Arial', '', 9)
        for update in ai_data.get("normative_updates", []):
            self.cell(5) # Indent
            self.cell(0, 5, f"> {update}", 0, 1)
        self.ln(5)

    def add_checklist_section(self, norms_list):
        if not norms_list: return
        
        self.add_page()
        self.chapter_title("2. MATRIZ DE CUMPLIMIENTO (SISTEMA JERÁRQUICO)", 'h1')
        
        # Filtramos la guía de integración (se muestra aparte)
        strict_norms = [n for n in norms_list if not n.get('is_pipc_guide')]
        
        for norm in strict_norms:
            # Determinamos color de jerarquía
            norm_name = norm.get('norma', '')
            if "FEDERAL" in norm_name or "Constitución" in norm_name:
                self.set_fill_color(255, 200, 200) # Rojo claro
            elif "ESTATAL" in norm_name:
                self.set_fill_color(255, 230, 200) # Naranja claro
            elif "MUNICIPAL" in norm_name:
                self.set_fill_color(255, 255, 200) # Amarillo claro
            else:
                self.set_fill_color(230, 255, 230) # Verde técnico

            # Encabezado de la Norma
            self.set_font('Arial', 'B', 9)
            self.cell(0, 6, f"{norm['norma']} - {norm['titulo']}", 1, 1, 'L', 1)
            
            # Puntos de chequeo
            self.set_font('Arial', '', 8)
            for check in norm['checks']:
                desc = check['desc'][:95] + "..." if len(check['desc']) > 95 else check['desc']
                
                self.cell(10) # Indent
                self.cell(140, 5, f"[ ] {desc}", 0, 0)
                
                # Fundamento alineado a derecha (Trucado para evitar desborde en PDF)
                art_text = str(check['art'])
                if len(art_text) > 30:
                    art_ref = f"(Ref: {art_text[:25]}...)"
                else:
                    art_ref = f"(Ref: Art. {art_text})"
                
                self.set_font('Arial', 'I', 7)
                self.set_text_color(100)
                self.cell(40, 5, art_ref, 0, 1, 'R')
                self.set_text_color(0)
                self.set_font('Arial', '', 8)
            
            self.ln(2)

    def add_integration_guide(self, norms_list):
        # Buscar la estructura de guía PIPC
        guide_data = next((n for n in norms_list if n.get('is_pipc_guide')), None)
        if not guide_data: return
        
        self.add_page()
        # [CORRECCIÓN] Usar el título dinámico que trae "TRPC" y el estado específico
        titulo_dinamico = guide_data.get('titulo', "GUÍA DE INTEGRACIÓN DOCUMENTAL")
        self.chapter_title(f"3. {titulo_dinamico}", 'h1')
        self.set_font('Arial', 'I', 9)
        self.multi_cell(0, 5, "Use este listado como carátula para la integración física de la carpeta técnica. El orden presentado cumple con TR-SGIRPC y Guías Estatales.", 0, 'L')
        self.ln(4)
        
        for capitulo in guide_data.get('guide_content', []):
            self.set_font('Arial', 'B', 10)
            self.set_fill_color(240, 240, 240)
            self.cell(0, 7, capitulo['capitulo'], 1, 1, 'L', 1)
            
            self.set_font('Arial', '', 9)
            for item in capitulo['items']:
                self.cell(5) # Indent
                
                # Checkbox visual
                self.rect(self.get_x(), self.get_y()+1, 3, 3) 
                self.cell(5)
                
                self.cell(130, 6, item['req'], 0, 0)
                self.set_font('Arial', 'B', 7)
                self.cell(50, 6, f"[{item['fundamento']}]", 0, 1, 'R')
                self.set_font('Arial', '', 9)
            self.ln(2)

    def add_budget_section(self, budget_items, total_general):
        self.add_page()
        self.chapter_title("4. PRESUPUESTO PRELIMINAR DE IMPLEMENTACIÓN", 'h1')
        
        # Agrupar items por Categoría
        from itertools import groupby
        budget_items.sort(key=lambda x: x['categoria'])
        
        self.set_font('Arial', 'B', 8)
        
        # Encabezados Tabla
        self.set_fill_color(50, 50, 50)
        self.set_text_color(255)
        self.cell(100, 6, 'CONCEPTO / EMPREGABLE', 1, 0, 'C', 1)
        self.cell(20, 6, 'CANT.', 1, 0, 'C', 1)
        self.cell(35, 6, 'P. UNITARIO', 1, 0, 'C', 1)
        self.cell(35, 6, 'SUBTOTAL', 1, 1, 'C', 1)
        self.set_text_color(0)
        
        self.set_font('Arial', '', 8)
        
        for categoria, items in groupby(budget_items, key=lambda x: x['categoria']):
            # Título de Categoría
            self.set_font('Arial', 'B', 8)
            self.set_fill_color(230, 230, 230)
            self.cell(190, 5, f" CATEGORÍA: {categoria.upper()}", 1, 1, 'L', 1)
            self.set_font('Arial', '', 8)
            
            for item in items:
                importe = item['cantidad'] * item['precio_unitario']
                concepto = item['concepto'][:70] 
                
                self.cell(100, 5, f"  {concepto}", "LRB")
                self.cell(20, 5, str(item['cantidad']), "LRB", 0, 'C')
                self.cell(35, 5, f"${item['precio_unitario']:,.2f}", "LRB", 0, 'R')
                self.cell(35, 5, f"${importe:,.2f}", "LRB", 1, 'R')
        
        # TOTAL FINAL
        self.ln(5)
        self.set_font('Arial', 'B', 11)
        self.cell(155, 8, 'INVERSIÓN ESTIMADA DE CUMPLIMIENTO:', 0, 0, 'R')
        self.set_fill_color(255, 255, 150)
        self.cell(35, 8, f"${total_general:,.2f}", 1, 1, 'C', 1)

def generate_pdf_report(input_data: dict, results: dict, filename: str):
    pdf = PDFReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PÁGINA 1: CARÁTULA "HIGH-END" (REDISEÑO) ---
    pdf.add_page()
    # 0. LOGOTIPO + BRANDING "LY" (Ajuste Radical de Proporciones)
    # Logo Reducido al 50% (aprox 20mm)
    if os.path.exists('logo_lunaya.png'):
        pdf.image('logo_lunaya.png', x=12, y=12, w=20, link='https://lunaya.com.mx/')
    
    # Texto "LY" Aumentado 20% (Tamaño 55)
    # Posición X = 12 + 20 + 2 = 34
    pdf.set_xy(34, 15) # Subimos Y porque la letra es más grande
    pdf.set_font('Helvetica', 'B', 55) 
    
    # Letra L en GRIS
    pdf.set_text_color(100, 100, 100) 
    pdf.cell(11, 20, "L", 0, 0, 'L') 
    
    # Letra Y en NARANJA
    pdf.set_text_color(255, 140, 0) 
    pdf.cell(15, 20, "Y", 0, 0, 'L')
    
    # 1. ENCABEZADO "PREMIUM"
    # Bloque de Título Alineado a la Derecha - Ajustado al nuevo espacio
    pdf.set_y(15) 
    pdf.set_x(80) # Más a la izquierda para balancear
    
    pdf.set_font('Arial', 'B', 14) 
    pdf.set_text_color(20, 40, 80) 
    pdf.multi_cell(0, 7, 'ANALISIS TÉCNICO DE OBLIGATORIEDAD\nEN MATERIA DE P.C.', 0, 'R')
    
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_x(80)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(100, 100, 100) # Gris elegante
    pdf.cell(0, 6, 'Sistema Experto en análisis normativo para PIPC en GIRRD PC', 0, 1, 'R')
    
    # Barra separadora sutil
    pdf.ln(8)
    pdf.set_draw_color(20, 40, 80)
    pdf.set_line_width(0.5)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(10)

    # 2. SECCIÓN: DATOS DEL INMUEBLE (Estilo Ficha Técnica Limpia)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(0)
    # Pequeño adorno visual a la izquierda del título
    pdf.set_fill_color(20, 40, 80)
    pdf.rect(12, pdf.get_y(), 4, 6, 'F') 
    pdf.set_x(18)
    pdf.cell(0, 6, "FICHA TÉCNICA DEL INMUEBLE EVALUADO", 0, 1, 'L')
    pdf.ln(4)
    
    pdf.set_font('Arial', '', 10)
    line_h = 7 # Más aire entre líneas
    
    # Función para fila "Zebra" (Sin bordes)
    def row_clean(label, value, fill=False):
        if fill:
            pdf.set_fill_color(245, 245, 245) # Gris muy tenue
        else:
            pdf.set_fill_color(255, 255, 255)
            
        pdf.cell(12, line_h, "", 0, 0, 'L', fill) # Margen izquierdo
        
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(80, 80, 80) # Etiqueta Gris
        pdf.cell(50, line_h, label, 0, 0, 'L', fill)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(0, 0, 0) # Valor Negro
        pdf.cell(128, line_h, str(value), 0, 1, 'L', fill)

    # Datos
    data_items = [
        ("Tipo Inmueble:", input_data.get('tipo_inmueble', '')),
        ("M2 Construcción:", f"{input_data.get('m2_construccion', '')} m²"),
        ("Niveles:", input_data.get('niveles', '')),
        ("Aforo Real:", f"{input_data.get('aforo', '')} personas"),
        ("Aforo Autorizado:", f"{input_data.get('aforo_autorizado', 'N/D')} personas"),
        ("Trabajadores:", input_data.get('trabajadores', '')),
        ("Ubicación:", f"{input_data.get('municipio', '')}, {input_data.get('estado', '')}"),
        ("Instalaciones:", f"Cocina: {'SÍ' if input_data.get('has_cocina') else 'NO'} | Site: {'SÍ' if input_data.get('has_site') else 'NO'}")
    ]

    fill = True
    for lbl, val in data_items:
        row_clean(lbl, val, fill)
        fill = not fill # Alternar color
    
    # [NUEVO] LEYENDA CAUTELAR DE AFORO (SOLICITADO POR USUARIO EXPERTO)
    m2 = float(input_data.get("m2_construccion", 0) or 0)
    aforo = int(input_data.get("aforo", 0) or 0)
    trabajadores = int(input_data.get("trabajadores", 0) or 0)
    
    # Si la densidad es "apretada" (> 1.5 personas por m2) o el aforo es masivo
    total_personas = aforo + trabajadores
    densidad = total_personas / m2 if m2 > 0 else 0
    
    if densidad > 1.0 or aforo > 500:
        pdf.ln(3) # Espacio antes de la alerta
        pdf.set_fill_color(255, 241, 242) # Rojo Muy Pálido Warning Hex #fff1f2
        pdf.set_text_color(185, 28, 28) # Rojo Oscuro Hex #b91c1c
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 8, "NOTA TÉCNICA: EL ANALISTA DEBE REVISAR LOS AFOROS REALES PARA EVITAR AGLOMERACIONES", 0, 1, 'C', 1)
        pdf.set_text_color(0, 0, 0) # Reset color
    
    pdf.ln(8)

    # 3. SECCIÓN: INFRAESTRUCTURA DE RIESGO
    infra = [] # Inicialización segura SIEMPRE
    
    if any([input_data.get('has_gas'), input_data.get('has_substation'), input_data.get('has_diesel')]):
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(150, 0, 0) # Rojo oscuro para riesgo
        pdf.cell(0, 6, "INFRAESTRUCTURA DE RIESGO DETECTADA:", 0, 1)
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(50, 50, 50)
    if input_data.get("has_gas"): infra.append("Gas LP/Natural")
    if input_data.get("has_substation"): infra.append("Subestación Eléctrica")
    if input_data.get("has_transformer"): infra.append("Transformador")
    if input_data.get("has_machine_room"): infra.append("Cuarto de Máquinas")
    if input_data.get("has_special_inst"): infra.append("Instalaciones Especiales")
    if input_data.get("has_pool"): infra.append("Alberca/Cuerpo de Agua")
    
    infra_text = ", ".join(infra) if infra else "No se reportó infraestructura de alto riesgo."
    pdf.cell(0, 7, infra_text, 1, 1, 'L')
    
    pdf.ln(8)
    
    # 4. JUSTIFICACIÓN LEGAL (Sentencia)
    pdf.ln(4)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(0)
    pdf.cell(0, 6, "FUNDAMENTACIÓN Y MOTIVACIÓN LEGAL:", 0, 1)
    
    pdf.ln(2)
    # Bloque destacado con Barra Lateral
    start_y = pdf.get_y()
    
    pdf.set_fill_color(240, 245, 255) # Azul muy tenue
    pdf.set_draw_color(20, 60, 120) # Borde Azul Fuerte
    
    # Texto Justificado
    pdf.set_font('Arial', '', 10)
    text = results['ai_analysis'].get('legal_justification', "N/A") # Assuming this is the correct source for the text
    
    # Simulación de margen izquierdo de color
    # Calculate height needed for the text to adjust the bar
    text_height = pdf.get_string_width(text) / 180 * 6 # Approx height for multi_cell(180, 6, ...)
    if text_height < 40: text_height = 40 # Ensure minimum height
    
    pdf.rect(12, start_y, 2, text_height, 'F') # Barra lateral
    
    pdf.set_x(16)
    pdf.multi_cell(180, 6, text, 0, 'J', True) # 'True' for fill
    
    pdf.ln(10)
    
    # 5. CODIGO QR Y FIRMA (Footer de Portada)
    # Posicionamos al fondo
    y_pos = 230 
    pdf.set_y(y_pos)
    
    import qrcode
    import uuid
    from datetime import datetime
    # import os REMOVED to fix UnboundLocalError (already global)

    unique_id = uuid.uuid4().hex[:8]
    qr_filename = f"temp_qr_{unique_id}.png"
    
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(f"ANALISIS TÉCNICO DE OBLIGATORIEDAD - {input_data.get('municipio')} - {datetime.now().isoformat()}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    try:
        qr_img.save(qr_filename)
        # Posicionar QR a la izquierda
        y_qr = pdf.get_y()
        pdf.image(qr_filename, x=10, y=y_qr, w=35)
        
        # Firma alineada derecha - Harmonizada con QR (35mm alto)
        # Etiqueta Arriba
        pdf.set_y(y_qr + 5)
        pdf.set_x(120)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(60, 4, "Firma del Perito Responsable:", 0, 1, 'C')

        # [CRITICAL] FIRMA DIGITAL O LINEA
        signature_b64 = input_data.get('signature_image')
        
        if signature_b64 and 'base64,' in signature_b64:
            import base64
            # Decodificar Base64
            sig_data = signature_b64.split('base64,')[1]
            sig_filename = f"temp_sig_{unique_id}.png"
            with open(sig_filename, "wb") as fh:
                fh.write(base64.b64decode(sig_data))
            
            # Dibujar imagen (ajustada para que parezca firma real)
            # Posición: X=130 (centro de la zona de firma), Y=y_qr+10
            pdf.image(sig_filename, x=135, y=y_qr + 10, w=30)
            
            # Limpiar archivo temp
            if os.path.exists(sig_filename):
                os.remove(sig_filename)
        else:
            # Línea de Firma Abajo (Solo si no hay firma digital)
            pdf.set_y(y_qr + 30) # 25mm de separación visual
            pdf.set_x(120)
            pdf.cell(60, 4, "_______________________________________", 0, 1, 'C')

    finally:
            try: os.remove(qr_filename) 
            except: pass
            
    # --- SECCIONES ADICIONALES (Páginas 2...) ---
    
    # 1.1 Vigilancia Normativa (Si hay updates)
    if "ai_analysis" in results:
        pdf.add_legal_section(results["ai_analysis"])
    
    # 2. Checklist Normativo Jerárquico
    if "checklist" in results:
        pdf.add_checklist_section(results["checklist"])
        
    # 3. Guía de Integración (TRPC Estatal/Federal)
    if "checklist" in results:
        pdf.add_integration_guide(results["checklist"])

    # 4. Presupuesto (AL FINAL DEL DOCUMENTO)
    if "presupuesto_inicial" in results:
        items = results["presupuesto_inicial"]
        total = sum([x['cantidad'] * x['precio_unitario'] for x in items])
        pdf.add_budget_section(items, total)
 
    # Directorio de salida
    if not os.path.exists("reports"):
        try: os.makedirs("reports")
        except: pass
            
    pdf.output(filename)

