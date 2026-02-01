import React, { useState, Suspense, lazy } from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { AnalysisProvider } from './contexts/AnalysisContext';
import { useAuth } from './hooks/useAuth';
import { useAnalysis } from './hooks/useAnalysis';
import NotificationBell from './components/NotificationBell';

// Lazy Loading de Componentes Mayores
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const CivilProtectForm = lazy(() => import('./CivilProtectForm'));
const HistoryView = lazy(() => import('./HistoryView'));

// Loading Fallback Component
const LoadingSpinner = () => (
    <div className="flex items-center justify-center h-full min-h-[400px]">
        <div className="flex flex-col items-center">
            <svg className="animate-spin h-10 w-10 text-blue-600 mb-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-gray-500 font-medium">Cargando módulo...</p>
        </div>
    </div>
);

function MainApp() {
    const { user, logout, loading } = useAuth();
    const { currentAnalysis, loadAnalysis, clearCurrentAnalysis } = useAnalysis();
    const [activeTab, setActiveTab] = useState('new');

    const handleLoadAnalysis = async (id) => {
        await loadAnalysis(id);
        setActiveTab('new');
    };

    const handleNewAnalysis = () => {
        clearCurrentAnalysis();
        setActiveTab('new');
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
                <div className="text-center">
                    <LoadingSpinner />
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-100 py-12">
            <header className="bg-white shadow-sm mb-8 py-4 px-8 flex justify-between items-center fixed top-0 w-full z-50">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <img src="/logo_lunaya.png" alt="LunaYa IP" className="h-12 w-auto object-contain" />
                        <div className="flex leading-none tracking-tighter">
                            <span className="text-5xl font-black text-gray-600">L</span>
                            <span className="text-5xl font-black text-orange-500">Y</span>
                        </div>
                    </div>
                    <div className="flex flex-col ml-2 border-l-2 border-gray-200 pl-4">
                        <span className="text-xl font-bold text-slate-800 leading-none">GIRRD PC <span className="text-blue-600">AI</span></span>
                        <span className="text-[10px] text-gray-500 font-medium uppercase">Sistema Experto en análisis normativo para PIPC en GIRRD PC</span>
                    </div>
                </div>
                <div className="flex items-center gap-6">
                    <NotificationBell />
                    <div className="flex flex-col items-end">
                        <div className="flex items-center gap-3">
                            <div className="text-right">
                                <p className="text-sm font-bold text-gray-700">{user?.name}</p>
                                <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
                            </div>
                            <button
                                onClick={logout}
                                className="text-sm text-red-500 hover:text-red-700 font-medium px-4 py-2 rounded-lg hover:bg-red-50 transition-all"
                            >
                                Cerrar Sesión
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <div className="mt-20 mb-4 max-w-7xl mx-auto px-6">
                <div className="flex gap-2 border-b-2 border-gray-200">
                    <button
                        onClick={handleNewAnalysis}
                        className={`px-6 py-3 font-semibold transition-all border-b-2 ${activeTab === 'new' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                    >
                        Nuevo Análisis
                    </button>
                    <button
                        onClick={() => setActiveTab('history')}
                        className={`px-6 py-3 font-semibold transition-all border-b-2 ${activeTab === 'history' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                    >
                        Historial
                    </button>
                </div>
            </div>

            <div className="mt-4">
                <Suspense fallback={<LoadingSpinner />}>
                    {activeTab === 'new' ? (
                        <CivilProtectForm
                            userRole={user?.role}
                            initialData={currentAnalysis?.input_data || currentAnalysis}
                        />
                    ) : (
                        <HistoryView onLoadAnalysis={handleLoadAnalysis} />
                    )}
                </Suspense>
            </div>
        </div>
    );
}

function AuthWrapper() {
    const { user, isAuthenticated, loading } = useAuth();
    const [showRegister, setShowRegister] = useState(false);

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-900 flex items-center justify-center">
                <LoadingSpinner />
            </div>
        );
    }

    if (!isAuthenticated || !user) {
        return (
            <Suspense fallback={<LoadingSpinner />}>
                {showRegister ?
                    <RegisterPage onSwitchToLogin={() => setShowRegister(false)} /> :
                    <LoginPage onSwitchToRegister={() => setShowRegister(true)} />
                }
            </Suspense>
        );
    }

    return (
        <AnalysisProvider>
            <MainApp />
        </AnalysisProvider>
    );
}

function App() {
    return (
        <AuthProvider>
            <AuthWrapper />
        </AuthProvider>
    );
}

export default App;
