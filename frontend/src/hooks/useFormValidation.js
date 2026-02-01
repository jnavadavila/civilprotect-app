import { useState } from 'react';

export const useFormValidation = () => {
    const [validationErrors, setValidationErrors] = useState([]);

    const validateInputs = (formData) => {
        const errors = [];
        const m2 = parseFloat(formData.m2Construccion) || 0;
        const aforo = parseInt(formData.aforoMax) || 0;
        const trabajadores = parseInt(formData.numTrabajadores) || 0;

        if (m2 <= 0) {
            errors.push('La superficie construida debe ser mayor a 0.');
        } else {
            // 1. CHEQUEO DE DENSIDAD POBLACIONAL (SANITY CHECK)
            const densidad = aforo / m2;
            if (densidad > 4) {
                errors.push(
                    `CRITICAL: Densidad poblacional imposible (${densidad.toFixed(1)} personas/m²). El máximo teórico es 4 pers/m².`
                );
            }

            // 2. CHEQUEO DE ESPACIO DE TRABAJO
            if (trabajadores > 0) {
                const m2PorTrabajador = m2 / trabajadores;
                if (m2PorTrabajador < 1.5) {
                    errors.push(
                        `ALERTA: Hacinamiento laboral detectado (${m2PorTrabajador.toFixed(1)} m²/trabajador). Mínimo recomendado 2 m².`
                    );
                }
            }

            // 3. CHEQUEO DE NIVELES (LÍMITE FÍSICO)
            const niveles = parseInt(formData.nivelesTotales) || 0;
            if (niveles > 50) {
                errors.push(`ERROR CRÍTICO: El número de niveles (${niveles}) excede el límite permitido de 50.`);
            }

            // [RESTAURADO] 4. CHEQUEO GEOMÉTRICO (Torre de Fideos)
            // Validar que cada nivel tenga una superficie lógica mínima (30m²)
            if (niveles > 0) {
                const m2PorNivel = m2 / niveles;
                if (m2PorNivel < 30) {
                    errors.push(
                        `INCOHERENCIA GEOMÉTRICA: Un edificio de ${niveles} niveles con ${m2}m² implica pisos de ${m2PorNivel.toFixed(1)}m². Esto es inviable (Mínimo 30m²/nivel estructural).`
                    );
                }
            }

            // [RESTAURADO] 5. CHEQUEO DE ALBERCA (Espacio Físico)
            if (formData.hasPool && m2 < 100) {
                errors.push(
                    `ERROR FÍSICO: No se puede tener una Alberca Normativa en un inmueble de ${m2}m². (Mínimo requerido para vaso + andadores + cuarto máquinas: 100m²).`
                );
            }

            // [RESTAURADO] 6. CHEQUEO HOSPITALARIO (Soporte de Vida)
            if (formData.tipoInmueble === 'Hospital' && !formData.hasMachineRoom && !formData.hasSubstation) {
                errors.push(
                    `NORMATIVIDAD SALUD: Un HOSPITAL está obligado por ley a contar con Planta de Emergencia (Cuarto de Máquinas) o Subestación para soporte de vida. Por favor marque la infraestructura correspondiente.`
                );
            }
        }

        setValidationErrors(errors);
        return errors.length === 0;
    };

    return {
        validationErrors,
        setValidationErrors,
        validateInputs
    };
};
