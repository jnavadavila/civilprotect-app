import React, { useState } from 'react';
import SignaturePad from './SignaturePad';

const ModernReportView = ({ data, onSignatureChange }) => {
    if (!data) return null;

    const [showSignaturePad, setShowSignaturePad] = useState(false);
    const [signatureImage, setSignatureImage] = useState(null);

    // Propagate signature changes to parent
    React.useEffect(() => {
        if (onSignatureChange) {
            onSignatureChange(signatureImage);
        }
    }, [signatureImage, onSignatureChange]);

    const {
        tipo_inmueble,
        m2_construccion,
        niveles,
        aforo,
        trabajadores,
        municipio,
        estado,
        ai_analysis,
        basic_requirements,
        resumen_ejecutivo,
        checklist,
        presupuesto_inicial,
        has_gas,
        has_transformer,
        has_machine_room,
        has_substation,
        has_special_inst,
        has_pool,
        has_cocina,
        has_site
    } = data;

    // --- LOGIC SANITIZATION LAYER (The "Anti-Absurd" Filter) ---
    // Detectamos si es Aeropuerto/Terminal para bloquear lógica de Albercas
    const isAirport =
        tipo_inmueble?.toLowerCase().includes('terminal') || tipo_inmueble?.toLowerCase().includes('aeropuerto');

    // 1. Filtered Infra
    const infraList = [];
    if (has_gas) infraList.push('Gas LP/Natural');
    if (has_substation) infraList.push('Subestación Eléctrica');
    if (has_transformer) infraList.push('Transformador');
    if (has_machine_room) infraList.push('Cuarto de Máquinas');
    if (has_special_inst) infraList.push('Instalaciones Especiales');
    // Strict Lock: No pools in airports
    if (has_pool && !isAirport) infraList.push('Alberca/Cuerpo de Agua');

    // 2. Filtered Checklist (Remove "Albercas" references if Airport)
    const cleanChecklist =
        checklist?.filter((norm) => {
            if (norm.is_pipc_guide) return false; // Filter guide items if handled elsewhere
            if (
                isAirport &&
                (norm.norma.toLowerCase().includes('alberca') || norm.titulo.toLowerCase().includes('alberca'))
            )
                return false;
            return true;
        }) || [];

    // 3. Filtered Budget (Remove "Albercas" items if Airport)
    const cleanBudget =
        presupuesto_inicial?.filter((item) => {
            if (
                isAirport &&
                (item.concepto.toLowerCase().includes('alberca') || item.concepto.toLowerCase().includes('piscina'))
            )
                return false;
            return true;
        }) || [];

    const infraText = infraList.length > 0 ? infraList.join(', ') : 'No se reportó infraestructura de alto riesgo.';

    // Helper para rows tipo PDF
    const DataRow = ({ label, value, isGray }) => (
        <div className={`flex text-sm py-1 px-4 ${isGray ? 'bg-gray-100' : 'bg-white'}`}>
            <div className="w-1/3 text-gray-600 font-normal">{label}</div>
            <div className="w-2/3 font-bold text-gray-900">{value}</div>
        </div>
    );

    return (
        <div className="bg-gray-100 p-8 flex flex-col items-center gap-8 font-sans relative">
            {/* Modal de Firma Digital (Táctil) - High Z-Index */}
            {showSignaturePad && (
                <div className="fixed inset-0 z-[100]">
                    <SignaturePad
                        onSave={(img) => {
                            setSignatureImage(img);
                            setShowSignaturePad(false);
                        }}
                        onCancel={() => setShowSignaturePad(false)}
                    />
                </div>
            )}

            {/* --- PAGE 1: PORTADA & FICHA TÉCNICA --- */}
            <div
                className="bg-white text-black shadow-2xl overflow-hidden relative"
                style={{ width: '215.9mm', height: '279.4mm', padding: '15mm' }}
            >
                {/* HEADERS */}
                <div className="flex justify-between items-start mb-6">
                    <div className="flex items-center gap-4">
                        <img src="/logo_lunaya.png" alt="Logo" className="h-14 w-auto" />
                        <div className="flex leading-none tracking-tighter">
                            <span className="text-4xl font-black text-gray-500">L</span>
                            <span className="text-4xl font-black text-orange-500">Y</span>
                        </div>
                    </div>
                    <div className="text-right">
                        <h1 className="text-xl font-bold text-[#142850] uppercase leading-tight">
                            ANALISIS TÉCNICO DE OBLIGATORIEDAD
                            <br />
                            EN MATERIA DE P.C.
                        </h1>
                        <p className="text-[9px] text-gray-500 uppercase mt-1">
                            Sistema Experto de Análisis Normativo (LY GIRRD PC AI V3.0)
                        </p>
                    </div>
                </div>

                <hr className="border-t-2 border-[#142850] mb-6" />

                {/* 1. FICHA TÉCNICA */}
                <div className="mb-6">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="w-1 h-5 bg-[#142850]"></div>
                        <h2 className="text-xs font-bold uppercase text-black">FICHA TÉCNICA DEL INMUEBLE EVALUADO</h2>
                    </div>
                    <div className="border border-gray-200 text-xs">
                        <DataRow label="Tipo Inmueble:" value={tipo_inmueble} isGray={true} />
                        <DataRow
                            label="M2 Construcción:"
                            value={`${m2_construccion ? m2_construccion.toLocaleString() : '0'} m²`}
                        />
                        <DataRow label="Niveles:" value={niveles} isGray={true} />
                        <DataRow label="Aforo Real:" value={`${aforo || 0} personas`} />
                        <DataRow
                            label="Aforo Autorizado:"
                            value={`${data.aforo_autorizado || 0} personas`}
                            isGray={true}
                        />
                        <DataRow label="Trabajadores:" value={trabajadores} />
                        <DataRow label="Ubicación:" value={`${municipio}, ${estado}`} isGray={true} />
                        <DataRow
                            label="Instalaciones:"
                            value={`Cocina: ${has_cocina ? 'SÍ' : 'NO'} | Site: ${has_site ? 'SÍ' : 'NO'}`}
                        />
                    </div>
                </div>

                {/* 2. INFRAESTRUCTURA - CAJA SIMPLE */}
                {infraList.length > 0 && (
                    <div className="mb-6">
                        <h3 className="text-xs font-bold text-[#900000] uppercase mb-1">
                            INFRAESTRUCTURA DE RIESGO DETECTADA:
                        </h3>
                        <div className="border border-gray-300 p-2 text-xs text-gray-700 bg-white uppercase">
                            {infraText}
                        </div>
                    </div>
                )}

                {/* 3. FUNDAMENTACIÓN LEGAL - TEXTO LARGO */}
                <div className="mb-4">
                    <h2 className="text-xs font-bold uppercase text-black mb-2">FUNDAMENTACIÓN Y MOTIVACIÓN LEGAL:</h2>
                    <div className="flex gap-3 h-[80mm] overflow-hidden">
                        <div className="w-1 bg-blue-100 flex-shrink-0"></div>
                        <p className="text-xs text-justify leading-relaxed font-normal text-gray-800 uppercase">
                            {resumen_ejecutivo?.legal_justification_strict ||
                                ai_analysis?.legal_justification ||
                                `EL INMUEBLE ESTÁ OBLIGADO A PRESENTAR UN PROGRAMA INTERNO DE PROTECCIÓN CIVIL (PIPC) DERIVADO DE SUS CARACTERÍSTICAS FÍSICAS Y OPERATIVAS: PLANTILLA DE TRABAJADORES SUPERIOR A 25 PERSONAS, SUPERFICIE CONSTRUIDA SUPERIOR A 250 M², AFORO DE VISITANTES SUPERIOR A 50 PERSONAS. ESTA CONDICIÓN ACTIVA LA OBLIGATORIEDAD PREVISTA EN EL ARTÍCULO 39 DE LA LEY GENERAL DE PROTECCIÓN CIVIL; ARTÍCULO 58 DE LA LEY DE PROTECCIÓN CIVIL DEL ESTADO Y SU REGLAMENTO ESTATAL; ASÍ COMO LAS DISPOSICIONES DEL REGLAMENTO DE PROTECCIÓN CIVIL DEL MUNICIPIO DE ${municipio?.toUpperCase() || 'LOCAL'}.`}
                        </p>
                    </div>
                </div>

                {/* FOOTER PAGE 1 */}
                <div className="absolute bottom-[20mm] left-[15mm] right-[15mm] flex justify-between items-end border-t border-gray-300 pt-4">
                    <div className="flex flex-col gap-1">
                        <img
                            src={`https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ANALISIS-TECNICO-${municipio}-${new Date().toISOString().split('T')[0]}`}
                            alt="QR"
                            className="w-24 h-24"
                        />
                        <span className="text-[8px] text-gray-400 font-mono">
                            Folio: {new Date().getTime().toString().slice(-8)}
                        </span>
                    </div>

                    <div className="text-center relative group w-64">
                        {/* ZONA DE FIRMA - STATIC POSITIONING (NO ABSOLUTE) */}
                        <div className="mb-4 flex flex-col items-center justify-end min-h-[50px]">
                            {signatureImage ? (
                                <img
                                    src={signatureImage}
                                    alt="Firma Analista"
                                    className="h-16 object-contain mix-blend-multiply"
                                />
                            ) : (
                                <button
                                    onClick={() => setShowSignaturePad(true)}
                                    className="print:hidden z-50 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg shadow-lg border-2 border-white animate-pulse"
                                    style={{ boxShadow: '0 0 15px rgba(37, 99, 235, 0.5)' }}
                                >
                                    ✍️ FIRMAR AQUÍ
                                </button>
                            )}
                        </div>

                        <p className="text-[9px] font-bold mb-2 pt-2">Firma del Analista:</p>
                        <div className="w-56 border-b border-black mb-2 mx-auto"></div>
                        <p className="text-[8px] text-gray-500 italic">
                            "Este documento es una guía técnica pre-aprobatoria. DR. JMND"
                        </p>

                        {/* Botón Reset Firma */}
                        {signatureImage && (
                            <button
                                onClick={() => setSignatureImage(null)}
                                className="print:hidden absolute -right-4 top-0 bg-red-100 text-red-600 rounded-full p-1 hover:bg-red-200 z-50"
                                title="Borrar Firma"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth="2"
                                        d="M6 18L18 6M6 6l12 12"
                                    ></path>
                                </svg>
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* --- PAGE 2+: MATRIZ DE CUMPLIMIENTO (FLUJO CONTINUO) --- */}
            <div
                className="bg-white text-black shadow-2xl relative print:shadow-none print:w-full print:h-auto"
                style={{ width: '215.9mm', minHeight: '279.4mm', padding: '15mm' }}
            >
                <div className="flex justify-between items-center mb-6 border-b border-gray-300 pb-2">
                    <h2 className="text-sm font-bold uppercase text-black">
                        2. MATRIZ DE CUMPLIMIENTO (SISTEMA JERÁRQUICO)
                    </h2>
                </div>

                <div className="space-y-4">
                    {/* Renderizado COMPLETO del Checklist */}
                    {cleanChecklist.map((norm, idx) => (
                        <div key={idx} className="border border-gray-300 mb-2 break-inside-avoid">
                            <div
                                className={`px-2 py-1 text-[10px] font-bold border-b border-gray-300 ${norm.norma.includes('FEDERAL') ? 'bg-red-50' : norm.norma.includes('ESTATAL') ? 'bg-orange-50' : 'bg-gray-100'}`}
                            >
                                {norm.norma} - {norm.titulo}
                            </div>
                            <div className="p-2 space-y-1">
                                {norm.checks.map((check, cIdx) => (
                                    <div key={cIdx} className="flex justify-between text-[9px]">
                                        <span>[ ] {check.desc.substring(0, 130)}</span>
                                        <span className="text-gray-500 italic whitespace-nowrap ml-2">
                                            Art. {check.art}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* --- PAGE 3: PRESUPUESTO --- */}
            <div
                className="bg-white text-black shadow-2xl overflow-hidden relative"
                style={{ width: '215.9mm', height: '279.4mm', padding: '15mm' }}
            >
                <div className="flex justify-between items-center mb-6 border-b border-gray-300 pb-2">
                    <h2 className="text-sm font-bold uppercase text-black">
                        3. PRESUPUESTO ESTIMADO DE IMPLEMENTACIÓN
                    </h2>
                    <span className="text-[10px] text-gray-400">Página 3</span>
                </div>

                <div className="border border-gray-200">
                    <table className="w-full text-xs">
                        <thead className="bg-[#142850] text-white">
                            <tr>
                                <th className="p-2 text-left">CONCEPTO</th>
                                <th className="p-2 text-center">CANT.</th>
                                <th className="p-2 text-right">P. UNITARIO</th>
                                <th className="p-2 text-right">IMPORTE</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {cleanBudget.map((item, idx) => (
                                <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                    <td className="p-2 font-bold text-gray-800">{item.concepto}</td>
                                    <td className="p-2 text-center text-gray-600">{item.cantidad}</td>
                                    <td className="p-2 text-right text-gray-600">
                                        ${item.precio_unitario?.toLocaleString()}
                                    </td>
                                    <td className="p-2 text-right font-bold text-black">
                                        ${((item.cantidad || 0) * (item.precio_unitario || 0)).toLocaleString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                        <tfoot className="bg-gray-100 font-bold border-t-2 border-black">
                            <tr>
                                <td colSpan="3" className="p-3 text-right uppercase">
                                    Total Estimado (Antes IVA):
                                </td>
                                <td className="p-3 text-right text-base">
                                    $
                                    {cleanBudget
                                        .reduce((acc, i) => acc + (i.cantidad || 0) * (i.precio_unitario || 0), 0)
                                        .toLocaleString('es-MX', { minimumFractionDigits: 2 }) || '0.00'}
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>

                <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 text-xs text-justify text-yellow-900">
                    <strong>NOTA IMPORTANTE:</strong> Los precios mostrados son referencias de mercado 2026 para fines
                    de presupuestación preliminar. No constituyen una oferta comercial vinculante. Se recomienda
                    solicitar 3 cotizaciones formales a proveedores certificados en su localidad antes de iniciar la
                    implementación.
                </div>
            </div>

            <style>{`
                @media print {
                    @page { size: letter; margin: 0; }
                    body { margin: 0; -webkit-print-color-adjust: exact; background: white; }
                    .shadow-2xl { shadow: none !important; border: none !important; margin: 0 !important; page-break-after: always; }
                    .bg-gray-100 { background: white !important; }
                    .gap-8 { gap: 0 !important; }
                    .print\\:hidden { display: none !important; }
                }
            `}</style>
        </div>
    );
};
