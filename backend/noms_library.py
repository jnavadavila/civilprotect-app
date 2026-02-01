import json
import os
from municipality_auto_registry import auto_register_municipality, slugify

# --- 1. CARGA DE BASE DE DATOS (JSON) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "legal_db.json")

def load_legal_db():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading legal_db.json: {e}")
        # Retornar estructura vacía para evitar crash y permitir fallback
        return {"state_laws": {}, "risk_config": {}, "guide_structure": [], "specific_noms": {}}

LEGAL_DB = load_legal_db()

# Asignación de bases de datos
STATE_LAWS = LEGAL_DB.get("state_laws", {})
RISK_CONFIG = LEGAL_DB.get("risk_config", {})
PIPC_GUIDE_STRUCTURE = LEGAL_DB.get("guide_structure", [])
SPECIFIC_NOMS = LEGAL_DB.get("specific_noms", {})

# [HOTFIX] Inyección de Normas Faltantes (Blindaje)
if "NOM-245-SSA1-2010" not in SPECIFIC_NOMS:
    SPECIFIC_NOMS["NOM-245-SSA1-2010"] = {
        "titulo": "Requisitos sanitarios y seguridad en albercas",
        "puntos_revision": [
            {"id": "SSA-01", "desc": "Bitácora de control de Cloro Residual y pH (Registro Diario)", "art": "Num. 5.1"},
            {"id": "SSA-02", "desc": "Reglamento de uso y seguridad visible a usuarios", "art": "Num. 6.2"},
            {"id": "PC-01", "desc": "Señalización de profundidad (Marcaje en borde y muro)", "art": "Reglamento Local PC"},
            {"id": "PC-02", "desc": "Equipo de rescate (Gancho, Aro salvavidas, Botiquín)", "art": "Reglamento Local PC"},
            {"id": "SSA-04", "desc": "Piso antiderrapante en áreas húmedas y de tránsito", "art": "Num 5.5"}
        ]
    }

# Fallback si falla la carga o está vacío
if not STATE_LAWS:
    STATE_LAWS = {
        "default": {
            "ley": "Ley General de Protección Civil (Supletoria)", 
            "art_pipc": "Art. 39",
            "reg": "Reglamento de la Ley General de Protección Civil",
            "art_reg": "Art. 74",
            "term_responsiva": "Carta de Corresponsabilidad",
            "term_estructural": "Dictamen de Seguridad Estructural"
        },
        "Aguascalientes": {"ley": "Ley de Protección Civil del Estado de Aguascalientes", "art_pipc": "Art. 45", "reg": "Reglamento de la Ley de PC", "art_reg": "Art. 20"},
        "Baja California": {"ley": "Ley de Protección Civil y Gestión de Riesgos de BC", "art_pipc": "Art. 58", "reg": "Reglamento de la Ley de PC", "art_reg": "Art. 30"},
        "Baja California Sur": {"ley": "Ley de Protección Civil de B.C.S.", "art_pipc": "Art. 33", "reg": "Reglamento de la Ley de PC", "art_reg": "Art. 15"},
        "Campeche": {"ley": "Ley de Protección Civil del Estado de Campeche", "art_pipc": "Art. 60", "reg": "Reglamento Estatal de PC", "art_reg": "Art. 25"},
        "Coahuila": {"ley": "Ley de Protección Civil para el Estado de Coahuila", "art_pipc": "Art. 42", "reg": "Reglamento de la Ley", "art_reg": "Art. 18"},
        "Colima": {"ley": "Ley de Protección Civil del Estado de Colima", "art_pipc": "Art. 55", "reg": "Reglamento de PC", "art_reg": "Art. 22"},
        "Chiapas": {"ley": "Ley de Protección Civil del Estado de Chiapas", "art_pipc": "Art. 74", "reg": "Reglamento de la Ley de PC", "art_reg": "Art. 40"},
        "Chihuahua": {"ley": "Ley de Protección Civil del Estado de Chihuahua", "art_pipc": "Art. 68", "reg": "Reglamento de PC", "art_reg": "Art. 35"},
        "Ciudad de México": {
            "ley": "Ley de Gestión Integral de Riesgos y PC de la CDMX", 
            "art_pipc": "Art. 58", 
            "reg": "Reglamento de la LGIRPC", 
            "art_reg": "Art. 45",
            "term_responsiva": "Carta de Responsabilidad (Tercero Acreditado)",
            "term_estructural": "Constancia de Seguridad Estructural"
        },
        "Durango": {"ley": "Ley de Protección Civil del Estado de Durango", "art_pipc": "Art. 40", "reg": "Reglamento de PC", "art_reg": "Art. 12"},
        "Guanajuato": {"ley": "Ley de Protección Civil para el Estado de Guanajuato", "art_pipc": "Art. 39", "reg": "Reglamento de la Ley", "art_reg": "Art. 28"},
        "Guerrero": {"ley": "Ley de Protección Civil del Estado de Guerrero", "art_pipc": "Art. 50", "reg": "Reglamento de la Ley 656", "art_reg": "Art. 45"},
        "Hidalgo": {"ley": "Ley de Protección Civil del Estado de Hidalgo", "art_pipc": "Art. 72", "reg": "Reglamento de PC", "art_reg": "Art. 33"},
        "Jalisco": {"ley": "Ley del Sistema Estatal de Protección Civil de Jalisco", "art_pipc": "Art. 24", "reg": "Reglamento de la Ley", "art_reg": "Art. 15"},
        "México": {"ley": "Libro Sexto del Código Administrativo del EDOMEX", "art_pipc": "Art. 6.18", "reg": "Reglamento del Libro Sexto", "art_reg": "Art. 72"},
        "Michoacán": {"ley": "Ley de Protección Civil del Estado de Michoacán", "art_pipc": "Art. 55", "reg": "Reglamento de PC", "art_reg": "Art. 20"},
        "Morelos": {"ley": "Ley de Protección Civil del Estado de Morelos", "art_pipc": "Art. 48", "reg": "Reglamento de PC", "art_reg": "Art. 19"},
        "Nayarit": {"ley": "Ley de Protección Civil del Estado de Nayarit", "art_pipc": "Art. 62", "reg": "Reglamento de PC", "art_reg": "Art. 25"},
        "Nuevo León": {"ley": "Ley de Protección Civil del Estado de Nuevo León", "art_pipc": "Art. 18", "reg": "Reglamento de la Ley", "art_reg": "Art. 10"},
        "Oaxaca": {"ley": "Ley de Protección Civil del Estado de Oaxaca", "art_pipc": "Art. 44", "reg": "Reglamento de PC", "art_reg": "Art. 21"},
        "Puebla": {"ley": "Ley del Sistema Estatal de Protección Civil de Puebla", "art_pipc": "Art. 66", "reg": "Reglamento de la Ley", "art_reg": "Art. 30"},
        "Querétaro": {"ley": "Ley de Protección Civil del Estado de Querétaro", "art_pipc": "Art. 54", "reg": "Reglamento de PC", "art_reg": "Art. 22"},
        "Quintana Roo": {"ley": "Ley de Protección Civil del Estado de Quintana Roo", "art_pipc": "Art. 88", "reg": "Reglamento de la Ley", "art_reg": "Art. 45"},
        "San Luis Potosí": {"ley": "Ley del Sistema de Protección Civil de S.L.P.", "art_pipc": "Art. 52", "reg": "Reglamento de la Ley", "art_reg": "Art. 18"},
        "Sinaloa": {"ley": "Ley de Protección Civil del Estado de Sinaloa", "art_pipc": "Art. 70", "reg": "Reglamento de PC", "art_reg": "Art. 35"},
        "Sonora": {"ley": "Ley de Protección Civil para el Estado de Sonora", "art_pipc": "Art. 38", "reg": "Reglamento de PC", "art_reg": "Art. 14"},
        "Tabasco": {"ley": "Ley de Protección Civil del Estado de Tabasco", "art_pipc": "Art. 65", "reg": "Reglamento de la Ley", "art_reg": "Art. 28"},
        "Tamaulipas": {"ley": "Ley de Protección Civil del Estado de Tamaulipas", "art_pipc": "Art. 41", "reg": "Reglamento de PC", "art_reg": "Art. 16"},
        "Tlaxcala": {"ley": "Ley de Protección Civil del Estado de Tlaxcala", "art_pipc": "Art. 53", "reg": "Reglamento de PC", "art_reg": "Art. 20"},
        "Veracruz": {"ley": "Ley de PC y Reducción de Riesgo de Veracruz", "art_pipc": "Art. 66", "reg": "Reglamento de la Ley 856", "art_reg": "Art. 40"},
        "Yucatán": {"ley": "Ley de Protección Civil del Estado de Yucatán", "art_pipc": "Art. 59", "reg": "Reglamento de la Ley", "art_reg": "Art. 33"},
        "Zacatecas": {"ley": "Ley de Protección Civil del Estado de Zacatecas", "art_pipc": "Art. 35", "reg": "Reglamento Provisional", "art_reg": "Art. 10"}
    }

# --- 2. LOGICA DE GUIAS ESPECIFICAS (FEDERAL vs ESTATAL) ---
def get_pipc_guide(estado: str) -> list:
    """
    Retorna la estructura de la guía dependiendo si es Federal o un Estado con guía muy propia (CDMX, etc).
    """
    
    # RECUPERAR DATOS ESTATALES EXACTOS
    # Si el estado no está en la db, usa default
    state_data = STATE_LAWS.get(estado, STATE_LAWS.get("default", {}))
    
    ley_nombre = state_data.get("ley", "Ley General de Protección Civil")
    art_obligatorio = state_data.get("art_pipc", "Art. 39")
    nombre_responsiva = state_data.get("term_responsiva", "Carta de Corresponsabilidad")
    nombre_estructural = state_data.get("term_estructural", "Dictamen Estructural")
    
    # METODOLOGIA DE RIESGO
    metodologia_riesgo = RISK_CONFIG.get(estado, RISK_CONFIG.get("default", "Metodología General CENAPRED"))

    # CONSTRUCCION DINÁMICA DE LA GUIA (NIVEL EXPERTO)
    
    guia_dinamica = [
        {
            "capitulo": f"1. DATOS ADMINISTRATIVOS Y JURÍDICOS ({estado.upper()})",
            "items": [
                {"req": f"{nombre_responsiva} (Vigente)", "fundamento": f"{art_obligatorio} de la {ley_nombre}"},
                {"req": "Acta Constitutiva y Poder Notarial del Representante", "fundamento": "Código Civil / Mercantil"},
                {"req": "Póliza de Seguro de Responsabilidad Civil (Daños a Terceros)", "fundamento": "Reglamento Local de PC"},
                {"req": "Licencia de Funcionamiento / Uso de Suelo", "fundamento": "Ley de Establecimientos Mercantiles"}
            ]
        },
        {
            "capitulo": "2. ANALISIS DE RIESGOS Y VULNERABILIDAD",
            "items": [
                {"req": "Identificación de Riesgos Internos y Externos", "fundamento": f"{art_obligatorio} de la Ley Estatal"},
                {"req": f"Estudio de Riesgo: {metodologia_riesgo}", "fundamento": "LINK: https://www.gob.mx/cms/uploads/attachment/file/113618/Guia_para_la_Presentacion_del_Estudio_de_Riesgo.pdf"},
                {"req": f"{nombre_estructural} (Firmado por Perito/DRO)", "fundamento": "Reglamento de Construcciones Estatal"}
            ]
        },
        {
            "capitulo": "3. PLAN DE OPERACIONES DE EMERGENCIA",
            "items": [
                {"req": "Acta de Conformación de la Unidad Interna de PC", "fundamento": "Normatividad Estatal"},
                {"req": "Directorios de Emergencia y Censo de Población", "fundamento": "Guía Técnica"},
                {"req": "Programa de Capacitación (Cronograma y Constancias)", "fundamento": "NOM-002-STPS / Local"},
                {"req": "Programa de Mantenimiento (Preventivo y Correctivo)", "fundamento": "NOM-001-SEDE / NOM-002-STPS"}
            ]
        }
    ]

    # CASO ESPECIAL CDMX (Extremadamente rigurosa, mantenemos sus extras)
    if estado == "Ciudad de México":
        guia_dinamica[0]["items"].append({
            "req": "Visto Bueno de Seguridad y Operación",
            "fundamento": "Reglamento de Construcciones CDMX"
        })
        guia_dinamica.append({
            "capitulo": "REFERENCIAS TÉCNICAS OFICIALES (CDMX)",
            "items": [
                {"req": "Lineamientos Técnicos Específicos y NTC", "fundamento": "LINK: https://www.proteccioncivil.cdmx.gob.mx/secretaria/marco-normativo"},
                {"req": "Términos de Referencia para PIPC", "fundamento": "Gaceta Oficial CDMX"}
            ]
        })

    return guia_dinamica

# --- HELPER: CARGA DINÁMICA DE ESTADOS (SCALABLE ARCHITECTURE) ---
def get_state_db(estado_nombre):
    """
    Carga bajo demanda el archivo JSON específico del estado desde data/states_db/
    Retorna un dict vacío si no existe, garantizando fallback.
    """
    try:
        slug = slugify(estado_nombre)
        json_path = os.path.join(BASE_DIR, "data", "states_db", f"{slug}.json")
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load state db for {estado_nombre}: {e}")
    
    return {}

def get_applicable_noms(profile: dict):
    """
    Construye el 'Arbol Normativo Completo' con 5 NIVELES (Científico-Legal).
    Nivel 1: Constitución/Leyes Federales
    Nivel 2: Leyes Estatales (Dinámico por Estado)
    Nivel 3: Reglamento Municipal (Dinámico HI-FI o Fallback)
    Nivel 4: Normatividad Técnica (NOMs)
    Nivel 5: Estructura de Guía PIPC (Entregables)
    """
    final_list = []
    estado = profile.get("estado", "default")
    municipio = profile.get("municipio", "Local")

    # Obtener leyes específicas por estado (Base Federal + Override Estatal Dinámico)
    # 1. Cargar DB Estatal Dinámica (Nueva Arquitectura)
    state_db_dynamic = get_state_db(estado)
    
    # [NUEVO] Auto-Registro Inteligente: Si el municipio no existe, lo crea automáticamente
    # Este proceso es no bloqueante y thread-safe
    if municipio and estado and municipio != "Local":
        mun_exists = municipio in state_db_dynamic.get("municipios", {})
        if not mun_exists:
            auto_register_municipality(estado, municipio, BASE_DIR)
            # Recargar DB después del registro
            state_db_dynamic = get_state_db(estado)
    
    # 2. Cargar DB Legacy (Fallback)
    leyes_estatales_legacy = STATE_LAWS.get(estado, STATE_LAWS.get("default", {}))

    # 1. NIVEL FEDERAL (SUPREMO)
    final_list.append({
        "norma": "NIVEL FEDERAL (MARCO GENERAL)",
        "titulo": "Leyes de Observancia Nacional Obligatoria",
        "checks": [
            {"id": "CPEUM", "desc": "Constitución Política EUM - Art. 123 (Seguridad en el Trabajo)", "art": "123"},
            {"id": "LGPC", "desc": "Ley General de Protección Civil - Obligación de Programa Interno", "art": "39 y 40"},
            {"id": "RLGPC", "desc": "Reglamento de la Ley General de Protección Civil", "art": "74 (Contenido PIPC)"},
            {"id": "LFT", "desc": "Ley Federal del Trabajo", "art": "132 y 475"}
        ]
    })

    # 2. NIVEL ESTATAL
    # Preferimos datos dinámicos, fallback a legacy
    ley_nombre = state_db_dynamic.get("state_law", {}).get("ley_nombre") or leyes_estatales_legacy.get("ley", "Ley Estatal PC")
    art_ley = state_db_dynamic.get("state_law", {}).get("art_obligatorio") or leyes_estatales_legacy.get("art_pipc", "Art. Variable")
    reg_nombre = state_db_dynamic.get("state_law", {}).get("reglamento_nombre") or leyes_estatales_legacy.get("reg", "Reglamento Estatal PC")
    art_reg = state_db_dynamic.get("state_law", {}).get("art_reglamento") or leyes_estatales_legacy.get("art_reg", "Art. Variable")

    final_list.append({
        "norma": f"NIVEL ESTATAL: {estado.upper()}",
        "titulo": "Leyes y Reglamentos de Observancia Estatal",
        "checks": [
            {"id": "LEY_EST", "desc": ley_nombre, "art": art_ley},
            {"id": "REG_EST", "desc": reg_nombre, "art": f"{art_reg} (Requisitos Técnicos)"}
        ]
    })

    # 3. NIVEL MUNICIPAL (ARQUITECTURA ESCALABLE)
    # Buscamos datos específicos del municipio en la DB estatal cargada
    mun_data = state_db_dynamic.get("municipios", {}).get(municipio, {})
    
    if mun_data:
        # DATA EXACTA ENCONTRADA (Nivel Oro)
        reg_mun_desc = mun_data.get("reglamento", f"Reglamento de PC de {municipio}")
        reg_mun_art = mun_data.get("art_inspeccion", "Art. Variable")
        bando_desc = mun_data.get("bando", f"Bando Municipal de {municipio}")
        bando_art = mun_data.get("art_bando", "Orden Público")
    else:
        # FALLBACK INTELIGENTE (Nivel Plata)
        reg_mun_desc = f"Reglamento de Protección Civil del Municipio de {municipio}"
        reg_mun_art = "Art. Fundamento (Facultad de Inspección)"
        bando_desc = f"Bando Municipal de Policía y Buen Gobierno de {municipio}"
        bando_art = "Orden Público y Convivencia"

    final_list.append({
        "norma": f"NIVEL MUNICIPAL: {municipio.upper()}",
        "titulo": "Reglamentación de Proximidad y Bando de Gobierno",
        "checks": [
            {"id": "REG_MUN", "desc": reg_mun_desc, "art": reg_mun_art},
            {"id": "BANDO", "desc": bando_desc, "art": bando_art}
        ]
    })

    # 4. NIVEL TÉCNICO (NOMs) - SELECCIÓN EXHAUSTIVA
    universales = [
        "NOM-001-SEDE-2012", # Diseño Eléctrico
        "NOM-029-STPS-2011", # Mantenimiento Eléctrico [CORRECCION]
        "NOM-001-STPS-2008", # Edificios (Escaleras/Rampas)
        "NOM-002-STPS-2010", # Incendios
        "NOM-003-SEGOB-2011", # Señales
        "NOM-030-STPS-2009", # Seguridad y Salud [CORRECCION]
        "NOM-008-SEGOB-2015",
        "NOM-017-STPS-2008",
        "NOM-022-STPS-2015",
        "NOM-154-SCFI-2005"
    ]
    
    # Agregar condicionales de infraestructura
    if profile.get("has_cocina") or profile.get("has_gas", True):
        universales.append("NOM-004-SEDG-2004")
    if profile.get("has_elevators") or profile.get("niveles", 1) > 2:
        universales.append("NOM-207-SCFI-2018")
    if profile.get("is_industrial") or profile.get("has_chemicals", False) or profile.get("has_substation", False):
        universales.append("NOM-005-STPS-1998")
        universales.append("NOM-018-STPS-2015")
    if profile.get("has_pressure") or profile.get("has_machine_room", False):
        universales.append("NOM-020-STPS-2011")
    if profile.get("has_heights", False): # Nuevo trigger detectado en JSON
        universales.append("NOM-009-STPS-2011")
    if profile.get("has_pool"):
        universales.append("NOM-245-SSA1-2010")
    if profile.get("has_special_inst"):
        universales.append("NOM-020-STPS-2011") # Recipientes Sujetos a Presión

    checks_nom = []
    
    for nom_key in universales:
        if nom_key in SPECIFIC_NOMS:
            data = SPECIFIC_NOMS[nom_key]
            final_list.append({
                "norma": nom_key,
                "titulo": data["titulo"],
                "checks": data["puntos_revision"]
            })

    # 5. NIVEL GUÍA DE INTEGRACIÓN (PIPC FOLDER)
    # Lógica Dinámica: Federal (SINAPROC) vs Estatal Específica (CDMX, etc)
    guia_pipc_aplicable = get_pipc_guide(estado)

    final_list.append({
        "norma": "GUÍA DE INTEGRACIÓN DOCUMENTAL (CARPETA TÉCNICA)",
        # Se agrega explícitamente "TRPC" (Términos de Referencia)
        "titulo": f"Estructura Mínima Capitular Obligatoria del PIPC (TRPC {'CDMX' if estado == 'Ciudad de México' else 'FEDERAL/ESTATAL'})",
        "checks": [],
        "is_pipc_guide": True,
        "guide_content": guia_pipc_aplicable
    })

    return final_list
