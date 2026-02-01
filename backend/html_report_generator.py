"""
Generador de Reportes HTML Premium
Versión V4.0 - Sistema de Reportes Interactivos de Alta Gama
"""
from datetime import datetime
import qrcode
import io
import base64

def generate_html_report(input_data: dict, analysis_data: dict) -> str:
    """
    Genera un reporte HTML premium con diseño moderno y profesional.
    
    Args:
        input_data: Datos del formulario
        analysis_data: Resultados del análisis completo
    
    Returns:
        str: HTML completo del reporte
    """
    
    # Extraer datos principales
    municipio = input_data.get("municipio", "N/A")
    estado = input_data.get("estado", "N/A")
    tipo_inmueble = input_data.get("tipo_inmueble", "N/A")
    m2 = input_data.get("m2_construccion", 0)
    niveles = input_data.get("niveles", 1)
    aforo = input_data.get("aforo", 0)
    trabajadores = input_data.get("trabajadores", 0)
    
    # Generar QR Code
    qr_data = f"Dictamen PC - {municipio}, {estado} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir QR a base64
    buffer = io.BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Obtener datos del análisis
    basic_info = analysis_data.get("basic_info", {})
    checklist = analysis_data.get("normative_checklist", [])
    presupuesto = analysis_data.get("budget_breakdown", {})
    
    # Construir lista de normativa
    normas_html = ""
    for idx, norma in enumerate(checklist, 1):
        normas_html += f"""
        <div class="norma-card">
            <div class="norma-header">
                <div class="norma-numero">{idx}</div>
                <h3 class="norma-titulo">{norma.get('norma', 'N/A')}</h3>
            </div>
            <div class="norma-body">
                <p class="norma-titulo-completo">{norma.get('titulo', 'N/A')}</p>
                <div class="norma-articulos">
                    <span class="label">Artículo:</span>
                    <span class="value">{norma.get('articulo', 'N/A')}</span>
                </div>
                <div class="norma-fundamento">
                    <span class="label">Fundamento:</span>
                    <p>{norma.get('fundamento_legal', 'N/A')}</p>
                </div>
            </div>
        </div>
        """
    
    # Construir presupuesto
    items_presupuesto = presupuesto.get("items", [])
    presupuesto_html = ""
    total_sin_iva = 0
    
    for item in items_presupuesto:
        cantidad = item.get("quantity", 0)
        precio_unit = item.get("unit_price", 0)
        subtotal = cantidad * precio_unit
        total_sin_iva += subtotal
        
        presupuesto_html += f"""
        <tr>
            <td class="concepto-col">{item.get('concept', 'N/A')}</td>
            <td class="center">{cantidad}</td>
            <td class="right">${precio_unit:,.2f}</td>
            <td class="right total">${subtotal:,.2f}</td>
        </tr>
        """
    
    iva = total_sin_iva * 0.16
    total_con_iva = total_sin_iva + iva
    
    # Plantilla HTML Premium
    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dictamen de Protección Civil - {municipio}, {estado}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            color: #2d3748;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
            color: white;
            padding: 60px 40px;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="rgba(255,255,255,0.1)" d="M0,96L48,112C96,128,192,160,288,165.3C384,171,480,149,576,128C672,107,768,85,864,90.7C960,96,1056,128,1152,138.7C1248,149,1344,139,1392,133.3L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
            background-size: cover;
            opacity: 0.3;
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .logo {{
            font-size: 48px;
            font-weight: 900;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .subtitle {{
            font-size: 18px;
            opacity: 0.95;
            letter-spacing: 2px;
            text-transform: uppercase;
            font-weight: 600;
        }}
        
        .dictamen-title {{
            font-size: 32px;
            font-weight: 800;
            margin-top: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .section {{
            padding: 40px;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #3b82f6;
        }}
        
        .section-icon {{
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #3b82f6, #1e3a8a);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
        }}
        
        .section-title {{
            font-size: 28px;
            font-weight: 800;
            color: #1e3a8a;
        }}
        
        .ficha-tecnica {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .ficha-item {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #3b82f6;
            transition: transform 0.3s;
        }}
        
        .ficha-item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
        }}
        
        .ficha-label {{
            font-size: 12px;
            text-transform: uppercase;
            color: #1e40af;
            font-weight: 700;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        
        .ficha-value {{
            font-size: 24px;
            font-weight: 800;
            color: #1e3a8a;
        }}
        
        .norma-card {{
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s;
        }}
        
        .norma-card:hover {{
            border-color: #3b82f6;
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.15);
            transform: translateX(5px);
        }}
        
        .norma-header {{
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .norma-numero {{
            width: 40px;
            height: 40px;
            background: rgba(255,255,255,0.3);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 18px;
        }}
        
        .norma-titulo {{
            font-size: 18px;
            font-weight: 700;
        }}
        
        .norma-body {{
            padding: 20px;
        }}
        
        .norma-titulo-completo {{
            font-size: 16px;
            color: #374151;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        
        .norma-articulos {{
            background: #fef3c7;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #f59e0b;
        }}
        
        .norma-fundamento {{
            background: #f0fdf4;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #10b981;
        }}
        
        .label {{
            font-weight: 700;
            color: #374151;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 1px;
        }}
        
        .value {{
            font-weight: 600;
            color: #1e3a8a;
        }}
        
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: 20px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        thead {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
        }}
        
        th {{
            padding: 18px;
            text-align: left;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 1px;
        }}
        
        tbody tr {{
            background: white;
            transition: background 0.3s;
        }}
        
        tbody tr:nth-child(even) {{
            background: #f9fafb;
        }}
        
        tbody tr:hover {{
            background: #eff6ff;
        }}
        
        td {{
            padding: 16px 18px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .center {{ text-align: center; }}
        .right {{ text-align: right; }}
        
        .concepto-col {{
            font-weight: 600;
            color: #374151;
        }}
        
        .total {{
            font-weight: 800;
            color: #1e3a8a;
        }}
        
        .totales {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
        }}
        
        .totales td {{
            padding: 20px 18px;
            font-size: 18px;
            font-weight: 800;
            border: none;
        }}
        
        .footer {{
            background: #f9fafb;
            padding: 40px;
            text-align: center;
            border-top: 3px solid #3b82f6;
        }}
        
        .qr-container {{
            margin: 20px 0;
        }}
        
        .qr-image {{
            width: 150px;
            height: 150px;
            margin: 0 auto;
        }}
        
        .timestamp {{
            font-size: 14px;
            color: #6b7280;
            margin-top: 20px;
        }}
        
        .firma {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #d1d5db;
        }}
        
        .firma-texto {{
            font-size: 12px;
            color: #6b7280;
            font-style: italic;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                border-radius: 0;
            }}
            
            .norma-card {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Premium -->
        <div class="header">
            <div class="header-content">
                <div class="logo">GIRRD PC AI</div>
                <div class="subtitle">Sistema Experto en Protección Civil</div>
                <div class="dictamen-title">
                    📋 Dictamen Técnico de Cumplimiento Normativo
                </div>
            </div>
        </div>
        
        <!-- Ficha Técnica -->
        <div class="section">
            <div class="section-header">
                <div class="section-icon">📊</div>
                <h2 class="section-title">Ficha Técnica del Inmueble</h2>
            </div>
            
            <div class="ficha-tecnica">
                <div class="ficha-item">
                    <div class="ficha-label">Ubicación</div>
                    <div class="ficha-value">{municipio}, {estado}</div>
                </div>
                <div class="ficha-item">
                    <div class="ficha-label">Tipo de Inmueble</div>
                    <div class="ficha-value">{tipo_inmueble}</div>
                </div>
                <div class="ficha-item">
                    <div class="ficha-label">Superficie</div>
                    <div class="ficha-value">{m2:,} m²</div>
                </div>
                <div class="ficha-item">
                    <div class="ficha-label">Niveles</div>
                    <div class="ficha-value">{niveles}</div>
                </div>
                <div class="ficha-item">
                    <div class="ficha-label">Aforo Máximo</div>
                    <div class="ficha-value">{aforo} personas</div>
                </div>
                <div class="ficha-item">
                    <div class="ficha-label">Personal</div>
                    <div class="ficha-value">{trabajadores} trabajadores</div>
                </div>
            </div>
        </div>
        
        <!-- Marco Normativo -->
        <div class="section" style="background: #f9fafb;">
            <div class="section-header">
                <div class="section-icon">⚖️</div>
                <h2 class="section-title">Marco Normativo Aplicable</h2>
            </div>
            
            {normas_html}
        </div>
        
        <!-- Presupuesto -->
        <div class="section">
            <div class="section-header">
                <div class="section-icon">💰</div>
                <h2 class="section-title">Presupuesto de Cumplimiento</h2>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Concepto</th>
                        <th class="center">Cantidad</th>
                        <th class="right">Precio Unitario</th>
                        <th class="right">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {presupuesto_html}
                </tbody>
                <tfoot class="totales">
                    <tr>
                        <td colspan="3" class="right">SUBTOTAL:</td>
                        <td class="right">${total_sin_iva:,.2f}</td>
                    </tr>
                    <tr>
                        <td colspan="3" class="right">IVA (16%):</td>
                        <td class="right">${iva:,.2f}</td>
                    </tr>
                    <tr>
                        <td colspan="3" class="right">TOTAL:</td>
                        <td class="right">${total_con_iva:,.2f}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        
        <!-- Footer con QR -->
        <div class="footer">
            <div class="qr-container">
                <img src="data:image/png;base64,{qr_base64}" class="qr-image" alt="QR Code">
            </div>
            <div class="timestamp">
                Generado el {datetime.now().strftime('%d de %B de %Y a las %H:%M hrs')}
            </div>
            <div class="firma">
                <p class="firma-texto">
                    Este documento fue generado automáticamente por GIRRD PC AI<br>
                    Sistema Experto en Análisis Normativo para Protección Civil<br>
                    © 2026 Lunaya CI - Todos los derechos reservados
                </p>
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    return html_template
