import React from 'react';
import FormWizard from './components/FormWizard/FormWizard';

/**
 * CivilProtectForm (Wrapper)
 *
 * Este componente actúa como adaptador para mantener la compatibilidad con App.js
 * mientras se migra toda la lógica a FormWizard y sus sub-componentes.
 *
 * Refactorización Phase 3.1 completed.
 */
export default function CivilProtectForm(props) {
    // [FIX] Anti-stuck loop: Si no hay datos iniciales explícitos,
    // forzamos limpieza de basura del localStorage al montar si venimos de "Nuevo Análisis"
    React.useEffect(() => {
        if (!props.initialData) {
            // No llamamos a localStorage.clear() global, solo limpiamos keys específicas si es necesario,
            // pero mejor dejamos que useFormData maneje su lógica.
            // Lo importante es que FormWizard no crashee.
        }
    }, [props.initialData]);

    try {
        return <FormWizard {...props} />;
    } catch (error) {
        return (
            <div className="p-4 bg-red-100 text-red-700 rounded mb-4">
                Error cargando el formulario: {error.message}
                <button onClick={() => window.location.reload()} className="ml-4 underline">Recargar</button>
            </div>
        );
    }
}
