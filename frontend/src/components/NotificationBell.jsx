import React, { useState, useEffect } from 'react';
import axios from 'axios';

const NotificationBell = () => {
    const [updates, setUpdates] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    const checkUpdates = async () => {
        try {
            const res = await axios.get(`${apiUrl}/check-updates`);
            if (res.data.status === 'success') {
                setUpdates(res.data.updates);
            }
        } catch (error) {
            console.error('Error checking updates:', error);
        }
    };

    useEffect(() => {
        checkUpdates();
        const interval = setInterval(checkUpdates, 30000); // Poll cada 30s
        return () => clearInterval(interval);
    }, []);

    const handleApprove = async (fileId) => {
        try {
            await axios.post(`${apiUrl}/approve-update`, { file_id: fileId });
            alert('✅ Inteligencia aprobada e integrada a la base de datos.');
            checkUpdates(); // Refresh
        } catch (error) {
            alert('Error aprobando update');
        }
    };

    if (updates.length === 0) return null;

    return (
        <div className="relative">
            {/* Bell Icon with Badge */}
            <button
                onClick={() => setShowModal(!showModal)}
                className="relative p-2 text-slate-800 hover:bg-slate-100 rounded-full transition-colors"
                title="Inteligencia Artificial: Nuevos Hallazgos"
            >
                <div className="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full animate-ping"></div>
                <div className="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full border-2 border-white"></div>
                <svg className="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                    ></path>
                </svg>
            </button>

            {/* Dropdown Modal */}
            {showModal && (
                <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-2xl border border-gray-200 z-50 overflow-hidden animate-fade-in origin-top-right">
                    <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-4">
                        <h3 className="text-white font-bold flex items-center gap-2">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M13 10V3L4 14h7v7l9-11h-7z"
                                ></path>
                            </svg>
                            Inteligencia Detectada ({updates.length})
                        </h3>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                        {updates.map((upd, idx) => (
                            <div key={idx} className="p-4 border-b border-gray-100 hover:bg-blue-50 transition-colors">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-0.5 rounded">
                                        {upd.document_type || 'Hallazgo'}
                                    </span>
                                    <span className="text-xs text-gray-400">
                                        {upd.municipio}, {upd.estado}
                                    </span>
                                </div>
                                <p className="text-sm font-bold text-gray-800 mb-1">
                                    {upd.requisito_nuevo || 'Actualización detectada'}
                                </p>
                                <p className="text-xs text-gray-500 mb-3">Fuente: {upd.source_url}</p>

                                <div className="flex gap-2">
                                    <button
                                        onClick={() => handleApprove(upd.file_id)}
                                        className="flex-1 bg-green-600 hover:bg-green-700 text-white text-xs font-bold py-2 rounded shadow transition-colors"
                                    >
                                        APROBAR
                                    </button>
                                    <button className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-600 text-xs font-bold py-2 rounded transition-colors">
                                        IGNORAR
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NotificationBell;
