import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import BudgetManager from '../components/BudgetManager';

// Mock de Intl.NumberFormat para consistencia en imports
const mockNumberFormat = new Intl.NumberFormat('es-MX', { minimumFractionDigits: 2 });

const mockItems = [
    {
        id: 1,
        categoria: 'Extinción',
        concepto: 'Extintor PQS',
        cantidad: 2,
        precio_unitario: 500,
        norma: 'NOM-002'
    },
    {
        id: 2,
        categoria: 'Señalización',
        concepto: 'Señal Salida',
        cantidad: 5,
        precio_unitario: 100,
        norma: 'NOM-026'
    }
];

describe('BudgetManager Component', () => {
    test('renders with initial items', () => {
        render(<BudgetManager initialData={mockItems} onUpdate={() => {}} />);

        // Regex para evitar problemas de encoding con tildes
        expect(screen.getByText(/An.lisis de Costos y Presupuesto/i)).toBeInTheDocument();
        expect(screen.getByDisplayValue('Extintor PQS')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Señal Salida')).toBeInTheDocument();
        expect(screen.getByDisplayValue('2')).toBeInTheDocument(); // Cantidad
        expect(screen.getByDisplayValue('500')).toBeInTheDocument(); // Precio
    });

    test('calculates and displays grand total correctly', () => {
        render(<BudgetManager initialData={mockItems} onUpdate={() => {}} />);

        // Items: (2*500) + (5*100) = 1000 + 500 = 1500
        const totalCell = screen.getByText('$1,500.00'); // Formateado
        expect(totalCell).toBeInTheDocument();
    });

    test('updates total when quantity changes', async () => {
        const handleUpdate = jest.fn();
        render(<BudgetManager initialData={mockItems} onUpdate={handleUpdate} />);

        // Cambiar cantidad de 2 a 3 en el primer item
        const quantityInput = screen.getByDisplayValue('2');
        fireEvent.change(quantityInput, { target: { value: '3' } });

        // Nuevo total: (3*500) + (5*100) = 1500 + 500 = 2000
        await waitFor(() => {
            expect(screen.getByText('$2,000.00')).toBeInTheDocument();
        });

        // Verificar que se llamó a onUpdate (sin importar cuantas veces) con el valor correcto al final
        expect(handleUpdate).toHaveBeenCalled();
        const lastCall = handleUpdate.mock.calls[handleUpdate.mock.calls.length - 1];
        expect(lastCall[1]).toBe(2000);
    });

    test('adds a new item', () => {
        render(<BudgetManager initialData={mockItems} onUpdate={() => {}} />);

        const addButton = screen.getByText('+ Agregar Fila');
        fireEvent.click(addButton);

        expect(screen.getByDisplayValue('Nuevo Concepto...')).toBeInTheDocument();
    });

    test('deletes an item', () => {
        render(<BudgetManager initialData={mockItems} onUpdate={() => {}} />);

        const deleteButtons = screen.getAllByText('×');
        fireEvent.click(deleteButtons[0]); // Borrar el primero

        expect(screen.queryByDisplayValue('Extintor PQS')).not.toBeInTheDocument();
        // Total debería ser solo el segundo item: 500. Hay 2 ocurrencias (item y total)
        const prices = screen.getAllByText('$500.00');
        expect(prices.length).toBeGreaterThanOrEqual(1);
    });
});
