import React, { createContext, useState, useCallback } from 'react';
import axios from '../utils/axios';

export const AnalysisContext = createContext();

export const AnalysisProvider = ({ children }) => {
    const [history, setHistory] = useState([]);
    const [currentAnalysis, setCurrentAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [historyFetched, setHistoryFetched] = useState(false);

    // Fetch History (con cache simple)
    const fetchHistory = useCallback(
        async (force = false) => {
            if (historyFetched && !force) return;

            setLoading(true);
            try {
                const response = await axios.get('/history');
                setHistory(response.data.history || []);
                setHistoryFetched(true);
            } catch (error) {
                console.error('Error fetching history:', error);
            } finally {
                setLoading(false);
            }
        },
        [historyFetched]
    );

    // Load Analysis (Cargar uno específico para editar/ver)
    const loadAnalysis = useCallback(
        async (id) => {
            setLoading(true);
            try {
                // Primero verificamos si ya está en memoria (historia)
                // Asumimos que el detail endpoint es necesario si history es resumen
                // Si el backend soporta /history/{id}, usamos eso.
                const response = await axios.get(`/history/${id}`);
                const analysisData = response.data; // Asumimos que trae input_data y results

                // Mapper si es necesario (snake -> camel lo hará useFormData)
                setCurrentAnalysis(analysisData);
                return analysisData;
            } catch (error) {
                console.error('Error loading analysis:', error);
                // Fallback: buscar en local history si existe
                const local = history.find((h) => h.id === id);
                if (local) {
                    console.warn('Usando versión local (resumen) debido a error de red');
                    setCurrentAnalysis(local);
                    return local;
                }
                return null;
            } finally {
                setLoading(false);
            }
        },
        [history]
    );

    // Crear/Guardar Analysis (actualizar historial localmente)
    const refreshHistory = useCallback(() => {
        fetchHistory(true);
    }, [fetchHistory]);

    // Delete Analysis
    const deleteAnalysis = useCallback(
        async (id) => {
            try {
                await axios.delete(`/history/${id}`);
                // Actualizar estado local
                setHistory((prev) => prev.filter((item) => item.id !== id));
                // Si el eliminado es el actual, limpiar
                if (currentAnalysis && currentAnalysis.id === id) {
                    setCurrentAnalysis(null);
                }
            } catch (error) {
                console.error('Error deleting analysis:', error);
            }
        },
        [currentAnalysis]
    );

    const clearCurrentAnalysis = useCallback(() => {
        setCurrentAnalysis(null);
    }, []);

    const value = {
        history,
        currentAnalysis,
        loading,
        fetchHistory,
        loadAnalysis,
        deleteAnalysis,
        refreshHistory,
        clearCurrentAnalysis
    };

    return <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>;
};
