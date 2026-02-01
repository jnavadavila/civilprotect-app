import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from '../pages/LoginPage';
import { useAuth } from '../hooks/useAuth';

// Mock useAuth
jest.mock('../hooks/useAuth');

describe('LoginPage Component', () => {
    const mockLogin = jest.fn();

    beforeEach(() => {
        useAuth.mockReturnValue({
            login: mockLogin,
            error: null
        });
        mockLogin.mockClear();
    });

    test('renders login form', () => {
        render(<LoginPage onSwitchToRegister={() => {}} />);

        expect(screen.getByRole('heading', { name: /Iniciar Sesión/i })).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Email/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Contraseña/i)).toBeInTheDocument();
    });

    test('calls login function on form submission', async () => {
        render(<LoginPage onSwitchToRegister={() => {}} />);

        const emailInput = screen.getByPlaceholderText(/Email/i);
        const passInput = screen.getByPlaceholderText(/Contraseña/i);
        const submitBtn = screen.getByRole('button', { name: /Entrar/i });

        fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
        fireEvent.change(passInput, { target: { value: 'password123' } });
        fireEvent.click(submitBtn);

        await waitFor(() => {
            expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
        });
    });

    test('displays error message when auth fails', () => {
        useAuth.mockReturnValue({
            login: mockLogin,
            error: 'Credenciales inválidas'
        });

        render(<LoginPage onSwitchToRegister={() => {}} />);

        expect(screen.getByText('Credenciales inválidas')).toBeInTheDocument();
    });

    test('calls onSwitchToRegister when link clicked', () => {
        const handleSwitch = jest.fn();
        render(<LoginPage onSwitchToRegister={handleSwitch} />);

        const registerLink = screen.getByText(/regístrate si no tienes cuenta/i);
        fireEvent.click(registerLink);

        expect(handleSwitch).toHaveBeenCalled();
    });
});
