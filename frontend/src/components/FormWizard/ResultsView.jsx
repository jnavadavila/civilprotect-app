import React, { useState } from 'react';
import axios from '../../utils/axios';
import BudgetManager from '../BudgetManager';
import NormativeChecklist from '../NormativeChecklist';
import SignaturePad from '../SignaturePad';

const ResultsView = ({
    result,
    setResult,
    formData,
    selectedState, // Needed for legal text
    selectedMuni, // Needed for Save Record
    signatureImage,
    setSignatureImage,
    userRole
}) => {
    const [activeTab, setActiveTab] = useState('resumen');

    const downloadPDF = async () => {
        if (!result) return;

        try {
            // [NUEVO LOGICA: FIRMA]
            if (signatureImage) {
                // Si hay firma, pedimos al backend que REGENERE el PDF con ella
                const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
                const payload = {
                    report_data: result.data,
                    signature_image: signatureImage
                };

                // UX Feedback
                const originalText = document.activeElement.innerText;
                document.activeElement.innerText = 'Firmando PDF...';

                const response = await axios.post(`${apiUrl}/sign-report`, payload);

                if (response.data.status === 'success') {
                    // [FIX] Usar Blob request también para firma
                    const fileRes = await axios.get(`${apiUrl}${response.data.download_url}`, {
                        responseType: 'blob'
                    });

                    const url = window.URL.createObjectURL(new Blob([fileRes.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', response.data.pdf_filename);
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                    window.URL.revokeObjectURL(url);

                    document.activeElement.innerText = originalText;
                    return;
                }
            }

            // [FALLBACK] Descarga Normal (Sin Firma o si falla anterior)
            if (result.download_url) {
                // [FIX] Usar blob request para incluir headers de auth
                const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
                const fileRes = await axios.get(`${apiUrl}${result.download_url}`, {
                    responseType: 'blob'
                });

                const url = window.URL.createObjectURL(new Blob([fileRes.data]));
                const link = document.createElement('a');
                link.href = url;

                if (result.pdf_filename) {
                    link.setAttribute('download', result.pdf_filename);
                } else {
                    link.setAttribute('download', 'Dictamen_PC.pdf');
                }

                document.body.appendChild(link);
                link.click();
                link.remove();
                window.URL.revokeObjectURL(url); // Clean up memory
            } else {
                alert('El PDF aún no se ha generado.');
            }
        } catch (err) {
            console.error('Error PDF:', err);
            alert('Error al descargar el PDF firmado.');
        }
    };

    const saveRecord = async () => {
        if (!result) {
            alert('No hay análisis para guardar. Ejecute un análisis primero.');
            return;
        }

        try {
            // Solicitar etiqueta personalizada (opcional)
            const customLabel = window.prompt(
                "Etiqueta personalizada (opcional):\nEjemplo: 'Restaurante La Morena - Revisión Inicial'",
                `${formData.tipoInmueble} - ${selectedMuni}`
            );

            // Preparar input_data (formulario original)
            const inputData = {
                tipo_inmueble: formData.tipoInmueble,
                m2_construccion: parseFloat(formData.m2Construccion) || 0,
                niveles: parseInt(formData.nivelesTotales) || 1,
                aforo: parseInt(formData.aforoMax) || 0,
                aforo_autorizado: parseInt(formData.aforoAutorizado) || 0,
                trabajadores: parseInt(formData.numTrabajadores) || 0,
                municipio: selectedMuni,
                estado: selectedState,
                has_gas: formData.hasGas,
                has_transformer: formData.hasTransformer,
                has_machine_room: formData.hasMachineRoom,
                has_substation: formData.hasSubstation,
                has_pool: formData.hasPool,
                has_special_inst: formData.hasSpecialInst
            };

            // Preparar payload
            const payload = {
                input_data: inputData,
                report_data: result.data,
                custom_label: customLabel || null,
                pdf_filename: null // Se generará bajo demanda
            };

            const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
            const response = await axios.post(`${apiUrl}/save-analysis`, payload);

            if (response.data.status === 'success') {
                alert(
                    `✅ Expediente guardado exitosamente\n\nID: ${response.data.analysis_id}\nFecha: ${new Date(response.data.created_at).toLocaleString('es-MX')}`
                );
            } else {
                alert(`❌ Error: ${response.data.message}`);
            }
        } catch (error) {
            console.error('Error guardando expediente:', error);
            alert('❌ Error de conexión al guardar el expediente.');
        }
    };

    return (
        <div className="space-y-6 animate-fadeIn">
            <h3 className="text-xl font-semibold text-slate-700 border-b pb-2">Resultados del Análisis</h3>
            {/* 1. FUNDAMENTO LEGAL (OBJETIVO) */}
            <div className="p-6 bg-slate-800 text-white border-l-4 border-blue-500 rounded-r-xl mb-6 shadow-lg">
                <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                    <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"
                        ></path>
                    </svg>
                    {result.data.ai_analysis ? 'Análisis Legal por Inteligencia Artificial' : 'Fundamento Legal'}
                </h3>
                <div className="mb-4 text-blue-100 text-lg">
                    {result.data.resumen_ejecutivo?.legal_justification_strict ? (
                        <span className="font-mono text-sm leading-relaxed block bg-slate-900 p-4 rounded border border-slate-600">
                            {result.data.resumen_ejecutivo.legal_justification_strict}
                        </span>
                    ) : result.data.ai_analysis ? (
                        <span>{result.data.ai_analysis.legal_justification}</span>
                    ) : (
                        <span>
                            El inmueble está <strong>OBLIGADO</strong> a presentar Programa Interno de Protección Civil
                            (PIPC).
                        </span>
                    )}
                </div>

                {result.data.ai_analysis && (
                    <div className="bg-slate-700 p-4 rounded-lg mt-2">
                        <p className="font-bold text-sm text-gray-300 uppercase mb-1">Vigilancia Normativa:</p>
                        <ul className="list-disc list-inside text-sm text-gray-200">
                            {result.data.ai_analysis.normative_updates.map((update, idx) => (
                                <li key={idx}>{update}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {!result.data.ai_analysis && (
                    <div className="bg-slate-700 p-4 rounded-lg">
                        <p className="font-bold text-sm text-gray-300 uppercase mb-1">Base Jurídica de la Autoridad:</p>
                        <p className="text-white italic">
                            "De acuerdo al <strong>Artículo 39 de la Ley General de Protección Civil</strong> y el
                            Reglamento Estatal de {selectedState}, los inmuebles de afluencia masiva (
                            {formData.aforoMax} personas) y alto riesgo de incendio están obligados a contar con un
                            programa autorizado."
                        </p>
                    </div>
                )}
            </div>
            {/* 2. BARRA DE NAVEGACIÓN MODULAR */}
            <div className="flex gap-4 mb-6 border-b border-gray-300 pb-2">
                <button
                    onClick={() => setActiveTab('resumen')}
                    className={`px-4 py-2 font-bold rounded-t-lg transition-colors ${activeTab === 'resumen' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:bg-gray-100'}`}
                >
                    Resumen Ejecutivo
                </button>
                <button
                    onClick={() => setActiveTab('checklist')}
                    className={`px-4 py-2 font-bold rounded-t-lg transition-colors ${activeTab === 'checklist' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:bg-gray-100'}`}
                >
                    Check List Normativo Completo
                </button>
                <button
                    onClick={() => setActiveTab('costos')}
                    className={`px-4 py-2 font-bold rounded-t-lg transition-colors ${activeTab === 'costos' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:bg-gray-100'}`}
                >
                    Análisis de Costos
                </button>
            </div>
            {/* 3. CONTENIDO DINÁMICO */}
            <div className="bg-white rounded-xl min-h-[300px]">
                {activeTab === 'resumen' && (
                    <div className="p-6 bg-green-50 border border-green-200 rounded-xl">
                        <h4 className="font-bold text-green-800 mb-4">Requerimientos Físicos Inmediatos</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <p className="mb-1 text-sm font-bold text-gray-700">Equipamiento Básico:</p>
                                <ul className="list-disc list-inside text-sm text-gray-600">
                                    <li>
                                        Extintores PQS:{' '}
                                        {result.data.basic_requirements?.extintores?.base_PQS?.cantidad || 0}
                                    </li>
                                    <li>
                                        Brigadistas Requeridos:{' '}
                                        {result.data.basic_requirements?.brigadas?.total_brigadistas || 0}
                                    </li>
                                    <li>
                                        Detectores de Humo:{' '}
                                        {result.data.basic_requirements?.alertamiento?.detectores_humo || 0}
                                    </li>
                                </ul>
                            </div>
                            {/* COLUMNA DERECHA: FIRMA DIGITAL EMBEBIDA */}
                            <div
                                className="border border-green-200 rounded-lg p-3 bg-white flex flex-col items-center justify-between"
                                style={{ minHeight: '220px' }}
                            >
                                <div className="w-full flex-shrink-0" style={{ height: '130px', marginBottom: '10px' }}>
                                    <SignaturePad
                                        isEmbedded={true}
                                        width={300}
                                        height={120}
                                        onSave={(img) => {
                                            setSignatureImage(img);
                                            // También guardar en result.data para persistencia
                                            if (result) {
                                                setResult((prev) => ({
                                                    ...prev,
                                                    data: {
                                                        ...prev.data,
                                                        signature_image: img
                                                    }
                                                }));
                                            }
                                        }}
                                        onCancel={() => {
                                            setSignatureImage(null);
                                            // Limpiar de result.data
                                            if (result) {
                                                setResult((prev) => ({
                                                    ...prev,
                                                    data: {
                                                        ...prev.data,
                                                        signature_image: null
                                                    }
                                                }));
                                            }
                                        }}
                                    />
                                </div>
                                <div className="mt-3 text-center w-full">
                                    <div className="w-48 border-b border-gray-400 mb-1 mx-auto"></div>
                                    <p className="text-xs font-bold text-gray-700">
                                        Analista: {userRole === 'ADMIN' ? 'Administrador' : 'Analista Certificado'}
                                    </p>
                                </div>
                            </div>
                        </div>
                        <p className="mt-4 text-sm text-gray-600 italic">
                            El Dictamen PDF oficial se habilitará en la barra inferior tras completar el análisis.
                        </p>
                    </div>
                )}

                {activeTab === 'checklist' && <NormativeChecklist normsData={result.data.checklist} />}

                {activeTab === 'costos' && (
                    <BudgetManager
                        initialData={result.data.presupuesto_inicial}
                        onUpdate={(items, total) => console.log('Presupuesto actualizado:', total)}
                    />
                )}
            </div>
            {/* BARRA DE ACCIONES PERMANENTE (PDF/GUARDAR) */}
            <div className="fixed bottom-0 left-0 w-full bg-white border-t border-gray-200 p-4 shadow-2xl flex justify-between items-center z-40 transition-transform transform translate-y-0">
                <div className="text-xs text-gray-500 font-medium px-4">
                    {result
                        ? '✅ Análisis completado. Acciones habilitadas.'
                        : 'ℹ️ Complete el formulario y analice para habilitar acciones.'}
                </div>
                <div className="flex gap-4 pr-8">
                    <button
                        onClick={saveRecord}
                        disabled={!result}
                        className={`px-6 py-2 rounded-lg font-bold flex items-center gap-2 transition-all ${result ? 'bg-green-600 hover:bg-green-700 text-white shadow-lg' : 'bg-gray-100 text-gray-300 cursor-not-allowed border border-gray-200'}`}
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
                            ></path>
                        </svg>
                        Guardar Expediente
                    </button>

                    <button
                        onClick={downloadPDF}
                        disabled={!result}
                        className={`px-6 py-2 rounded-lg font-bold flex items-center gap-2 transition-all ${result ? 'bg-blue-800 hover:bg-blue-900 text-white shadow-lg' : 'bg-gray-100 text-gray-300 cursor-not-allowed border border-gray-200'}`}
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            ></path>
                        </svg>
                        Descargar Dictamen Oficial
                    </button>
                    {userRole === 'ADMIN' && (
                        <button className="bg-gray-800 text-white px-3 py-2 rounded hover:bg-black">⚙️</button>
                    )}
                </div>
            </div>
            <div className="h-24"></div> {/* Espaciador para el footer fijo */}
        </div>
    );
};

export default ResultsView;
