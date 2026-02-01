import React, { createContext, useState, useEffect, useCallback } from 'react';
import axios from '../utils/axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Cargar usuario desde localStorage al iniciar
    useEffect(() => {
        const loadUser = async () => {
            const token = localStorage.getItem('access_token');
            const storedUser = localStorage.getItem('user');

            if (token && storedUser) {
                try {
                    // Verificar que el token sigue siendo válido
                    // axios instance interceptor will attach token
                    const response = await axios.get('/auth/me');
                    setUser(response.data);
                } catch (err) {
                    // Token inválido o expirado
                    console.error('Session validation failed:', err);
                    // No need to manually clear if axios interceptor handles 401,
                    // but we do it for safety/UI state sync
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');
                    setUser(null);
                }
            }
            setLoading(false);
        };

        loadUser();
    }, []);

    // Login
    const login = useCallback(async (email, password) => {
        setError(null);
        try {
            const response = await axios.post('/auth/login', {
                email,
                password
            });

            const { access_token, refresh_token, user: userData } = response.data;

            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            localStorage.setItem('user', JSON.stringify(userData));

            setUser(userData);
            return { success: true };
        } catch (err) {
            const errorMsg = err.response?.data?.detail || 'Error al iniciar sesión';
            setError(errorMsg);
            return { success: false, error: errorMsg };
        }
    }, []);

    // Register
    const register = useCallback(async (email, name, password, role = 'consultor') => {
        setError(null);
        try {
            const response = await axios.post('/auth/register', {
                email,
                name,
                password,
                role
            });

            const { access_token, refresh_token, user: userData } = response.data;

            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            localStorage.setItem('user', JSON.stringify(userData));

            setUser(userData);
            return { success: true };
        } catch (err) {
            const errorMsg = err.response?.data?.detail || 'Error al registrarse';
            setError(errorMsg);
            return { success: false, error: errorMsg };
        }
    }, []);

    // Logout
    const logout = useCallback(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        setUser(null);
        // Optional: Call logout endpoint if exists
    }, []);

    // Refresh token manually if needed (exposed but axios handles it too)
    const refreshToken = useCallback(async () => {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) {
            logout();
            return false;
        }

        try {
            const response = await axios.post('/auth/refresh', {
                refresh_token: refresh
            });

            const { access_token, refresh_token: newRefreshToken, user: userData } = response.data;

            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', newRefreshToken);
            localStorage.setItem('user', JSON.stringify(userData));

            setUser(userData);
            return true;
        } catch (err) {
            console.error('Error refreshing token:', err);
            logout();
            return false;
        }
    }, [logout]);

    const value = {
        user,
        loading,
        error,
        login,
        register,
        logout,
        refreshToken,
        isAuthenticated: !!user
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
