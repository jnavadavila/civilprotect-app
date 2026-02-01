import React from 'react';
import { useRiskValidation } from '../../hooks/useRiskValidation';

const InfrastructureStep = ({ formData, setFormData, onAnalyze, loading }) => {
    const { modalConfig, handleRiskChange } = useRiskValidation(formData, setFormData);

    return (
        <div className="space-y-6 animate-fadeIn">
            <h3 className="text-xl font-semibold text-slate-700 border-b pb-2">Infraestructura de Riesgo</h3>

            {/* MODAL DE CONFIRMACIÓN DE RIESGO */}
            {modalConfig && modalConfig.show && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm">
                    <div className="bg-white rounded-lg shadow-2xl max-w-lg w-full p-6 animate-bounce-in">
                        <div className="flex items-center gap-3 mb-4 text-orange-600">
                            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                                ></path>
                            </svg>
                            <h3 className="text-xl font-bold">{modalConfig.title}</h3>
                        </div>
                        <p className="text-gray-700 mb-6 whitespace-pre-wrap">{modalConfig.message}</p>
                        <div className="flex justify-end gap-3">
                            <button
                                onClick={modalConfig.onCancel}
                                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 font-medium"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={modalConfig.onConfirm}
                                className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 font-bold shadow-lg"
                            >
                                Confirmar Riesgo
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="mt-6 pt-4 border-t border-gray-200">
                <label className="block text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        ></path>
                    </svg>
                    Infraestructura de Riesgo (Marque si aplica):
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <label
                        className={`flex items-center space-x-3 p-3 rounded-lg border transition-all ${formData.hasGas ? 'bg-orange-50 border-orange-500 shadow-sm' : 'bg-white border-gray-200 hover:border-orange-300'}`}
                    >
                        <div
                            className={`p-2 rounded-full ${formData.hasGas ? 'bg-orange-100 text-orange-600' : 'bg-gray-100 text-gray-400'}`}
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="1.5"
                                    d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"
                                ></path>
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="1.5"
                                    d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z"
                                ></path>
                            </svg>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-sm font-bold text-gray-700">Instalación de Gas</span>
                            <span className="text-xs text-gray-500">LP o Natural</span>
                        </div>
                        <input
                            type="checkbox"
                            checked={formData.hasGas || false}
                            onChange={(e) => handleRiskChange('hasGas', e.target.checked)}
                            className="ml-auto form-checkbox h-5 w-5 text-orange-600 rounded focus:ring-orange-500"
                        />
                    </label>

                    <label
                        className={`flex items-center space-x-3 p-3 rounded-lg border transition-all ${formData.hasTransformer ? 'bg-yellow-50 border-yellow-500 shadow-sm' : 'bg-white border-gray-200 hover:border-yellow-300'}`}
                    >
                        <div
                            className={`p-2 rounded-full ${formData.hasTransformer ? 'bg-yellow-100 text-yellow-600' : 'bg-gray-100 text-gray-400'}`}
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="1.5"
                                    d="M13 10V3L4 14h7v7l9-11h-7z"
                                ></path>
                            </svg>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-sm font-bold text-gray-700">Transformador</span>
                            <span className="text-xs text-gray-500">Eléctrico</span>
                        </div>
                        <input
                            type="checkbox"
                            checked={formData.hasTransformer || false}
                            onChange={(e) => setFormData((prev) => ({ ...prev, hasTransformer: e.target.checked }))}
                            className="ml-auto form-checkbox h-5 w-5 text-yellow-600 rounded focus:ring-yellow-500"
                        />
                    </label>

                    <label
                        className={`flex items-center space-x-3 p-3 rounded-lg border transition-all ${formData.hasMachineRoom ? 'bg-slate-50 border-slate-500 shadow-sm' : 'bg-white border-gray-200 hover:border-slate-300'}`}
                    >
                        <div
                            className={`p-2 rounded-full ${formData.hasMachineRoom ? 'bg-slate-100 text-slate-600' : 'bg-gray-100 text-gray-400'}`}
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="1.5"
                                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                                ></path>
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="1.5"
                                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                                ></path>
                            </svg>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-sm font-bold text-gray-700">Cuarto de Máquinas</span>
                            <span className="text-xs text-gray-500">Equipos Mayores</span>
                        </div>
                        <input
                            type="checkbox"
                            checked={formData.hasMachineRoom || false}
                            onChange={(e) => handleRiskChange('hasMachineRoom', e.target.checked)}
                            className="ml-auto form-checkbox h-5 w-5 text-slate-600 rounded focus:ring-slate-500"
                        />
                    </label>

                    <label
                        className={`flex items-center space-x-3 p-3 rounded-lg border transition-all ${formData.hasSubstation ? 'bg-red-50 border-red-500 shadow-sm' : 'bg-white border-gray-200 hover:border-red-300'}`}
                    >
                        <div
                            className={`p-2 rounded-full ${formData.hasSubstation ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-400'}`}
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="1.5"
                                    d="M13 10V3L4 14h7v7l9-11h-7z"
                                ></path>
                            </svg>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-sm font-bold text-gray-700">Subestación CFE</span>
                            <span className="text-xs text-gray-500">Alta Tensión</span>
                        </div>
                        <input
                            type="checkbox"
                            checked={formData.hasSubstation || false}
                            onChange={(e) => handleRiskChange('hasSubstation', e.target.checked)}
                            className="ml-auto form-checkbox h-5 w-5 text-red-600 rounded focus:ring-red-500"
                        />
                    </label>

                    <label
                        className={`flex items-center space-x-3 p-3 rounded-lg border transition-all ${formData.hasPool ? 'bg-cyan-50 border-cyan-500 shadow-sm' : 'bg-white border-gray-200 hover:border-cyan-300'}`}
                    >
                        <div
                            className={`p-2 rounded-full ${formData.hasPool ? 'bg-cyan-100 text-cyan-600' : 'bg-gray-100 text-gray-400'}`}
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="1.5"
                                    d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
                                ></path>
                            </svg>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-sm font-bold text-gray-700">Alberca</span>
                            <span className="text-xs text-gray-500">Uso Recreativo</span>
                        </div>
                        <input
                            type="checkbox"
                            checked={formData.hasPool || false}
                            onChange={(e) => handleRiskChange('hasPool', e.target.checked)}
                            className="ml-auto form-checkbox h-5 w-5 text-cyan-600 rounded focus:ring-cyan-500"
                        />
                    </label>

                    <label
                        className={`flex items-center space-x-3 p-3 rounded-lg border transition-all ${formData.hasSpecialInst ? 'bg-purple-50 border-purple-500 shadow-sm' : 'bg-white border-gray-200 hover:border-purple-300'}`}
                    >
                        <div
                            className={`p-2 rounded-full ${formData.hasSpecialInst ? 'bg-purple-100 text-purple-600' : 'bg-gray-100 text-gray-400'}`}
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="1.5"
                                    d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
                                ></path>
                            </svg>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-sm font-bold text-gray-700">Inst. Especiales</span>
                            <span className="text-xs text-gray-500">Q. Industriales</span>
                        </div>
                        <input
                            type="checkbox"
                            checked={formData.hasSpecialInst || false}
                            onChange={(e) => handleRiskChange('hasSpecialInst', e.target.checked)}
                            className="ml-auto form-checkbox h-5 w-5 text-purple-600 rounded focus:ring-purple-500"
                        />
                    </label>
                </div>
            </div>

            {/* BOTÓN DE ANÁLISIS */}
            <div className="flex justify-center mt-10">
                <button
                    onClick={onAnalyze}
                    disabled={loading}
                    className="group relative w-full md:w-2/3 flex justify-center py-4 px-4 border border-transparent text-lg font-extrabold rounded-full text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all transform hover:scale-105 shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <div className="flex items-center">
                            <svg
                                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                            >
                                <circle
                                    className="opacity-25"
                                    cx="12"
                                    cy="12"
                                    r="10"
                                    stroke="currentColor"
                                    strokeWidth="4"
                                ></circle>
                                <path
                                    className="opacity-75"
                                    fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                ></path>
                            </svg>
                            Analizando Normatividad...
                        </div>
                    ) : (
                        <span className="flex items-center gap-2">
                            ANALIZAR RIESGOS Y REQUISITOS
                            <svg
                                className="w-6 h-6 group-hover:translate-x-1 transition-transform"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M14 5l7 7m0 0l-7 7m7-7H3"
                                ></path>
                            </svg>
                        </span>
                    )}
                </button>
            </div>
        </div>
    );
};

export default InfrastructureStep;
