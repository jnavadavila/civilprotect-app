import React from 'react';

const PropertyInfoStep = ({ formData, handleInputChange, validationErrors }) => {
    return (
        <div className="space-y-6 animate-fadeIn">
            <h3 className="text-xl font-semibold text-slate-700 border-b pb-2">Datos del Inmueble</h3>

            {/* ALERTA DE ERRORES DE VALIDACIÓN */}
            {validationErrors && validationErrors.length > 0 && (
                <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg animate-pulse">
                    <h3 className="text-red-800 font-bold flex items-center gap-2">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                            ></path>
                        </svg>
                        DETECCIÓN DE INCOHERENCIA PERICIAL
                    </h3>
                    <ul className="list-disc list-inside text-red-700 mt-2">
                        {validationErrors.map((err, idx) => (
                            <li key={idx} className="font-medium">
                                {err}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            <div className="bg-slate-50 p-6 rounded-lg border border-slate-200">
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 flex items-center gap-2">
                        <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                            ></path>
                        </svg>
                        Tipo de Inmueble
                    </label>
                    <select
                        name="tipoInmueble"
                        className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                        value={formData.tipoInmueble}
                        onChange={handleInputChange}
                    >
                        <option value="Hotel">Hotel</option>
                        <option value="Hospital">Hospital</option>
                        <option value="Plaza Comercial">Plaza Comercial</option>
                        <option value="Restaurante">Restaurante</option>
                        <option value="Oficina Corporativa">Oficina Corporativa</option>
                        <option value="Nave Industrial">Nave Industrial</option>
                        <option value="Call center">Call Center</option>
                        <option value="Terminal de Pasajeros">Terminal de Pasajeros (Aeropuerto)</option>
                        <option value="Hangar">Hangar</option>
                    </select>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                        <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
                                ></path>
                            </svg>
                            M² Construcción
                        </label>
                        <input
                            name="m2Construccion"
                            type="number"
                            className="w-full p-2 border rounded"
                            placeholder="0.00"
                            value={formData.m2Construccion}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div>
                        <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                                ></path>
                            </svg>
                            Niveles Totales
                        </label>
                        <input
                            name="nivelesTotales"
                            type="number"
                            className="w-full p-2 border rounded"
                            placeholder="Inc. deprimidos"
                            value={formData.nivelesTotales}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div>
                        <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                                ></path>
                            </svg>
                            Aforo Máximo
                        </label>
                        <input
                            name="aforoMax"
                            type="number"
                            className="w-full p-2 border rounded"
                            placeholder="Real"
                            value={formData.aforoMax}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div>
                        <label className="text-xs font-bold text-blue-600 uppercase flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                ></path>
                            </svg>
                            Aforo Autorizado
                        </label>
                        <input
                            name="aforoAutorizado"
                            type="number"
                            className="w-full p-2 border border-blue-200 bg-blue-50 rounded"
                            placeholder="Permiso/Licencia"
                            value={formData.aforoAutorizado}
                            onChange={handleInputChange}
                        />
                    </div>
                    <div>
                        <label className="text-xs font-bold text-gray-500 uppercase flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                                ></path>
                            </svg>
                            Trabajadores
                        </label>
                        <input
                            name="numTrabajadores"
                            type="number"
                            className="w-full p-2 border rounded"
                            placeholder="Plantilla total"
                            value={formData.numTrabajadores}
                            onChange={handleInputChange}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PropertyInfoStep;
