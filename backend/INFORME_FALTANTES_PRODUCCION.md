# INFORME DE FALTANTES DE CUMPLIMIENTO Y HOJA DE RUTA DE PRODUCCIÓN
# Fecha: 23 de Enero de 2026
# Sistema: CivilProtect AI (Deepmind Upgrade)

## 1. DIAGNÓSTICO DE COMPONENTES DE ALTO RIESGO
El sistema ha detectado brechas en la lógica de seguridad para infraestructuras mayores a 2,000 m².

### HALLAZGOS CRÍTICOS (FALTANTES)
1.  **Omisión de Sistemas Fijos (Hidrantes):**
    *   La versión anterior solo calculaba extintores. Para naves industriales (>2,000m²), esto viola la NOM-002-STPS (Anexo A) y estándares NFPA.
    *   *Riesgo:* Incapacidad de control de fuego en fase de desarrollo.

2.  **Omisión de Reserva de Agua (Cisterna PCI):**
    *   No existía advertencia sobre la necesidad de 20-40m³ de agua exclusiva.
    *   *Riesgo:* Inviabilidad de operar cualquier sistema de bombeo.

3.  **Cálculo de Evacuación Estático:**
    *   Falta integrar el cálculo de ancho de salidas (Factor 0.6cm/persona) para validar si las puertas existentes soportan el aforo.

---

## 2. ACCIONES REALIZADAS (CORRECCIONES EN CÓDIGO)
Se han implementado las siguientes mejoras en `calculator_engine.py`:

*   [x] **Trigger de Hidrantes:** Si `m2 >= 2000` o Tipo = `Industrial`, se agrega automáticamente la partida "Proyecto Ejecutivo PCI (NOM-002/NFPA)".
*   [x] **Advertencia de Cisterna:** Se agrega el item "Adecuación de Cisterna/Cuarto de Bombas" con reserva estimada de 45m³ (Cálculo rápido: 2 mangueras x 100GPM x 60min).
*   [x] **Arancel de Ingeniería:** Se cotiza el proyecto ejecutivo, no solo la "firma", reconociendo que esto requiere especialidad.

---

## 3. LISTA DE ACCIONES PARA PASE A PRODUCCIÓN (ACTION LIST)

### FASE A: VALIDACIÓN DE DATOS (Inmediato)
1.  [ ] **Prueba de Estrés (Nave Industrial):**
    *   Ejecutar simulador con: `m2=5000`, `tipo="Nave Industrial"`.
    *   *Resultado Esperado:* Que aparezcan las partidas de "Ingeniería PCI ($50k+)" y "Cisterna".
2.  [ ] **Validación de Textos Legales:**
    *   Generar PDF para "Estado de México" y verificar que cite el "Libro Sexto del Código Administrativo".

### FASE B: DESPLIEGUE OPERATIVO
3.  [ ] **Reiniciar Servicio Backend:**
    *   `CTRL+C` en terminal actual.
    *   Ejecutar `python main.py` para cargar los nuevos módulos (Aranceles + Hidrantes).
4.  [ ] **Actualizar Frontend (Opcional):**
    *   Agregar campo "Capacidad de Cisterna Actual (m3)" para que el sistema valide si cumple o no (actualmente solo sugiere, no valida).

### FASE C: FUTURO (ROADMAP DEEPMIND)
5.  **Cálculo Hidráulico Real:** Integrar fórmula de Hazen-Williams para sugerir diámetro de tubería (ej. "Requiere tubería de 4 pulgadas").
6.  **Simulación de Evacuación:** Usar `pathfinding` en los planos (si se subieran) para calcular tiempos de salida.

---
**ESTADO DEL SISTEMA:** LISTO PARA PRUEBAS DE ACEPTACIÓN (UAT) CON MEJORAS DE HIDRANTES E INTEGRIDAD DE DATOS.
