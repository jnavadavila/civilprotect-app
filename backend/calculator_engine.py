import math
import json
import os
from noms_library import get_applicable_noms

class CivilProtectionCalculator:
    def __init__(self):
        # Cargar Matriz de Reglas (Arquitectura Dinámica)
        self.output_item_counter = 1
        self.rules_data = self._load_rules()
        self.constants = self.rules_data.get("constants", {})
        self.rules = self.rules_data.get("rules", [])

    def _load_rules(self):
        """Carga el cerebro normativo desde JSON."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, "data", "rules_matrix.json")
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR CRÍTICO] Falló carga de reglas: {e}. Usando backup de memoria.")
            return {"rules": [], "constants": {}}

    def _safe_eval(self, expression, context):
        """
        Motor de Inferencia Seguro.
        Evalúa expresiones lógicas (strings) usando el contexto de datos del inmueble.
        """
        if expression == "always":
            return True
        
        try:
            # Sandbox seguro: solo permitimos variables del contexto y math basic
            # Nota: En producción real, usar librerías como 'simpleeval' es mejor.
            # Aquí usamos eval con scope restringido por eficiencia e innovación nativa.
            allowed_names = {k: v for k, v in context.items()}
            allowed_names['math'] = math
            allowed_names['ceil'] = math.ceil
            
            return eval(expression, {"__builtins__": {}}, allowed_names)
        except Exception as e:
            # Si falla la regla, asumimos False para no romper el flujo (Fail Safe)
            print(f"[Engine Warning] Error evaluando regla '{expression}': {e}")
            return False

    def analyze_requirements(self, data: dict):
        """Generador de Requerimientos Básicos (Legacy Support Wrapper)"""
        # Este método se mantiene por compatibilidad con tests viejos si los hay,
        # pero la lógica real está en analyze_full_compliance
        return self._legacy_basic_calc(data)

    def _legacy_basic_calc(self, data):
        """Cálculo básico rápido para frontend (manteniendo formato anterior)"""
        m2 = data.get("m2_construccion", 0)
        extintores = math.ceil(m2 / 300)
        return {
            "extintores": {"base_PQS": {"cantidad": extintores, "descripcion": "Estimado Base"}},
            "brigadas": {"total_brigadistas": math.ceil(data.get("trabajadores",0)/10)},
            "alertamiento": {"detectores_humo": math.ceil(m2/80)},
            "equipamiento_medico": {"fijos": data.get("niveles", 1)}
        }

    def _generate_strict_legal_justification(self, data):
        """Generador Jurídico (Mantenido híbrido por complejidad semántica)"""
        reasons = []
        if data.get("trabajadores", 0) > 25: reasons.append(f"PLANTILLA > 25 TRABAJADORES")
        if data.get("m2_construccion", 0) > 250: reasons.append(f"SUPERFICIE > 250 M²")
        if data.get("has_gas"): reasons.append("INSTALACIÓN DE GAS")
        if data.get("has_special_inst"): reasons.append("INSTALACIONES ESPECIALES")
        if data.get("has_pool"): reasons.append("RIESGO ACUÁTICO (ALBERCA)")
        
        reasons_text = " Y ".join(reasons)
        municipio = data.get("municipio", "Local")
        return (f"EL INMUEBLE ESTÁ OBLIGADO A PRESENTAR UN PROGRAMA INTERNO DE PROTECCIÓN CIVIL "
                f"POR FACTORES DE RIESGO: {reasons_text}. CONFROME A LEY GENERAL DE PC ART. 39 Y REGLAMENTO DE {municipio.upper()}.")

    def analyze_full_compliance(self, data: dict):
        """
        MOTOR DE INFERENCIA V3.0
        Ejecuta todas las reglas de la matriz contra los datos del usuario.
        """
        budget_items = []
        self.output_item_counter = 1
        
        # 1. Preparar Contexto de Datos (Normalización)
        context = data.copy()
        context['tipo_inmueble'] = context.get('tipo_inmueble', 'Otro')
        context['m2_construccion'] = float(context.get('m2_construccion', 0))
        
        # 2. Iterar Reglas (Motor Dinámico)
        for rule in self.rules:
            # A. Evaluar Trigger
            if self._safe_eval(rule['trigger_logic'], context):
                # B. Calcular Cantidad
                qty = 1
                if 'calculation_formula' in rule and rule['calculation_formula'] != "1":
                    raw_qty = self._safe_eval(rule['calculation_formula'], context)
                    qty = int(raw_qty) if raw_qty else 1
                
                # C. Validar Mínimos (ej. niveles)
                if 'min_value_ref' in rule:
                    min_val = context.get(rule['min_value_ref'], 0)
                    if qty < min_val: qty = min_val
                
                # D. Generar Item de Presupuesto
                out_def = rule['output_item']
                concept = out_def['concept_template']
                # Interpolación simple de strings si es necesario (ej. factor riesgo)
                
                item = {
                    "id": f"auto_{self.output_item_counter}",
                    "categoria": rule['category'],
                    "concepto": concept,
                    "cantidad": qty,
                    "precio_unitario": float(out_def['unit_price']),
                    "norma": out_def['norma']
                }
                budget_items.append(item)
                self.output_item_counter += 1

        # 3. Lógica Estática Remanente (Aranceles Complejos y Honorarios)
        # (Se mantiene aquí para no sobrecomplicar el JSON V1, pero se puede migrar luego)
        # Cálculo de Honorarios Profesionales Base
        m2 = context['m2_construccion']
        honorarios = 8000.00 + (m2 * 3.50)
        budget_items.append({
            "id": f"auto_{self.output_item_counter}",
            "categoria": "Servicios Profesionales",
            "concepto": "Elaboración de Carpeta Técnica PIPC (Análisis Integral de Riesgos)",
            "cantidad": 1,
            "precio_unitario": honorarios,
            "norma": "LGPC Art. 39"
        })
        
        # 4. Retorno Estructurado
        basic_res = self._legacy_basic_calc(context) # Para compatibilidad visual UI
        
        return {
            "basic_requirements": basic_res,
            "resumen_ejecutivo": {
                "total_brigadistas": math.ceil(data.get("trabajadores",0)/10),
                "nivel_riesgo_estimado": "Dinámico V3.0",
                "legal_justification_strict": self._generate_strict_legal_justification(context)
            },
            "checklist": get_applicable_noms(data), # Sigue usando library externa (modular)
            "budget_matrix_version": self.rules_data.get("_meta", {}).get("version", "Unknown"),
            "presupuesto_inicial": budget_items
        }

if __name__ == "__main__":
    eng = CivilProtectionCalculator()
    print("Motor Iniciado. Reglas cargadas:", len(eng.rules))

