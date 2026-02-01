import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import PropertyInfoStep from './PropertyInfoStep';

describe('PropertyInfoStep Component', () => {
    const mockFormData = {
        tipoInmueble: 'Hotel',
        m2Construccion: '',
        nivelesTotales: ''
    };
    const mockHandleChange = jest.fn();

    test('renders all inputs', () => {
        render(<PropertyInfoStep formData={mockFormData} handleInputChange={mockHandleChange} validationErrors={[]} />);

        expect(screen.getByText(/Tipo de Inmueble/i)).toBeInTheDocument();
        expect(screen.getByText(/M² Construcción/i)).toBeInTheDocument();
        expect(screen.getByRole('spinbutton', { name: '' })).toBeInTheDocument(); // m2 input (placeholder 0.00?)
    });

    test('displays validation errors when passed', () => {
        const errors = ['Error de densidad', 'Error de niveles'];
        render(
            <PropertyInfoStep formData={mockFormData} handleInputChange={mockHandleChange} validationErrors={errors} />
        );

        expect(screen.getByText(/DETECCIÓN DE INCOHERENCIA PERICIAL/i)).toBeInTheDocument();
        expect(screen.getByText('Error de densidad')).toBeInTheDocument();
    });
});
