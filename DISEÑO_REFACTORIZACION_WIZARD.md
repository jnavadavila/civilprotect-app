# Diseño de Refactorización: CivilProtectForm -> FormWizard

## 1. Objetivo
Refactorizar el componente monolítico `CivilProtectForm.jsx` (+1000 líneas) en una arquitectura modular basada en pasos (Wizard) y hooks personalizados, mejorando la mantenibilidad y la experiencia de usuario.

## 2. Estructura de Archivos Propuesta

```
frontend/src/
├── components/
│   ├── FormWizard/
│   │   ├── FormWizard.jsx          # Contenedor principal y navegación
│   │   ├── LocationStep.jsx        # Paso 1: Ubicación y Geografía
│   │   ├── PropertyInfoStep.jsx    # Paso 2: Datos del Inmueble
│   │   ├── InfrastructureStep.jsx  # Paso 3: Infraestructura y Riesgos
│   │   ├── ResultsView.jsx         # Vista de resultados (Tabs, Reportes)
│   │   └── steps/
│   │       └── IndicatorButton.jsx # Componente UI reutilizable
│   └── ...
├── hooks/
│   ├── useFormData.js              # Gestión de estado global del formulario y persistencia
│   ├── useCatalogData.js           # Carga de catálogos (Estados/Municipios)
│   ├── useRiskValidation.js        # Lógica de validación de riesgos (Modales)
│   └── useAnalysisSubmit.js        # Lógica de envío al backend
```

## 3. Especificación de Componentes

### 3.1. `FormWizard.jsx` (Container)
*   **Responsabilidad:** Orquestar el estado global, manejar la navegación entre pasos y renderizar el paso activo.
*   **Estado:** `currentStep`, `formData` (vía hook), `result` (vía hook).
*   **Props:**
    *   `userRole`: string
    *   `initialData`: object (opcional, para historial)

### 3.2. `LocationStep.jsx`
*   **Responsabilidad:** Selección de Estado y Municipio, visualización de indicadores geográficos (Pueblo Mágico, Zona Industrial, etc.).
*   **Props:**
    *   `formData`: object
    *   `setFormData`: function
    *   `catalogData`: object (vía hook `useCatalogData`)
    *   `onNext`: function

### 3.3. `PropertyInfoStep.jsx`
*   **Responsabilidad:** Captura de datos numéricos y tipo de inmueble.
*   **Props:**
    *   `formData`: object
    *   `handleInputChange`: function
    *   `validationErrors`: array
    *   `onNext`: function
    *   `onBack`: function

### 3.4. `InfrastructureStep.jsx`
*   **Responsabilidad:** Checkboxes de infraestructura con validación de riesgos (modales).
*   **Props:**
    *   `formData`: object
    *   `handleRiskChange`: function (vía hook `useRiskValidation`)
    *   `onSubmit`: function
    *   `onBack`: function
    *   `loading`: boolean

### 3.5. `ResultsView.jsx`
*   **Responsabilidad:** Mostrar el resultado del análisis, gestionar pestañas (Resumen, Checklist, Costos) y firma.
*   **Props:**
    *   `result`: object
    *   `formData`: object
    *   `onSave`: function
    *   `onDownload`: function
    *   `onReset`: function

## 4. Diseño de Custom Hooks

### 4.1. `useFormData.js`
*   **Lógica:**
    *   Estado inicial (`useState`).
    *   Efecto de carga desde `localStorage` o `initialData`.
    *   Efecto de guardado en `localStorage`.
    *   Función `updateField(name, value)`.

### 4.2. `useRiskValidation.js`
*   **Lógica:**
    *   Contiene la lógica de `handleRiskChange`.
    *   Maneja el estado del Modal de Confirmación (`modalConfig`).
    *   Retorna: `{ handleRiskChange, RiskConfirmationModal }`.

### 4.3. `useAnalysisSubmit.js`
*   **Lógica:**
    *   Maneja `loading`, `error`, `result`.
    *   Contiene la lógica de `handleSubmit` (llamada a Axios).
    *   Contiene la lógica de `validateInputs` (Validaciones de Perito).
    *   Retorna: `{ submitAnalysis, result, loading, validationErrors }`.

## 5. Estrategia de Migración (Bit a Bit)

1.  **Crear Hooks:** Extraer la lógica del componente actual a los nuevos hooks sin borrar el componente original.
2.  **Crear Sub-componentes:** Crear los archivos en `components/FormWizard/` vacíos o con estructura básica.
3.  **Migrar Lógica:** Mover el JSX por secciones desde `CivilProtectForm` a los sub-componentes.
4.  **Integrar:** Reemplazar el contenido de `CivilProtectForm.jsx` con el `FormWizard` que orquesta los pasos.
5.  **Verificar:** Asegurar que la persistencia y validaciones sigan funcionando igual.

## 6. Interfaces (Props Definitions)

### LocationStep Interface
```javascript
LocationStep.propTypes = {
  formData: PropTypes.shape({
    estado: PropTypes.string,
    municipio: PropTypes.string
  }).isRequired,
  onChange: PropTypes.func.isRequired,
  catalog: PropTypes.object.isRequired
};
```

### InfrastructureStep Interface
```javascript
InfrastructureStep.propTypes = {
  formData: PropTypes.object.isRequired,
  onRiskChange: PropTypes.func.isRequired, // Wrapper que incluye la lógica de modal
  onSubmit: PropTypes.func.isRequired
};
```
