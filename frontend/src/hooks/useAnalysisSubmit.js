import { useState } from 'react';
import axios from '../utils/axios';

export const useAnalysisSubmit = (setResult, setValidationErrors, setModalConfig) => {
    const [loading, setLoading] = useState(false);

    const submitAnalysis = async (
        formData,
        selectedMuni,
        selectedState,
        validateInputs,
        bypassConfirmation = false
    ) => {
        // Ejecutar Validaciones de Perito antes de enviar (si validateInputs se pasa)
        if (validateInputs) {
            const isValid = validateInputs(formData);
            if (!isValid) {
                // Scroll al top para ver errores
                window.scrollTo(0, 0);
                return;
            }
        }

        // [NUEVO] Verificación de Valores Extremos ("Sanity Check" Pericial)
        if (!bypassConfirmation) {
            const m2 = parseFloat(formData.m2Construccion) || 0;
            const aforo = parseInt(formData.aforoMax) || 0;
            const trabajadores = parseInt(formData.numTrabajadores) || 0;

            // 1. Umbrales de "Incredulidad" (Dimensiones)
            const isExtremeM2 = m2 > 15000;
            const isExtremeAforo = aforo > 5000;

            // 2. Umbrales de Hacinamiento / Incoherencia (Imagen del Usuario)
            const totalPersonas = aforo + trabajadores;
            const densidadFisica = m2 > 0 ? totalPersonas / m2 : 0;

            // Si hay más trabajadores que el aforo total permitido
            const incongruenciaPoblacional =
                trabajadores > aforo &&
                !['Nave Industrial', 'Bodega', 'Oficina Corporativa'].includes(formData.tipoInmueble);

            if (isExtremeM2 || isExtremeAforo || densidadFisica > 2 || incongruenciaPoblacional) {
                let riskMsg = '';
                if (isExtremeM2) riskMsg += `- Superficie Extraordinaria: ${m2.toLocaleString()} m²\n`;
                if (isExtremeAforo) riskMsg += `- Aforo Masivo: ${aforo.toLocaleString()} personas\n`;
                if (densidadFisica > 2)
                    riskMsg += `- HACINAMIENTO CRÍTICO: Detectamos ${densidadFisica.toFixed(1)} personas por m². Esto es físicamente improbable para operaciones seguras (Estándar: ~1m² por persona). \n`;
                if (incongruenciaPoblacional)
                    riskMsg += `- PLANTILLA EXCESIVA: Reporta ${trabajadores} trabajadores, superando el aforo de clientes (${aforo}).\n`;

                if (setModalConfig) {
                    setModalConfig({
                        show: true,
                        title: 'Alerta de Coherencia Dimensional',
                        message: `El sistema ha detectado valores potencialmente incoherentes:\n\n${riskMsg}\n¿Son correctos los datos o desea corregirlos?`,
                        onConfirm: () => {
                            setModalConfig(null);
                            // Llamada recursiva con bypass
                            submitAnalysis(formData, selectedMuni, selectedState, null, true);
                        },
                        onCancel: () => setModalConfig(null)
                    });
                }
                return;
            }
        }

        setLoading(true);
        try {
            // Preparar payload para el backend
            const payload = {
                tipo_inmueble: formData.tipoInmueble,
                m2_construccion: parseFloat(formData.m2Construccion) || 0,
                niveles: parseInt(formData.nivelesTotales) || 1,
                aforo: parseInt(formData.aforoMax) || 0,
                aforo_autorizado: parseInt(formData.aforoAutorizado) || 0,
                trabajadores: parseInt(formData.numTrabajadores) || 0,
                municipio: selectedMuni,
                estado: selectedState,
                // Infraestructura de Riesgo
                has_gas: formData.hasGas,
                has_transformer: formData.hasTransformer,
                has_machine_room: formData.hasMachineRoom,
                has_substation: formData.hasSubstation,
                has_pool: formData.hasPool,
                has_special_inst: formData.hasSpecialInst
            };

            const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
            const response = await axios.post(`${apiUrl}/analyze`, payload);
            setResult(response.data);
            if (setValidationErrors) setValidationErrors([]); // Limpiar errores si tuvo éxito
        } catch (error) {
            console.error('Error analyzing:', error);
            alert('Error de conexión con el servidor de análisis.');
        } finally {
            setLoading(false);
        }
    };

    return {
        loading,
        submitAnalysis
    };
};
