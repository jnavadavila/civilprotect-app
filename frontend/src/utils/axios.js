import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Crear instancia de axios
const axiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Interceptor de request: Auto-incluir token en cada petición
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor de response: Auto-refresh de token si expira
axiosInstance.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // Si el error es 401 y no hemos intentado refresh aún
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');

                if (!refreshToken) {
                    // No hay refresh token, limpiar items y rechazar para que AuthContext maneje el logout
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');
                    return Promise.reject(error);
                }

                // Intentar renovar el token
                const response = await axios.post(`${API_URL}/auth/refresh`, {
                    refresh_token: refreshToken
                });

                const { access_token, refresh_token: newRefreshToken, user } = response.data;

                // Actualizar tokens en localStorage
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', newRefreshToken);
                localStorage.setItem('user', JSON.stringify(user));

                // Actualizar header del request original
                originalRequest.headers.Authorization = `Bearer ${access_token}`;

                // Reintentar request original con nuevo token
                return axiosInstance(originalRequest);
            } catch (refreshError) {
                // Refresh falló, limpiar sesión y permitir que AuthContext maneje el estado
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default axiosInstance;
