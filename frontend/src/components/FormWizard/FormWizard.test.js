import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import FormWizard from './FormWizard';

// Mock Hooks
jest.mock('../../hooks/useFormData', () => ({
    useFormData: () => ({
        formData: {
            tipoInmueble: 'Hotel',
            m2Construccion: '',
            hasGas: false
        },
        setFormData: jest.fn(),
        selectedState: '',
        setSelectedState: jest.fn(),
        selectedMuni: '',
        setSelectedMuni: jest.fn(),
        handleInputChange: jest.fn()
    })
}));

jest.mock('../../hooks/useFormValidation', () => ({
    useFormValidation: () => ({
        validationErrors: [],
        setValidationErrors: jest.fn(),
        validateInputs: jest.fn(() => true)
    })
}));

jest.mock('../../hooks/useAnalysisSubmit', () => ({
    useAnalysisSubmit: () => ({
        loading: false,
        submitAnalysis: jest.fn()
    })
}));

// Mock Catalog Data Hook inside LocationStep
jest.mock('../../hooks/useCatalogData', () => ({
    useCatalogData: () => ({
        catalogData: { estados: [{ nombre: 'CDMX', municipios: [{ nombre: 'Coyoacan', metadata: {} }] }] },
        loadingCatalog: false,
        getMuniMetadata: jest.fn()
    })
}));

describe('FormWizard Integration', () => {
    test('renders Step 1 (Location) initially', () => {
        render(<FormWizard />);
        expect(screen.getByText(/Ubicación del Inmueble/i)).toBeInTheDocument();
        expect(screen.getByText(/Estado/i)).toBeInTheDocument();
        expect(screen.getByText('1')).toHaveClass('bg-indigo-600'); // Step 1 active
    });

    test('validates Step 1 before proceeding', () => {
        // Mock alert
        window.alert = jest.fn();

        render(<FormWizard />);
        const nextBtn = screen.getByText(/Siguiente/i);

        // Try next without selection
        fireEvent.click(nextBtn);
        expect(window.alert).toHaveBeenCalledWith('Por favor seleccione Estado y Municipio.');

        // Step shouldn't change (check Indicator still step 1)
        expect(screen.getByText('1')).toHaveClass('bg-indigo-600');
    });

    // Note: To test success path, we'd need to manipulate the mocked hook return values
    // which is harder with jest.mock factory pattern here.
    // Usually we'd mock the hook implementation per test or use a more flexible mock.
});
