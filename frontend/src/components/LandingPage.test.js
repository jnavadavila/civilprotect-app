import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LandingPage from '../components/LandingPage';

describe('LandingPage Component', () => {
    test('renders landing page correctly', () => {
        render(<LandingPage onLogin={() => {}} />);

        const mainTitles = screen.getAllByText(/GIRRD PC/i);
        expect(mainTitles.length).toBeGreaterThan(0);

        const accessTitles = screen.getAllByText(/Acceso al Sistema/i);
        expect(accessTitles[0]).toBeInTheDocument();
    });

    test('calls onLogin with ADMIN role when admin credentials provided', () => {
        const handleLogin = jest.fn();
        render(<LandingPage onLogin={handleLogin} />);

        const userInput = screen.getByPlaceholderText(/Ej. admin/i);
        const passInput = screen.getByPlaceholderText(/••••••••/i);
        const submitBtn = screen.getByRole('button', { name: /Ingresar/i });

        fireEvent.change(userInput, { target: { value: 'admin' } });
        fireEvent.change(passInput, { target: { value: 'admin123' } });
        fireEvent.click(submitBtn);

        expect(handleLogin).toHaveBeenCalledWith('ADMIN');
    });

    test('calls onLogin with USER role when guest credentials (empty) provided', () => {
        const handleLogin = jest.fn();
        render(<LandingPage onLogin={handleLogin} />);

        const submitBtn = screen.getByRole('button', { name: /Ingresar/i });
        fireEvent.click(submitBtn);

        expect(handleLogin).toHaveBeenCalledWith('USER');
    });

    test('shows alert on invalid credentials', () => {
        const handleLogin = jest.fn();
        const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});
        render(<LandingPage onLogin={handleLogin} />);

        const userInput = screen.getByPlaceholderText(/Ej. admin/i);
        const passInput = screen.getByPlaceholderText(/••••••••/i);
        const submitBtn = screen.getByRole('button', { name: /Ingresar/i });

        fireEvent.change(userInput, { target: { value: 'wrong' } });
        fireEvent.change(passInput, { target: { value: 'wrong' } });
        fireEvent.click(submitBtn);

        expect(handleLogin).not.toHaveBeenCalled();
        expect(alertMock).toHaveBeenCalled();
        alertMock.mockRestore();
    });
});
