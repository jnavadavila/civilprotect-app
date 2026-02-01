import { useState } from 'react';

export const useRiskValidation = (formData, setFormData) => {
    const [modalConfig, setModalConfig] = useState(null); // { show: boolean, title, message, onConfirm, onCancel }

    const handleRiskChange = (field, value) => {
        // Lógica de Controversia
        if (value === true) {
            // Caso 1: Gas en Oficinas/Call Center
            if (field === 'hasGas') {
                const suspicious = ['Oficina', 'Call center', 'Escuela', 'Banco', 'Plaza Comercial'];
                if (suspicious.some((t) => formData.tipoInmueble.includes(t))) {
                    setModalConfig({
                        show: true,
                        title: 'Confirmación de Riesgo Atípico',
                        message: `Ha seleccionado "Instalación de Gas" para un inmueble tipo "${formData.tipoInmueble}". Esto es inusual para este giro. ¿Confirma que realmente existe esta instalación?`,
                        onConfirm: () => {
                            setFormData((prev) => ({ ...prev, [field]: true }));
                            setModalConfig(null);
                        },
                        onCancel: () => setModalConfig(null)
                    });
                    return;
                }
            }

            // Caso 2: Cuarto de Máquinas y la Confusión con SITE
            if (field === 'hasMachineRoom') {
                const suspicious = ['Restaurante', 'Cafetería', 'Tienda', 'Call center', 'Oficina'];
                if (suspicious.some((t) => formData.tipoInmueble.includes(t))) {
                    setModalConfig({
                        show: true,
                        title: 'Distinción Operativa: Site vs. Máquinas',
                        message: `Ha seleccionado "Cuarto de Máquinas".\n\nIMPORTANTE: Si se refiere al SITE de Servidores/CCTV, NO marque esta casilla (el sistema lo infiere automáticamente). Marque esta opción SOLO si existe un cuarto con Equipos Mayores (Bombas, Chillers, Planta de Emergencia > 300KW). ¿Confirma que es un Cuarto de Máquinas Industrial?`,
                        onConfirm: () => {
                            setFormData((prev) => ({ ...prev, [field]: true }));
                            setModalConfig(null);
                        },
                        onCancel: () => setModalConfig(null)
                    });
                    return;
                }
            }

            // Caso 3: Albercas en Giros Inusuales o Espacios Pequeños
            if (field === 'hasPool') {
                const suspicious = ['Oficina', 'Call center', 'Nave Industrial', 'Bodega', 'Restaurante', 'Escuela'];
                const m2 = parseFloat(formData.m2Construccion) || 0;

                if (suspicious.some((t) => formData.tipoInmueble.includes(t)) || (m2 > 0 && m2 < 1000)) {
                    setModalConfig({
                        show: true,
                        title: 'Verificación de Factibilidad de Alberca',
                        message: `Ha marcado "Alberca" en un "${formData.tipoInmueble}" de ${m2}m². \n\n1. ¿El espacio permite físicamente una alberca normativa?\n2. ¿Es una alberca de uso público/recreativo?\n\nMarque SÍ solo si cumple ambas. (Fuentes decorativas NO cuentan como riesgo acuático mayor).`,
                        onConfirm: () => {
                            setFormData((prev) => ({ ...prev, [field]: true }));
                            setModalConfig(null);
                        },
                        onCancel: () => setModalConfig(null)
                    });
                    return;
                }
            }

            // Caso 4: Subestación en Giros de Bajo/Medio Consumo
            if (field === 'hasSubstation') {
                const suspicious = ['Restaurante', 'Oficina', 'Escuela', 'Tienda', 'Casa'];
                if (
                    suspicious.some((t) => formData.tipoInmueble.includes(t)) &&
                    parseFloat(formData.m2Construccion || 0) < 2000
                ) {
                    setModalConfig({
                        show: true,
                        title: 'Confirmación de Alta Tensión',
                        message: `Ha marcado "Subestación Eléctrica". Esto implica recibir Alta Tensión (23kV+) y tener equipo propio de paso. Los comercios u oficinas < 2000m² usualmente solo tienen acometida o Transformador regular. ¿Confirma la Subestación?`,
                        onConfirm: () => {
                            setFormData((prev) => ({ ...prev, [field]: true }));
                            setModalConfig(null);
                        },
                        onCancel: () => setModalConfig(null)
                    });
                    return;
                }
            }

            // Caso 5: Instalaciones Especiales en Giros Administrativos o Pequeños
            if (field === 'hasSpecialInst') {
                const suspicious = ['Oficina', 'Escuela', 'Banco', 'Call center', 'Restaurante', 'Tienda'];
                const m2 = parseFloat(formData.m2Construccion) || 0;

                if (suspicious.some((t) => formData.tipoInmueble.includes(t)) || m2 < 500) {
                    setModalConfig({
                        show: true,
                        title: 'Confirmación de Riesgo Químico Industrial',
                        message: `Ha marcado "Instalaciones Especiales". \n\nNOTA: Las cámaras de refrigeración estándar de un restaurante o tienda NO califican como "Alto Riesgo Químico" (NOM-028/NOM-005). Esto se reserva para Amoníaco Industrial o Tanques Criogénicos. ¿Confirma que REALMENTE posee instalaciones industriales de este tipo?`,
                        onConfirm: () => {
                            setFormData((prev) => ({ ...prev, [field]: true }));
                            setModalConfig(null);
                        },
                        onCancel: () => setModalConfig(null)
                    });
                    return;
                }
            }
        }

        // Si no hay controversia, aplicar directo
        setFormData((prev) => ({ ...prev, [field]: value }));
    };

    return {
        modalConfig,
        setModalConfig,
        handleRiskChange
    };
};
