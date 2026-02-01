"""
Sistema de Auto-Registro de Municipios
Auto-populate de la base de datos estatal conforme se van analizando municipios.
Thread-safe, no bloqueante, incremental.
"""
import json
import os
import unicodedata
from pathlib import Path
from threading import Lock

# Thread-safety lock para escritura concurrente
_write_lock = Lock()

def slugify(value):
    """Normaliza strings para nombres de archivo: 'Ciudad de México' -> 'ciudad_de_mexico'"""
    value = str(value).lower()
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    return value.replace(' ', '_')

def auto_register_municipality(estado_nombre, municipio_nombre, base_dir):
    """
    Auto-registra un municipio en la DB estatal si no existe.
    **AHORA CON INVESTIGACIÓN AUTOMÁTICA DE IA**
    Crea el archivo JSON del estado si no existe.
    Thread-safe y no bloqueante.
    
    Args:
        estado_nombre (str): Nombre del estado (ej. "Morelos")
        municipio_nombre (str): Nombre del municipio (ej. "Cuautla")
        base_dir (str): Directorio base del backend
    
    Returns:
        bool: True si se registró exitosamente, False si ya existía o hubo error
    """
    try:
        with _write_lock:  # Evita corrupción por escritura concurrente
            # 1. Construir ruta del archivo
            slug = slugify(estado_nombre)
            states_db_dir = os.path.join(base_dir, "data", "states_db")
            Path(states_db_dir).mkdir(parents=True, exist_ok=True)
            
            json_path = os.path.join(states_db_dir, f"{slug}.json")
            
            # 2. Cargar o crear estructura base
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
            else:
                # Crear estructura base si no existe el estado
                state_data = {
                    "_meta": {
                        "estado": estado_nombre,
                        "last_updated": "Auto-generado",
                        "auto_populated": True
                    },
                    "state_law": {
                        "ley_nombre": f"Ley de Protección Civil del Estado de {estado_nombre}",
                        "art_obligatorio": "Art. Variable",
                        "reglamento_nombre": f"Reglamento de la Ley de Protección Civil de {estado_nombre}",
                        "art_reglamento": "Art. Variable"
                    },
                    "municipios": {}
                }
            
            # 3. Verificar si el municipio ya existe
            if municipio_nombre in state_data.get("municipios", {}):
                return False  # Ya existe, no hacer nada
            
            # 4. [NUEVO] INVESTIGACIÓN CON IA DE LA NORMATIVA ESPECÍFICA
            from ai_service import AIService
            ai = AIService()
            
            print(f"🔍 Investigando normativa para {municipio_nombre}, {estado_nombre}...")
            municipal_regs = ai.research_municipal_regulations(estado_nombre, municipio_nombre)
            
            # 5. Agregar municipio con estructura ENRIQUECIDA POR IA
            if "municipios" not in state_data:
                state_data["municipios"] = {}
            
            state_data["municipios"][municipio_nombre] = {
                "reglamento": municipal_regs.get("reglamento", f"Reglamento de PC de {municipio_nombre}"),
                "bando": municipal_regs.get("bando", f"Bando Municipal de {municipio_nombre}"),
                "art_inspeccion": municipal_regs.get("art_inspeccion", "Art. Variable"),
                "art_bando": municipal_regs.get("art_bando", "Orden Público"),
                "_ai_researched": True,
                "_research_timestamp": str(__import__('datetime').datetime.now())
            }
            
            # 6. Guardar archivo actualizado
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=4)
            
            print(f"✅ Auto-registrado CON IA: {municipio_nombre}, {estado_nombre}")
            return True
            
    except Exception as e:
        # NO FALLAR si hay error de escritura (permisos, disco lleno, etc)
        print(f"⚠ Warning: No se pudo auto-registrar {municipio_nombre}: {e}")
        return False

def get_municipality_count(estado_nombre, base_dir):
    """
    Retorna el número de municipios registrados para un estado.
    Útil para estadísticas y monitoreo.
    """
    try:
        slug = slugify(estado_nombre)
        json_path = os.path.join(base_dir, "data", "states_db", f"{slug}.json")
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
                return len(state_data.get("municipios", {}))
    except:
        pass
    
    return 0
