import React from 'react';
import 'jest-canvas-mock';
import { render, screen, fireEvent } from '@testing-library/react';
import SignaturePad from '../components/SignaturePad';

// Refuerzo del mock de canvas
beforeAll(() => {
    HTMLCanvasElement.prototype.getContext = jest.fn(() => ({
        beginPath: jest.fn(),
        moveTo: jest.fn(),
        lineTo: jest.fn(),
        stroke: jest.fn(),
        closePath: jest.fn(),
        clearRect: jest.fn(),
        lineCap: 'round',
        lineJoin: 'round',
        strokeStyle: '#000',
        lineWidth: 1
    }));
    HTMLCanvasElement.prototype.toDataURL = jest.fn(() => 'data:image/png;base64,mock');

    // Mock getBoundingClientRect
    HTMLCanvasElement.prototype.getBoundingClientRect = jest.fn(() => ({
        width: 400,
        height: 200,
        top: 0,
        left: 0,
        bottom: 200,
        right: 400
    }));
});

describe('SignaturePad Component', () => {
    test('renders correctly', () => {
        render(<SignaturePad onSave={() => {}} onCancel={() => {}} />);
        expect(screen.getByText(/Firma Digital/i)).toBeInTheDocument();
        expect(screen.getByText(/Firmar aqu./i)).toBeInTheDocument(); // Regex . match i or í
    });

    test('enables save button after drawing', () => {
        render(<SignaturePad onSave={() => {}} onCancel={() => {}} />);

        // Buscar el canvas. Al usar jest-canvas-mock, el canvas existe.
        // A veces getByRole img funciona si tiene accessible name, si no, querySelector
        const canvas = document.querySelector('canvas');
        const saveButton = screen.getByText(/Aceptar y Firmar/i);

        // Inicialmente deshabilitado
        expect(saveButton).toBeDisabled();

        // Simular dibujo
        fireEvent.mouseDown(canvas, { nativeEvent: { clientX: 10, clientY: 10 } });
        fireEvent.mouseMove(canvas, { nativeEvent: { clientX: 20, clientY: 20 } });
        fireEvent.mouseUp(canvas);

        // Debería estar habilitado
        expect(saveButton).toBeEnabled();
    });

    test('calls onSave with data URL', () => {
        const handleSave = jest.fn();
        render(<SignaturePad onSave={handleSave} onCancel={() => {}} />);

        const canvas = document.querySelector('canvas');
        const saveButton = screen.getByText(/Aceptar y Firmar/i);

        // Dibujar
        fireEvent.mouseDown(canvas, { nativeEvent: { clientX: 10, clientY: 10 } });
        fireEvent.mouseMove(canvas, { nativeEvent: { clientX: 20, clientY: 20 } });
        fireEvent.mouseUp(canvas);

        // Guardar
        fireEvent.click(saveButton);

        // canvas.toDataURL es mockeado por jest-canvas-mock
        expect(handleSave).toHaveBeenCalledWith(expect.stringContaining('data:image/png'));
    });

    test('clears canvas and disables save button', () => {
        render(<SignaturePad onSave={() => {}} onCancel={() => {}} />);

        const canvas = document.querySelector('canvas');
        const saveButton = screen.getByText(/Aceptar y Firmar/i);
        const clearButton = screen.getByText(/Borrar/i);

        // Dibujar
        fireEvent.mouseDown(canvas, { nativeEvent: { clientX: 10, clientY: 10 } });
        fireEvent.mouseMove(canvas, { nativeEvent: { clientX: 20, clientY: 20 } });
        fireEvent.mouseUp(canvas);

        expect(saveButton).toBeEnabled();

        // Borrar
        fireEvent.click(clearButton);

        expect(saveButton).toBeDisabled();
    });
});
