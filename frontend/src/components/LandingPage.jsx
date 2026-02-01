import React, { useState } from 'react';

export default function LandingPage({ onLogin }) {
    const [showLogin, setShowLogin] = useState(false);
    const [credentials, setCredentials] = useState({ user: '', pass: '' });

    const handleLogin = (e) => {
        e.preventDefault();
        // Lógica de Login Simulada (Científica/Institucional)
        if (credentials.user === 'admin' && credentials.pass === 'admin123') {
            onLogin('ADMIN');
        } else if (credentials.user === 'invitado' || credentials.user === '') {
            onLogin('USER');
        } else {
            alert('Credenciales incorrectas. Para demo use: admin/admin123 o deje en blanco para invitado.');
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex flex-col items-center justify-center relative overflow-hidden">
            {/* Fondo Abstracto "Data Science" */}
            <div className="absolute inset-0 opacity-10 pointer-events-none">
                <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <path d="M0 100 C 20 0 50 0 100 100 Z" fill="white" />
                </svg>
            </div>

            {/* Contenedor Principal */}
            <div className="bg-white/10 backdrop-blur-lg border border-white/20 p-8 rounded-2xl shadow-2xl max-w-4xl w-full mx-4 flex flex-col md:flex-row gap-8 z-10">
                {/* Lado Izquierdo: Branding */}
                <div className="flex-1 text-white flex flex-col justify-center">
                    <div className="mb-6">
                        <span className="bg-blue-500/20 text-blue-300 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-widest border border-blue-500/30">
                            LY GIRRD PC AI V3.0
                        </span>
                    </div>
                    <h1 className="text-5xl font-extrabold mb-4 leading-tight">
                        GIRRD PC <span className="text-blue-400">AI</span>
                    </h1>
                    <p className="text-blue-100 text-lg mb-6 leading-relaxed">
                        Sistema Experto en análisis normativo para PIPC en GIRRD PC.
                    </p>
                    <div className="space-y-3 text-sm text-blue-200">
                        <div className="flex items-center gap-2">
                            <span className="bg-green-500 h-2 w-2 rounded-full"></span>
                            <span>Base de Datos Legal Nacional (32 Estados)</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="bg-green-500 h-2 w-2 rounded-full"></span>
                            <span>Cálculo Pericial de Costos y Equipo</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="bg-green-500 h-2 w-2 rounded-full"></span>
                            <span>Generación de Dictámenes Jurídicos</span>
                        </div>
                    </div>
                </div>

                {/* Lado Derecho: Acceso */}
                <div className="w-full md:w-96 bg-white rounded-xl p-8 shadow-inner">
                    <h2 className="text-2xl font-bold text-slate-800 mb-6 text-center">Acceso al Sistema</h2>

                    <form onSubmit={handleLogin} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Usuario / ID</label>
                            <input
                                type="text"
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                                placeholder="Ej. admin"
                                value={credentials.user}
                                onChange={(e) => setCredentials({ ...credentials, user: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
                            <input
                                type="password"
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                                placeholder="••••••••"
                                value={credentials.pass}
                                onChange={(e) => setCredentials({ ...credentials, pass: e.target.value })}
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5"
                        >
                            Ingresar a Plataforma
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-xs text-gray-400">
                            Acceso restringido a personal certificado.
                            <br />
                            Invitados usar acceso libre.
                        </p>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="absolute bottom-4 text-slate-500 text-xs text-center w-full">
                &copy; 2024 CivilProtect AI Engine. Compliance Standard ISO/IEC 27001 conformant.
            </div>
        </div>
    );
}
