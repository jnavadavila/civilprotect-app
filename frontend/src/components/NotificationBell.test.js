import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import NotificationBell from '../components/NotificationBell';

// jest.mock('axios'); // Ya no es necesario, Jest usa __mocks__/axios.js automáticamente

describe('NotificationBell Component', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders nothing when no updates', async () => {
        axios.get.mockResolvedValue({ data: { status: 'success', updates: [] } });
        const { container } = render(<NotificationBell />);

        await waitFor(() => {
            expect(axios.get).toHaveBeenCalled();
        });

        expect(container.firstChild).toBeNull();
    });

    test('renders bell and updates when data exists', async () => {
        const mockUpdates = [
            {
                file_id: '123',
                document_type: 'Reglamento Test',
                requisito_nuevo: 'Nuevo requerimiento X',
                municipio: 'Guadalajara',
                estado: 'Jalisco',
                source_url: 'http://test.com'
            }
        ];

        axios.get.mockResolvedValue({ data: { status: 'success', updates: mockUpdates } });

        render(<NotificationBell />);

        // Esperar a que el icono aparezca
        const bellButton = await screen.findByRole('button', { name: /Inteligencia Artificial/i });
        expect(bellButton).toBeInTheDocument();

        // Abrir modal
        fireEvent.click(bellButton);

        // Verificar contenido
        expect(screen.getByText(/Inteligencia Detectada/i)).toBeInTheDocument();
        expect(screen.getByText(/Nuevo requerimiento X/i)).toBeInTheDocument();
        expect(screen.getByText(/Reglamento Test/i)).toBeInTheDocument();
    });

    test('calls approve endpoint on button click', async () => {
        const mockUpdates = [
            {
                file_id: '123_abc',
                document_type: 'Reglamento'
            }
        ];

        axios.get.mockResolvedValue({ data: { status: 'success', updates: mockUpdates } });
        axios.post.mockResolvedValue({ data: { success: true } });
        const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

        render(<NotificationBell />);

        const bellButton = await screen.findByRole('button', { name: /Inteligencia Artificial/i });
        fireEvent.click(bellButton);

        const approveBtn = screen.getByText(/APROBAR/i);
        fireEvent.click(approveBtn);

        await waitFor(() => {
            expect(axios.post).toHaveBeenCalledWith(expect.stringContaining('/approve-update'), { file_id: '123_abc' });
        });

        alertMock.mockRestore();
    });
});
