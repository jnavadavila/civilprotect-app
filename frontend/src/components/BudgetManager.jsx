import React, { useState, useEffect } from 'react';

export default function BudgetManager({ initialData, onUpdate }) {
    const [items, setItems] = useState([]);
    const [grandTotal, setGrandTotal] = useState(0);

    // Cargar datos iniciales del backend
    useEffect(() => {
        if (initialData) {
            setItems(initialData);
        }
    }, [initialData]);

    // Recalcular total cada vez que cambia un item
    useEffect(() => {
        const total = items.reduce((acc, item) => acc + item.cantidad * item.precio_unitario, 0);
        setGrandTotal(total);
        // Enviar datos actualizados al componente padre (para imprimir PDF)
        if (onUpdate) onUpdate(items, total);
    }, [items, onUpdate]);

    const handleChange = (id, field, value) => {
        const newItems = items.map((item) => {
            if (item.id === id) {
                return { ...item, [field]: parseFloat(value) || 0 };
            }
            return item;
        });
        setItems(newItems);
    };

    const addItem = () => {
        const newItem = {
            id: Date.now(),
            categoria: 'Extra',
            concepto: 'Nuevo Concepto...',
            cantidad: 1,
            precio_unitario: 0,
            norma: 'N/A'
        };
        setItems([...items, newItem]);
    };

    const deleteItem = (id) => {
        setItems(items.filter((item) => item.id !== id));
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-lg mt-8">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-slate-800">💰 Análisis de Costos y Presupuesto (Editable)</h3>
                <button
                    onClick={addItem}
                    className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded hover:bg-green-200"
                >
                    + Agregar Fila
                </button>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full text-sm text-left">
                    <thead className="bg-slate-100 text-slate-600 uppercase font-bold">
                        <tr>
                            <th className="px-4 py-3">Norma</th>
                            <th className="px-4 py-3">Concepto</th>
                            <th className="px-4 py-3 w-24">Cant.</th>
                            <th className="px-4 py-3 w-32">P. Unitario ($)</th>
                            <th className="px-4 py-3 w-32">Importe</th>
                            <th className="px-4 py-3 w-10"></th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {items.map((item) => (
                            <tr key={item.id} className="hover:bg-slate-50 transition">
                                <td className="px-4 py-2">
                                    <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-0.5 rounded">
                                        {item.norma}
                                    </span>
                                </td>
                                <td className="px-4 py-2">
                                    <input
                                        type="text"
                                        value={item.concepto}
                                        onChange={(e) => handleChange(item.id, 'concepto', e.target.value)}
                                        className="w-full border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 border p-1"
                                    />
                                </td>
                                <td className="px-4 py-2">
                                    <input
                                        type="number"
                                        value={item.cantidad}
                                        onChange={(e) => handleChange(item.id, 'cantidad', e.target.value)}
                                        className="w-full border-gray-300 rounded focus:ring-blue-500 border p-1 text-center font-bold"
                                    />
                                </td>
                                <td className="px-4 py-2">
                                    <input
                                        type="number"
                                        value={item.precio_unitario}
                                        onChange={(e) => handleChange(item.id, 'precio_unitario', e.target.value)}
                                        className="w-full border-gray-300 rounded focus:ring-blue-500 border p-1 text-right"
                                    />
                                </td>
                                <td className="px-4 py-2 text-right font-bold text-slate-700">
                                    $
                                    {(item.cantidad * item.precio_unitario).toLocaleString('es-MX', {
                                        minimumFractionDigits: 2
                                    })}
                                </td>
                                <td className="px-4 py-2 text-center">
                                    <button
                                        onClick={() => deleteItem(item.id)}
                                        className="text-red-400 hover:text-red-600 font-bold"
                                    >
                                        ×
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                    <tfoot className="bg-slate-100 font-bold text-slate-800">
                        <tr>
                            <td colSpan="4" className="px-4 py-3 text-right">
                                TOTAL ESTIMADO DE IMPLEMENTACIÓN:
                            </td>
                            <td className="px-4 py-3 text-right text-lg text-blue-700">
                                ${grandTotal.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                            </td>
                            <td></td>
                        </tr>
                    </tfoot>
                </table>
            </div>

            <p className="text-xs text-gray-500 mt-2">
                * Edite las cantidades y precios unitarios según cotizaciones reales de proveedores locales.
            </p>
        </div>
    );
}
