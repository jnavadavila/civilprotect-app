import React, { useState, useEffect } from 'react';
import { useCatalogData } from '../../hooks/useCatalogData';
import IndicatorButton from './IndicatorButton';

const LocationStep = ({ selectedState, setSelectedState, selectedMuni, setSelectedMuni }) => {
    const { catalogData, loadingCatalog, getMuniMetadata } = useCatalogData();
    const [muniData, setMuniData] = useState(null);

    // Actualizar metadata visual cuando cambia selección
    useEffect(() => {
        if (selectedState && selectedMuni && catalogData.estados.length > 0) {
            const data = getMuniMetadata(selectedState, selectedMuni);
            setMuniData(data);
        } else {
            setMuniData(null);
        }
    }, [selectedState, selectedMuni, catalogData, getMuniMetadata]);

    const handleStateChange = (e) => {
        setSelectedState(e.target.value);
        setSelectedMuni('');
        setMuniData(null);
    };

    const handleMuniChange = (e) => {
        setSelectedMuni(e.target.value);
    };

    if (loadingCatalog) {
        return <div className="p-4 text-center text-gray-500">Cargando catálogos geográficos...</div>;
    }

    return (
        <div className="space-y-6 animate-fadeIn">
            <h3 className="text-xl font-semibold text-slate-700 border-b pb-2">Ubicación del Inmueble</h3>

            {/* SECCIÓN 1: GEOGRAFÍA */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div>
                    <label className="block text-sm font-medium text-gray-700 flex items-center gap-2">
                        <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            ></path>
                        </svg>
                        Estado
                    </label>
                    <select
                        className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                        value={selectedState}
                        onChange={handleStateChange}
                    >
                        <option value="">Seleccione Estado...</option>
                        {catalogData.estados.map((estado) => (
                            <option key={estado.nombre} value={estado.nombre}>
                                {estado.nombre}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 flex items-center gap-2">
                        <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                            ></path>
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                            ></path>
                        </svg>
                        Municipio
                    </label>
                    <select
                        className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                        onChange={handleMuniChange}
                        value={selectedMuni}
                        disabled={!selectedState}
                    >
                        <option value="">Seleccione Municipio...</option>
                        {catalogData.estados
                            .find((e) => e.nombre === selectedState)
                            ?.municipios.map((m) => (
                                <option key={m.nombre} value={m.nombre}>
                                    {m.nombre}
                                </option>
                            ))}
                    </select>
                </div>
            </div>

            {/* BOTONES INDICADORES AUTOMÁTICOS */}
            <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-8">
                <IndicatorButton
                    label="Aeropuerto"
                    active={muniData?.hasAirport}
                    color="blue"
                    icon={
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="1.5"
                                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                            ></path>
                        </svg>
                    }
                />
                <IndicatorButton
                    label="Polo Turístico"
                    active={muniData?.isTuristico}
                    color="orange"
                    icon={
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="1.5"
                                d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                            ></path>
                        </svg>
                    }
                />
                <IndicatorButton
                    label="Pueblo Mágico"
                    active={muniData?.isPuebloMagico}
                    color="purple"
                    icon={
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="1.5"
                                d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
                            ></path>
                        </svg>
                    }
                />
                <IndicatorButton
                    label="Zona Industrial"
                    active={muniData?.isIndustrial}
                    color="gray"
                    icon={
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="1.5"
                                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                            ></path>
                        </svg>
                    }
                />
                <IndicatorButton
                    label="Zona Fronteriza"
                    active={muniData?.isFrontera}
                    color="red"
                    icon={
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="1.5"
                                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0121 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                            ></path>
                        </svg>
                    }
                />
                <IndicatorButton
                    label="Puerto Marítimo"
                    active={muniData?.isPuerto}
                    color="cyan"
                    icon={
                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="1.5"
                                d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.015a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72l1.189-1.19A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z"
                            ></path>
                        </svg>
                    }
                />
            </div>
        </div>
    );
};

export default LocationStep;
