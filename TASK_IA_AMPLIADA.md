
# TAREA DE INTERVENCIÓN INMEDIATA: EXPANSIÓN DE IA EN ESTRUCTURA CAPITULAR (v4.0)

## 1. Hallazgo de Auditoría (Lo No Atendido)
Se detectó una **omisión crítica** en la interpretación de la instrucción del *Step 2322*.
*   **Instrucción Original:** "PRODUCTO DE ESTO CON LA AYUDA DE IA REALIZA EL CUMPLIMIENTO REFERENCIADO POR CADA ESTADO Y CADA MUNICIPIO AMPLIADO".
*   **Estado Actual:** Se cambió el título a "Estructura Mínima...", pero el **contenido** de la Guía Capitular (Sección 3 del PDF) sigue siendo una lista estática (`guia_dinamica` en `noms_library.py`) basada en reglas fijas (`if estado == "CDMX"...`).
*   **Faltante:** No hay un motor de IA que "amplíe" o "personalice" dinámicamente esta estructura para municipios específicos (ej. reglamentos particulares de Tulum vs Cancún) mediante inferencia o consulta.

## 2. Objetivo de la Intervención
Transformar la generación de la "Estructura Mínima Capitular" de un modelo estático a un modelo **Híbrido (Base Legal + Enriquecimiento IA)**.

Si el sistema detecta un municipio específico, la IA debe insertar los requisitos particulares de ese municipio en la estructura capitular, referenciándolos correctamente.

## 3. Pasos de Ejecución

### PASO 1: Actualizar `ai_service.py`
Crear un nuevo método `enrich_chapter_structure(estado, municipio, structure_base)`:
*   **Input:** La estructura base JSON (lo que ya tenemos).
*   **Proceso:** Prompt a OpenAI: "Eres experto legal. Para el municipio {municipio} de {estado}, analiza esta estructura estándar. Si existe un reglamento municipal con requisitos adicionales (ej. Visto Bueno de Ecología, Dictamen de Aseo Público), AGREGA esos ítems a la lista con su fundamento legal probable o real. NO ELIMINES lo base."
*   **Output:** Estructura JSON enriquecida.

### PASO 2: Conectar `noms_library.py` con `ai_service.py`
*   Modificar `get_pipc_guide` para que acepte una instancia (opcional) del servicio de IA o reciba los datos enriquecidos.
*   Si no hay conexión a OpenAI, mantener el *fallback* estático actual (seguridad).

### PASO 3: Actualizar `main.py`
*   En el endpoint `/analyze`, asegurarse de invocar esta nueva capacidad de enriquecimiento antes de generar el PDF para que la sección 3 ("Guía de Integración") salga "Ampliada".

## 4. Criterio de Éxito
El PDF generado para un municipio complejo (ej. "Solidaridad / Playa del Carmen") debe mostrar ítems específicos en la Guía de Integración (como "Anuencia de Medio Ambiente") que NO estaban en el JSON estático, generados por la "consulta con IA".
