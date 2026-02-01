# Plan de Implementación: Refinamiento de UX y Validación Pericial

## Objetivos Críticos
1.  **Sistema de Validación Pericial ("Sanity Checks"):** Implementar lógica matemática en el frontend que impida o alerte sobre datos físicamente imposibles (densidad poblacional extrema) antes de permitir el análisis.
2.  **Corrección de Flujo de Interfaz (UI/UX):** Asegurar la visibilidad de la Pantalla de Login y reubicar o clarificar la aparición de los botones de Gestión Documental (PDF/Guardar).
3.  **Seguridad de Acceso:** Garantizar que el usuario pase por el Landing/Login antes de ver el formulario.

## Cambios Propuestos

### 1. Frontend: Validación de Densidad (CivilProtectForm.jsx)
- **Nueva Función `validateDensity()`:**
  - Calculará la relación `Aforo / Metros Cuadrados`.
  - Si la densidad > 4 personas/m² (estándar de riesgo extremo/hacinamiento), mostrará una **Alerta Bloqueante**.
  - Si la relación `Trabajadores / Metros` es irracional (ej. < 2 m² por trabajador), lanzará advertencia.
- **Feedback Visual:** Los campos numéricos se pondrán rojos si los valores son incoherentes.

### 2. Frontend: Corrección de Login y Navegación (App.js)
- **Forzado de Estado:** Asegurar que `isLoggedIn` inicie siempre en `false` al recargar la página para garantizar que el usuario vea el Landing Page.
- **Indicadores de Estado:** Mejorar la barra superior para mostrar claramente el rol actual.

### 3. Frontend: Visibilidad de Herramientas (CivilProtectForm.jsx)
- **Barra de Acción Permanente:** Aunque los botones de "Generar PDF" requieren un resultado previo para funcionar, se mostrará una barra de herramientas desactivada (disabled) visualmente desde el inicio para que el usuario sepa que esas opciones existen y se habilitarán tras el análisis.

### 4. Backend: Noms Library (Ejecución de Fase B pendiente)
- Se mantiene en cola la carga de las 32 leyes estatales, asegurando que se integre en el siguiente ciclo de escritura.

## Verificación de Éxito
- [ ] Intentar ingresar "630m2" y "69,000 aforo" -> El sistema debe arrojar un error: "Error de Densidad: Imposible alojar 109 personas por m2".
- [ ] Recargar la página -> Debe aparecer el Landing Page con fondo azul animado.
- [ ] Realizar un análisis válido -> Deben habilitarse los botones de "Generar PDF Oficial" y "Guardar".
