import React from 'react';

export default function NormativeChecklist({ normsData }) {
    if (!normsData) return null;

    // Detectar si viene la Guía PIPC en la data
    const guideData = normsData.find((n) => n.is_pipc_guide === true);
    const normsOnly = normsData.filter((n) => !n.is_pipc_guide);

    return (
        <div className="mt-8 space-y-8">
            {/* SECCIÓN 1: WIZARD DE INTEGRACIÓN PIPC (NUEVO - "SCIENTIFIC/EXPERT") */}
            {guideData && (
                <div className="bg-white border border-blue-200 rounded-xl shadow-sm overflow-hidden">
                    <div className="bg-blue-900 text-white px-6 py-4 flex items-center justify-between">
                        <h3 className="text-xl font-bold flex items-center gap-2">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                ></path>
                            </svg>
                            Guía de Integración Documental (Estructura de Carpeta)
                        </h3>
                        <span className="bg-blue-700 text-xs py-1 px-3 rounded-full uppercase tracking-wider font-semibold">
                            Base: TR-SGIRPC / Guías Estatales
                        </span>
                    </div>

                    <div className="p-6 bg-blue-50/50">
                        <p className="text-sm text-slate-600 mb-6">
                            Para conformar el Expediente Técnico Legal, asegúrese de integrar las siguientes carpetas
                            conforme al índice oficial. Marque los documentos a medida que los integre al expediente
                            físico/digital.
                        </p>

                        <div className="space-y-6">
                            {guideData.guide_content.map((capitulo, idx) => (
                                <div key={idx} className="bg-white border border-blue-100 rounded-lg shadow-sm">
                                    <h4 className="px-4 py-3 bg-blue-100/50 text-blue-900 font-bold border-b border-blue-100">
                                        {capitulo.capitulo}
                                    </h4>
                                    <div className="p-4 grid grid-cols-1 gap-2">
                                        {capitulo.items.map((item, i) => (
                                            <label
                                                key={i}
                                                className="flex items-start gap-3 p-2 hover:bg-gray-50 rounded cursor-pointer transition-colors border border-transparent hover:border-gray-200 group"
                                            >
                                                <input
                                                    type="checkbox"
                                                    className="mt-1 h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                                                />
                                                <div className="flex-1">
                                                    <span className="text-sm font-medium text-gray-800 group-hover:text-blue-700 transition-colors block">
                                                        {item.req}
                                                    </span>
                                                    <span className="text-xs text-gray-500 font-mono">
                                                        Ref: {item.fundamento}
                                                    </span>
                                                </div>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Enlaces de soporte (Mantener accesibles pero secundarios) */}
                        <div className="mt-6 pt-6 border-t border-blue-200">
                            {guideData.titulo.includes('FEDERAL') ? (
                                <div className="flex items-center gap-3 p-3 bg-yellow-50 text-yellow-800 rounded-lg border border-yellow-200">
                                    <svg
                                        className="w-5 h-5 flex-shrink-0"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="2"
                                            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                        ></path>
                                    </svg>
                                    <p className="text-xs font-bold uppercase tracking-wide">
                                        EN ESTE ESTADO NO SE CUENTA CON GUÍA ESTATAL PARA PIPC, SE TOMA LA GUÍA FEDERAL
                                        DEL SINAPROC.
                                    </p>
                                </div>
                            ) : (
                                <p className="text-xs text-gray-400 italic text-right">Fuente: {guideData.titulo}</p>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* SECCIÓN 2: TABLA NORMATIVA JERÁRQUICA */}
            <div>
                <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <span>📋</span> Matriz de Cumplimiento Normativo (Leyes y Reglamentos)
                </h3>
                <div className="border border-gray-300 rounded-lg overflow-hidden shadow-sm">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-slate-800 text-white">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider w-1/4">
                                    Jerarquía / Norma
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider w-3/4">
                                    Puntos de Inspección y Fundamento
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {normsOnly.map((norm, index) => (
                                <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                    <td className="px-6 py-4 align-top">
                                        <div className="flex flex-col">
                                            <span className="font-bold text-slate-800 text-sm">{norm.norma}</span>
                                            <span className="text-xs text-slate-500 mt-1">{norm.titulo}</span>
                                            {/* Badge de Nivel */}
                                            <span
                                                className={`mt-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium w-fit
                                                ${
                                                    norm.norma.includes('NIVEL FEDERAL') ||
                                                    norm.norma.includes('Constitución')
                                                        ? 'bg-red-100 text-red-800'
                                                        : norm.norma.includes('NIVEL ESTATAL')
                                                          ? 'bg-orange-100 text-orange-800'
                                                          : norm.norma.includes('NIVEL MUNICIPAL')
                                                            ? 'bg-yellow-100 text-yellow-800'
                                                            : 'bg-green-100 text-green-800'
                                                }`}
                                            >
                                                {norm.norma.includes('FEDERAL')
                                                    ? 'NIVEL FEDERAL'
                                                    : norm.norma.includes('ESTATAL')
                                                      ? 'NIVEL ESTATAL'
                                                      : norm.norma.includes('MUNICIPAL')
                                                        ? 'NIVEL MUNICIPAL'
                                                        : 'NIVEL TÉCNICO (NOM)'}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <ul className="space-y-3">
                                            {norm.checks.map((point) => (
                                                <li
                                                    key={point.id}
                                                    className="flex items-start gap-3 p-2 hover:bg-gray-100 rounded transition-colors"
                                                >
                                                    <input
                                                        type="checkbox"
                                                        className="mt-1 h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 cursor-pointer"
                                                    />
                                                    <div className="flex-1">
                                                        <p className="text-sm text-gray-800 font-medium">
                                                            {point.desc}
                                                        </p>
                                                        <p className="text-xs text-blue-600 font-mono mt-0.5 font-bold">
                                                            Fundamento:{' '}
                                                            {point.art.startsWith('Art')
                                                                ? point.art
                                                                : `Art. ${point.art}`}
                                                        </p>
                                                    </div>
                                                </li>
                                            ))}
                                        </ul>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
