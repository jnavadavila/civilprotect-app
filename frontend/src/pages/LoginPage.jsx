import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

export default function LoginPage({ onSwitchToRegister }) {
    const { login, error } = useAuth();
    const [credentials, setCredentials] = useState({ email: '', password: '' });
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await login(credentials.email, credentials.password);
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 z-0">
                <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 opacity-90"></div>
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/20 blur-[100px] rounded-full"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 blur-[100px] rounded-full"></div>
            </div>

            <div className="max-w-md w-full space-y-8 bg-white/10 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl relative z-10 transition-all hover:border-white/20">
                <div className="flex flex-col items-center">
                    <div className="bg-gradient-to-tr from-white/10 to-white/5 p-4 rounded-full mb-4 ring-1 ring-white/20 shadow-lg">
                        <img src="/logo_lunaya.png" alt="LunaYa IP" className="h-12 w-auto object-contain drop-shadow" />
                    </div>

                    <h2 className="text-center text-3xl font-black text-white tracking-tight">
                        Bienvenido a <span className="text-blue-400">GIRRD PC</span>
                    </h2>
                    <p className="mt-2 text-center text-sm text-slate-400">
                        Sistema Experto en Análisis Normativo
                    </p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/50 p-4 rounded-lg flex items-start gap-3" role="alert">
                            <svg className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <p className="text-sm text-red-200 font-medium">{error}</p>
                        </div>
                    )}

                    <div className="space-y-4">
                        <div className="group">
                            <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-1 ml-1 group-focus-within:text-blue-400 transition-colors">
                                Correo Electrónico
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <svg className="h-5 w-5 text-slate-500 group-focus-within:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                                    </svg>
                                </div>
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    required
                                    className="block w-full pl-10 pr-3 py-3 border border-white/10 rounded-xl leading-5 bg-white/5 text-slate-200 placeholder-slate-500 focus:outline-none focus:bg-white/10 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 sm:text-sm transition-all shadow-inner"
                                    placeholder="ejemplo@empresa.com"
                                    value={credentials.email}
                                    onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="group">
                            <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-1 ml-1 group-focus-within:text-blue-400 transition-colors">
                                Contraseña
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <svg className="h-5 w-5 text-slate-500 group-focus-within:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                    </svg>
                                </div>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    autoComplete="current-password"
                                    required
                                    className="block w-full pl-10 pr-3 py-3 border border-white/10 rounded-xl leading-5 bg-white/5 text-slate-200 placeholder-slate-500 focus:outline-none focus:bg-white/10 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 sm:text-sm transition-all shadow-inner"
                                    placeholder="••••••••"
                                    value={credentials.password}
                                    onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center justify-between">
                        <div className="text-sm">
                            <button
                                type="button"
                                onClick={onSwitchToRegister}
                                className="font-medium text-blue-400 hover:text-blue-300 transition-colors"
                            >
                                Registrar nueva cuenta
                            </button>
                        </div>
                        <div className="text-sm">
                            <a href="#" className="font-medium text-slate-400 hover:text-slate-300 transition-colors">
                                ¿Olvidaste tu contraseña?
                            </a>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-blue-500 disabled:opacity-50 settings-shadow transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
                    >
                        {isLoading ? (
                            <span className="flex items-center gap-2">
                                <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Ingresando...
                            </span>
                        ) : 'Iniciar Sesión'}
                    </button>

                    <p className="text-center text-xs text-slate-500 mt-4">
                        Protegido con encriptación de nivel bancario
                    </p>
                </form>
            </div>
        </div>
    );
}
