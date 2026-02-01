import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';
import { useAuth } from './hooks/useAuth';

// Mocks
jest.mock('./hooks/useAuth');
jest.mock('./CivilProtectForm', () => () => <div data-testid="civil-protect-form">CivilProtectForm</div>);
jest.mock('./HistoryView', () => () => <div data-testid="history-view">HistoryView</div>);
jest.mock('./components/NotificationBell', () => () => <div data-testid="notification-bell">Bell</div>);
jest.mock('./pages/LoginPage', () => ({ onSwitchToRegister }) => (
    <div data-testid="login-page">
        LoginPage <button onClick={onSwitchToRegister}>Register</button>
    </div>
));
jest.mock('./pages/RegisterPage', () => ({ onSwitchToLogin }) => (
    <div data-testid="register-page">
        RegisterPage <button onClick={onSwitchToLogin}>Login</button>
    </div>
));
// Mock AuthContext provider to avoid axios issues in real provider
jest.mock('./contexts/AuthContext', () => ({
    AuthProvider: ({ children }) => <div>{children}</div>
}));

describe('App Component Navigation', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders LoginPage when not authenticated', () => {
        useAuth.mockReturnValue({
            user: null,
            isAuthenticated: false,
            loading: false
        });

        render(<App />);

        expect(screen.getByTestId('login-page')).toBeInTheDocument();
        expect(screen.queryByTestId('civil-protect-form')).not.toBeInTheDocument();
    });

    test('switches to RegisterPage when triggered', () => {
        useAuth.mockReturnValue({
            user: null,
            isAuthenticated: false,
            loading: false
        });

        render(<App />);

        // Click register button in mock Login
        fireEvent.click(screen.getByText('Register'));

        expect(screen.getByTestId('register-page')).toBeInTheDocument();
    });

    test('renders MainApp (CivilProtectForm) when authenticated', () => {
        useAuth.mockReturnValue({
            user: { name: 'Test User', role: 'user' },
            isAuthenticated: true,
            loading: false,
            logout: jest.fn()
        });

        render(<App />);

        // Should render header info
        expect(screen.getByText('Test User')).toBeInTheDocument();
        // Default tab is New Analysis (CivilProtectForm)
        expect(screen.getByTestId('civil-protect-form')).toBeInTheDocument();
        // NotificationBell should be there
        expect(screen.getByTestId('notification-bell')).toBeInTheDocument();
    });

    test('navigates between tabs', () => {
        useAuth.mockReturnValue({
            user: { name: 'Test User', role: 'user' },
            isAuthenticated: true,
            loading: false,
            logout: jest.fn()
        });

        render(<App />);

        const historyBtn = screen.getByText('Historial');
        const newBtn = screen.getByText('Nuevo Análisis');

        // Initial state
        expect(screen.getByTestId('civil-protect-form')).toBeInTheDocument();

        // Switch to History
        fireEvent.click(historyBtn);
        expect(screen.getByTestId('history-view')).toBeInTheDocument();
        expect(screen.queryByTestId('civil-protect-form')).not.toBeInTheDocument();

        // Switch back to New
        fireEvent.click(newBtn);
        expect(screen.getByTestId('civil-protect-form')).toBeInTheDocument();
    });

    test('calls logout when button clicked', () => {
        const mockLogout = jest.fn();
        useAuth.mockReturnValue({
            user: { name: 'Test User', role: 'user' },
            isAuthenticated: true,
            loading: false,
            logout: mockLogout
        });

        render(<App />);

        const logoutBtn = screen.getByText('Cerrar Sesión');
        fireEvent.click(logoutBtn);

        expect(mockLogout).toHaveBeenCalled();
    });
});
