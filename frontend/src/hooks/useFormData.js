import { useState, useEffect } from 'react';

export const useFormData = (initialData) => {
    // Estado del formulario
    const [selectedState, setSelectedState] = useState('');
    const [selectedMuni, setSelectedMuni] = useState('');
    const [signatureImage, setSignatureImage] = useState(null);
    const [result, setResult] = useState(null);

    // Datos del inmueble
    const [formData, setFormData] = useState({
        tipoInmueble: 'Hotel', // Default
        m2Construccion: '',
        nivelesTotales: '',
        nivelesDeprimidos: '', // Sótanos
        aforoMax: '',
        aforoAutorizado: '',
        numTrabajadores: '',
        // Infraestructura (Booleans)
        hasGas: false,
        hasTransformer: false,
        hasMachineRoom: false,
        hasSubstation: false,
        hasSpecialInst: false,
        hasPool: false
    });

    // EFFECT: Gestión de Datos Iniciales y Persistencia
    useEffect(() => {
        if (initialData) {
            console.log('Cargando datos históricos:', initialData);
            // 1. Mapeo de Campos
            setFormData({
                tipoInmueble: initialData.tipo_inmueble || 'Hotel',
                m2Construccion: initialData.m2_construccion || '',
                nivelesTotales: initialData.niveles || '',
                nivelesDeprimidos: '',
                aforoMax: initialData.aforo || '',
                aforoAutorizado: initialData.aforo_autorizado || '',
                numTrabajadores: initialData.trabajadores || '',
                hasGas: initialData.has_gas || false,
                hasTransformer: initialData.has_transformer || false,
                hasMachineRoom: initialData.has_machine_room || false,
                hasSubstation: initialData.has_substation || false,
                hasSpecialInst: initialData.has_special_inst || false,
                hasPool: initialData.has_pool || false
            });

            // 2. Mapeo de Geografía (Estado/Municipio)
            if (initialData.estado) {
                setSelectedState(initialData.estado);
                if (initialData.municipio) {
                    setSelectedMuni(initialData.municipio);
                }
            }
        } else {
            // [FIX] Si NO hay initialData (es "Nuevo Análisis"), 
            // NO cargamos basura del localStorage automáticamente para evitar confusión.
            // Iniciamos limpio.
            // (Opcional: Si quisiéramos "recuperar borrador", necesitaríamos un botón explícito)
        }
    }, [initialData]);

    // ==================== PERSISTENCIA EN LOCALSTORAGE ====================
    useEffect(() => {
        localStorage.setItem('civilprotect_formData', JSON.stringify(formData));
    }, [formData]);

    useEffect(() => {
        if (result) localStorage.setItem('civilprotect_result', JSON.stringify(result));
    }, [result]);

    useEffect(() => {
        if (selectedState) localStorage.setItem('civilprotect_selectedState', selectedState);
    }, [selectedState]);

    useEffect(() => {
        if (selectedMuni) localStorage.setItem('civilprotect_selectedMuni', selectedMuni);
    }, [selectedMuni]);

    useEffect(() => {
        if (signatureImage) localStorage.setItem('civilprotect_signature', signatureImage);
    }, [signatureImage]);
    // ======================================================================

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value
        }));
    };

    const resetForm = () => {
        setFormData({
            tipoInmueble: 'Hotel',
            m2Construccion: '',
            nivelesTotales: '',
            nivelesDeprimidos: '',
            aforoMax: '',
            aforoAutorizado: '',
            numTrabajadores: '',
            hasGas: false,
            hasTransformer: false,
            hasMachineRoom: false,
            hasSubstation: false,
            hasSpecialInst: false,
            hasPool: false
        });
        setSelectedState('');
        setSelectedMuni('');
        setResult(null);
        setSignatureImage(null);

        // Limpiar localStorage
        localStorage.removeItem('civilprotect_formData');
        localStorage.removeItem('civilprotect_result');
        localStorage.removeItem('civilprotect_selectedState');
        localStorage.removeItem('civilprotect_selectedMuni');
        localStorage.removeItem('civilprotect_signature');
    };

    return {
        formData,
        setFormData,
        selectedState,
        setSelectedState,
        selectedMuni,
        setSelectedMuni,
        signatureImage,
        setSignatureImage,
        result,
        setResult,
        handleInputChange,
        resetForm
    };
};
