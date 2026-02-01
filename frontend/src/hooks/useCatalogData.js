import { useState, useEffect } from 'react';
import axios from '../utils/axios';

export const useCatalogData = () => {
    const [catalogData, setCatalogData] = useState({ estados: [] });
    const [loadingCatalog, setLoadingCatalog] = useState(true);
    const [muniData, setMuniData] = useState(null);

    // Cargar Catálogos al montar
    useEffect(() => {
        const fetchCatalog = async () => {
            try {
                const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
                const res = await axios.get(`${apiUrl}/catalog/municipios`);
                setCatalogData(res.data);
            } catch (err) {
                console.error('Error cargando catálogos', err);
            } finally {
                setLoadingCatalog(false);
            }
        };
        fetchCatalog();
    }, []);

    const getMuniMetadata = (selectedState, selectedMuni) => {
        if (!selectedState || !selectedMuni) return null;

        const estadoObj = catalogData.estados.find((e) => e.nombre === selectedState);
        if (estadoObj) {
            const muniObj = estadoObj.municipios.find((m) => m.nombre === selectedMuni);
            if (muniObj) {
                return {
                    hasAirport: muniObj.metadata.has_aeropuerto,
                    isTuristico: muniObj.metadata.is_polo_turistico,
                    isPuebloMagico: muniObj.metadata.is_pueblo_magico,
                    isIndustrial: muniObj.metadata.is_zona_industrial,
                    isFrontera: muniObj.metadata.is_frontera,
                    isPuerto: muniObj.metadata.is_puerto,
                    estado: selectedState
                };
            }
        }
        return null;
    };

    return { catalogData, loadingCatalog, getMuniMetadata };
};
