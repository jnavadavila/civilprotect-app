# AUDITORÍA TÉCNICA Y PROSPECTIVA - LY GIRRD PC AI V3.0
# Fecha: 24/Enero/2026
# Auditoría: Deepmind/Antigravity

## 1. VULNERABILIDADES Y MALAS PRÁCTICAS DETECTADAS

### A. Vulnerabilidades de Seguridad y "Hardcoding"
1.  **Credenciales en Frontend:**
    *   *Hallazgo:* En `LandingPage.jsx`, las credenciales "admin/admin123" están escritas directamente en el código del cliente (`if (credentials.user === 'admin'...)`).
    *   *Riesgo:* Crítico. Cualquier usuario puede ver esto inspeccionando el código fuente en el navegador.
    *   *Mala Práctica:* Autenticación "Mock" en producción.

2.  **Inyección de Dependencias Manual:**
    *   *Hallazgo:* En `noms_library.py`, inyectamos "NOM-245-SSA1" manualmente con un `if "NOM..." not in SPECIFIC_NOMS`.
    *   *Riesgo:* Si la base de datos JSON crece o cambia de estructura, este "parche" en código Python quedará obsoleto o causará conflictos de duplicidad.
    *   *Mala Práctica:* Lógica de datos dispersa (parte en JSON, parte en Python).

3.  **Manejo de CORS Permisivo:**
    *   *Hallazgo:* `main.py` permite `origins = ["*"]`.
    *   *Riesgo:* Permite que cualquier sitio web haga peticiones a tu API backend. En un entorno real, esto facilita ataques CSRF o uso no autorizado de tu API.

### B. Deficiencias Arquitectónicas
4.  **Monolito Híbrido:**
    *   La lógica de negocio (`calculator_engine`) y la lógica de presentación (`report_generator`) están muy acopladas. Si cambias una regla de cálculo, podrías romper impensadamente el PDF si no sincronizas las claves del diccionario.

---

## 2. CONFLICTOS CON IA Y PROBLEMAS A FUTURO

### A. Alucinación Normativa vs. Determinismo
*   **Conflicto:** El sistema usa reglas deterministas (`if has_gas: append NOM-004`) mezcladas con "IA Legislativa" que escanea el DOF.
*   **Problema Futuro:** Si la IA detecta que la norma cambió (ej. de NOM-004 a NOM-005 nueva), el código "duro" (`calculator_engine.py`) seguirá cobrando la norma vieja hasta que un programador lo actualice manualmente. La IA no tiene permiso de reescribir el código Python.

### B. Escalabilidad de la Base de Datos Legal
*   **Deficiencia:** Estamos usando un archivo estático `legal_db.json` cargado en memoria.
*   **Problema Futuro:** Con 32 estados y cientos de municipios, este archivo crecerá masivamente. Cargar 50MB de JSON en memoria cada vez que inicia el servidor es ineficiente y bloqueará la API.

### C. Mantenibilidad del Reporte PDF
*   **Deficiencia:** El PDF se dibuja "pixel por pixel" (`pdf.set_xy(34, 15)`).
*   **Problema Futuro:** Cualquier cambio mínimo en el logo o fuente desalinea todo el documento. Mantener esto requerirá horas de "prueba y error" visual.

---

## 3. TASK DE INTERVENCIÓN (PROPUESTA "PHASE 2 - HARDENING")

**Tarea Prioritaria: Desacolplamiento y Seguridad**

1.  **Refactorización de Autenticación (JWT):**
    *   Eliminar credenciales del frontend. Implementar endpoint `/login` real en backend que devuelva un Token JWT.

2.  **Migración a SQLite/Postgres:**
    *   Mover `legal_db.json` y las inyecciones manuales a una base de datos ligera (SQLite) consultable por SQL. Esto elimina la carga en memoria y centraliza la verdad normativa.

3.  **Motor de Reglas Dinámico (No Hardcode):**
    *   En lugar de `if has_gas: add item`, crear una tabla "Reglas de Presupuesto" en la DB:
    *   `{ trigger: "has_gas", item: "Dictamen GLP", cost: 4500 }`.
    *   El motor solo iteraría la DB. Esto permite agregar nuevas reglas (ej. "Paneles Solares") sin tocar una línea de código Python.

4.  **Sistema de Plantillas PDF (HTML to PDF):**
    *   Reemplazar `fpdf` (pixel perfect) por `jinja2 + weasyprint`. Generar el reporte en HTML (fácil de editar) y convertirlo a PDF automáticamente.

**¿Autorizas proceder con el Task 1 (Autenticación Real) o prefieres el Task 3 (Motor Dinámico) para asegurar la escalabilidad del análisis?**
