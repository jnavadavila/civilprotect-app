# ANÁLISIS DE VULNERABILIDAD Y RIESGOS (METODOLOGÍA)

## 1. INTRODUCCIÓN
El sistema CivilProtect AI utiliza una metodología híbrida para la determinación del nivel de riesgo, basándose en los estándares nacionales (CENAPRED) e internacionales (Método Mosler).

## 2. MÉTODO DE EVALUACIÓN (MOSLER SIMPLIFICADO)
Para determinar si un inmueble es de **RIESGO ALTO, MEDIO o BAJO**, el sistema analiza 4 vectores:

### A. Vector de Agresión (F)
*   **Carga de Fuego:** Cantidad de materiales combustibles.
    *   *Industrial/Bodega:* Alta (5 pts)
    *   *Oficina/Comercio:* Media (3 pts)
*   **Sustancias Químicas:** Presencia de materiales peligrosos (Gas, Diesel).

### B. Vector de Vulnerabilidad (S)
*   **Aforo:** Densidad de ocupación. (>50 personas = Alta).
*   **Superficie:** Tamaño del inmueble. (>3000m² = Alta).
*   **Infraestructura:** Presencia de Subestaciones o Tanques de alta presión.

### C. Coeficiente de Evolución (P)
Capacidad del fuego o amenaza de crecer rápidamente.

### D. Coeficiente de Protección (E)
Mitigación por sistemas instalados (Extintores, Hidrantes, Detectores).

## 3. CÁLCULO EN EL SISTEMA
El algoritmo actual (`calculator_engine.py`) aplica las siguientes reglas de negocio derivadas:

1.  **Regla de Superficie:** Todo inmueble > 3,000 m² es automáticamente **RIESGO ALTO**.
2.  **Regla de Giro:** Hospitales, Escuelas e Industrias son RIESGO ALTO por defecto (Factor de Vulnerabilidad Social).
3.  **Regla de Infraestructura:** La presencia de "Gas LP" + "Subestación" eleva el nivel de riesgo en 1 grado.

### Resultado del Análisis
El Nivel de Riesgo resultante determina:
*   La obligatoriedad del proyecto de Hidrantes.
*   La frecuencia de los simulacros (2 o 3 al año).
*   La necesidad de Visto Bueno de Seguridad y Operación.


