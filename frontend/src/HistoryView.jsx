import React, { useState, useEffect } from 'react';
import { useAnalysis } from './hooks/useAnalysis';

const HistoryView = ({ onLoadAnalysis }) => {
    // Usar Contexto Global
    const { history, loading, fetchHistory, deleteAnalysis } = useAnalysis();

    const [filter, setFilter] = useState({ keyword: '', estado: '' });

    // Cargar historial al montar (si no está cargado)
    useEffect(() => {
        fetchHistory();
    }, [fetchHistory]);

    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    // Función para formatear fechas
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-MX', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const handleDeleteAnalysis = async (id) => {
        if (!window.confirm('¿Seguro que deseas eliminar este análisis?')) return;
        await deleteAnalysis(id);
    };

    const handleDownloadPDF = (pdfPath) => {
        const filename = pdfPath.split('/').pop() || 'reporte.pdf';
        window.open(`${apiUrl}/download-pdf/${filename}`, '_blank');
    };

    const filteredAnalyses = history.filter((a) => {
        const term = filter.keyword.toLowerCase();
        const matchKeyword =
            !filter.keyword ||
            a.municipio.toLowerCase().includes(term) ||
            (a.custom_label && a.custom_label.toLowerCase().includes(term));

        const matchEst = !filter.estado || a.estado.toLowerCase().includes(filter.estado.toLowerCase());
        return matchKeyword && matchEst;
    });

    if (loading && history.length === 0) {
        return (
            <div className="flex items-center justify-center py-20">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent"></div>
                    <p className="mt-6 text-gray-600 font-medium">Cargando historial...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto p-6">
            <div className="bg-white shadow-2xl rounded-2xl overflow-hidden border border-gray-100">
                {/* Filtros */}
                <div className="p-6 bg-gradient-to-b from-gray-50 to-white border-b">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="relative">
                            <svg
                                className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                                ></path>
                            </svg>
                            <input
                                type="text"
                                placeholder="Buscar municipio o empresa..."
                                value={filter.keyword}
                                onChange={(e) => setFilter({ ...filter, keyword: e.target.value })}
                                className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all font-medium"
                            />
                        </div>
                        <div className="relative">
                            <svg
                                className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                                ></path>
                            </svg>
                            <input
                                type="text"
                                placeholder="Filtrar estado..."
                                value={filter.estado}
                                onChange={(e) => setFilter({ ...filter, estado: e.target.value })}
                                className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all font-medium"
                            />
                        </div>
                        <button
                            onClick={() => setFilter({ municipio: '', estado: '' })}
                            className="px-6 py-3 bg-gradient-to-r from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 rounded-xl font-bold text-gray-700 transition-all shadow-sm flex items-center justify-center gap-2"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                                ></path>
                            </svg>
                            Limpiar
                        </button>
                    </div>
                </div>

                {/* Grid de análisis */}
                <div className="p-8 bg-gradient-to-b from-white to-gray-50 min-h-[400px]">
                    {filteredAnalyses.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-20">
                            <svg
                                className="w-24 h-24 text-gray-300 mb-6"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="1.5"
                                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                ></path>
                            </svg>
                            <p className="text-gray-500 text-xl font-semibold">No hay análisis guardados</p>
                            <p className="text-gray-400 text-sm mt-2">Los análisis se guardan automáticamente</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {filteredAnalyses.map((a) => (
                                <div
                                    key={a.id}
                                    className="group bg-white border-2 border-gray-200 rounded-2xl p-6 hover:border-blue-400 hover:shadow-2xl transition-all transform hover:-translate-y-1"
                                >
                                    <div className="absolute top-4 right-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-xs font-black px-3 py-1 rounded-full shadow-lg">
                                        #{a.id}
                                    </div>

                                    <div className="border-b border-gray-200 pb-4 mb-4">
                                        <h3 className="font-black text-lg text-gray-800 pr-12">
                                            {a.custom_label || `Análisis ${a.id}`}
                                        </h3>
                                        <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                                            <svg
                                                className="w-4 h-4"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                                                ></path>
                                            </svg>
                                            <span className="font-medium">{formatDate(a.created_at)}</span>
                                        </div>
                                    </div>

                                    <div className="space-y-3 mb-6">
                                        <div className="flex items-start gap-2">
                                            <svg
                                                className="w-5 h-5 text-blue-500 mt-0.5"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                                                ></path>
                                            </svg>
                                            <div className="text-sm">
                                                <span className="font-semibold text-gray-700">Ubicación:</span>
                                                <p className="text-gray-900 font-bold">
                                                    {a.municipio}, {a.estado}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-start gap-2">
                                            <svg
                                                className="w-5 h-5 text-green-500 mt-0.5"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                                                ></path>
                                            </svg>
                                            <div className="text-sm">
                                                <span className="font-semibold text-gray-700">Tipo:</span>
                                                <p className="text-gray-900 font-bold">{a.tipo_inmueble}</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex flex-col gap-2">
                                        <button
                                            onClick={() => onLoadAnalysis(a.id)}
                                            className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl font-bold flex items-center justify-center gap-2"
                                        >
                                            <svg
                                                className="w-5 h-5"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                                ></path>
                                            </svg>
                                            Cargar
                                        </button>
                                        {a.has_pdf && (
                                            <button
                                                onClick={() => handleDownloadPDF(a.pdf_path)}
                                                className="w-full px-4 py-3 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-xl font-bold flex items-center justify-center gap-2"
                                            >
                                                <svg
                                                    className="w-5 h-5"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                        strokeWidth="2"
                                                        d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                                    ></path>
                                                </svg>
                                                PDF
                                            </button>
                                        )}
                                        <button
                                            onClick={() => window.open(`${apiUrl}/preview-html/${a.id}`, '_blank')}
                                            className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white rounded-xl font-bold flex items-center justify-center gap-2"
                                        >
                                            <svg
                                                className="w-5 h-5"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                                ></path>
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                                                ></path>
                                            </svg>
                                            HTML
                                        </button>
                                        <button
                                            onClick={() => handleDeleteAnalysis(a.id)}
                                            className="w-full px-4 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-xl font-bold flex items-center justify-center gap-2"
                                        >
                                            <svg
                                                className="w-5 h-5"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                                ></path>
                                            </svg>
                                            Eliminar
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-5 bg-gradient-to-r from-gray-50 to-gray-100 border-t flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm">
                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                            ></path>
                        </svg>
                        <span className="text-gray-600 font-medium">
                            Mostrando <span className="font-bold text-blue-600">{filteredAnalyses.length}</span> de{' '}
                            <span className="font-bold text-blue-600">{history.length}</span>
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HistoryView;
