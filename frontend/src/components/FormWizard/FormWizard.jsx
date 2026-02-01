import React, { useState, useEffect } from 'react';
import { useFormData } from '../../hooks/useFormData';
import { useFormValidation } from '../../hooks/useFormValidation';
import { useAnalysisSubmit } from '../../hooks/useAnalysisSubmit';
import LocationStep from './LocationStep';
import PropertyInfoStep from './PropertyInfoStep';
import InfrastructureStep from './InfrastructureStep';
import ResultsView from './ResultsView';

const FormWizard = ({ userRole, onLoadRequest, initialData }) => {
    // 1. Hooks de Lógica de Negocio
    const {
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
    } = useFormData(initialData);

    const { validationErrors, setValidationErrors, validateInputs } = useFormValidation();

    // Notar que passamos setModalConfig como null porque InfrastructureStep maneja su propio modal vía hook interno.
    // Pero useAnalysisSubmit también soporta modal de Sanity Check.
    // Para que useAnalysisSubmit pueda mostrar SU modal, necesitamos un estado de modal aquí o usar un ref.
    // Por simplicidad en esta fase, usaremos un estado local para el modal de submit si es necesario,
    // pero el hook useAnalysisSubmit pide 'setModalConfig'.
    // Implementaremos el modal de sanity check aquí en el contenedor.
    const [sanityModalConfig, setSanityModalConfig] = useState(null);

    const { loading, submitAnalysis } = useAnalysisSubmit(setResult, setValidationErrors, setSanityModalConfig);

    // 2. Estado del Wizard
    const [currentStep, setCurrentStep] = useState(1);

    // Scroll top on step change
    useEffect(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, [currentStep, result]);

    // Si hay resultado, mostramos la vista de resultados (sería "Paso 4" virtual)
    const showResults = !!result;

    // 3. Handlers de Navegación
    const handleNext = () => {
        // Validaciones simples por paso
        if (currentStep === 1) {
            if (!selectedState || !selectedMuni) {
                alert('Por favor seleccione Estado y Municipio.');
                return;
            }
        }
        if (currentStep === 2) {
            if (!formData.tipoInmueble) {
                alert('Seleccione un tipo de inmueble.');
                return;
            }
            // Validar que m2 sea numérico si se ingresó algo
            if (formData.m2Construccion && parseFloat(formData.m2Construccion) <= 0) {
                alert('Los M² deben ser mayores a 0.');
                return;
            }
        }

        setCurrentStep((prev) => prev + 1);
    };

    const handleBack = () => {
        if (showResults) {
            // Si estamos en resultados, 'volver' podría significar borrar resultado y volver a editar
            if (window.confirm('¿Desea volver a editar los datos? Se borrará el análisis actual.')) {
                setResult(null);
                // Mantenemos step 3
            }
            return;
        }
        setCurrentStep((prev) => Math.max(prev - 1, 1));
    };

    const handleAnalyze = () => {
        // Trigger análisis
        submitAnalysis(formData, selectedMuni, selectedState, validateInputs);
    };

    // 4. Renderizado Condicional
    return (
        <div className="max-w-4xl mx-auto p-6 bg-white shadow-xl rounded-xl min-h-[600px]">
            {/* Header */}
            <div className="mb-6 flex justify-between items-center border-b pb-4">
                <div>
                    <h2 className="text-3xl font-bold text-slate-800">GIRRD PC AI</h2>
                    <p className="text-slate-500">Sistema Experto en análisis normativo</p>
                </div>
                {userRole && <div className="text-xs font-mono bg-slate-100 px-2 py-1 rounded">Rol: {userRole}</div>}
            </div>

            {/* Modal de Sanity Check (Coherencia Dimensional) */}
            {sanityModalConfig && sanityModalConfig.show && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm animate-fade-in">
                    <div className="bg-white rounded-lg shadow-2xl max-w-lg w-full p-6 border-l-8 border-yellow-400">
                        <h3 className="text-xl font-bold mb-4 text-yellow-700">{sanityModalConfig.title}</h3>
                        <p className="text-gray-700 mb-6 whitespace-pre-line">{sanityModalConfig.message}</p>
                        <div className="flex justify-end gap-3">
                            <button
                                onClick={sanityModalConfig.onCancel}
                                className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                            >
                                Corregir
                            </button>
                            <button
                                onClick={sanityModalConfig.onConfirm}
                                className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 font-bold"
                            >
                                Confirmar Datos
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Stepper (Solo si no hay resultados) */}
            {!showResults && (
                <div className="mb-8">
                    <div className="flex items-center justify-between relative">
                        {/* Línea conectora */}
                        <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-full h-1 bg-gray-200 -z-10"></div>

                        {[1, 2, 3].map((step) => (
                            <div key={step} className={`flex flex-col items-center bg-white px-2`}>
                                <div
                                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white transition-all ${step <= currentStep ? 'bg-indigo-600 scale-110' : 'bg-gray-300'}`}
                                >
                                    {step}
                                </div>
                                <span className="text-xs font-semibold text-gray-500 mt-2 uppercase">
                                    {step === 1 ? 'Ubicación' : step === 2 ? 'Inmueble' : 'Infraestructura'}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Contenido de Pasos */}
            <div className="min-h-[400px]">
                {showResults ? (
                    <ResultsView
                        result={result}
                        setResult={setResult}
                        formData={formData}
                        selectedState={selectedState}
                        selectedMuni={selectedMuni}
                        signatureImage={signatureImage}
                        setSignatureImage={setSignatureImage}
                        userRole={userRole}
                    />
                ) : (
                    <>
                        {currentStep === 1 && (
                            <LocationStep
                                selectedState={selectedState}
                                setSelectedState={setSelectedState}
                                selectedMuni={selectedMuni}
                                setSelectedMuni={setSelectedMuni}
                            />
                        )}
                        {currentStep === 2 && (
                            <PropertyInfoStep
                                formData={formData}
                                handleInputChange={handleInputChange}
                                validationErrors={validationErrors}
                            />
                        )}
                        {currentStep === 3 && (
                            <InfrastructureStep
                                formData={formData}
                                setFormData={setFormData}
                                onAnalyze={handleAnalyze}
                                loading={loading}
                            />
                        )}
                    </>
                )}
            </div>

            {/* Navegación (Footer de Wizard) */}
            {!showResults && (
                <div className="mt-8 flex justify-between border-t pt-6">
                    <button
                        onClick={handleBack}
                        disabled={currentStep === 1}
                        className={`px-6 py-2 rounded font-semibold transition-colors ${currentStep === 1 ? 'text-gray-300 cursor-not-allowed' : 'text-slate-600 hover:bg-slate-100'}`}
                    >
                        &larr; Anterior
                    </button>

                    {currentStep < 3 && (
                        <button
                            onClick={handleNext}
                            className="px-8 py-2 bg-indigo-600 text-white rounded font-bold shadow hover:bg-indigo-700 transition-transform transform hover:scale-105"
                        >
                            Siguiente &rarr;
                        </button>
                    )}
                </div>
            )}
        </div>
    );
};

export default FormWizard;
