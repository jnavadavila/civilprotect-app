import React, { useRef, useState, useEffect } from 'react';

const SignaturePad = (props) => {
    const { onSave, onCancel } = props;
    const canvasRef = useRef(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [hasSignature, setHasSignature] = useState(false);

    // Configuración del Contexto
    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.strokeStyle = '#000044'; // Azul Oscuro Tinta
        ctx.lineWidth = 2; // Grosor de pluma fina
    }, []);

    // --- MOUSE EVENTS ---
    const startDrawing = (e) => {
        const { offsetX, offsetY } = getCoordinates(e);
        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return;
        ctx.beginPath();
        ctx.moveTo(offsetX, offsetY);
        setIsDrawing(true);
    };

    const draw = (e) => {
        if (!isDrawing) return;
        const { offsetX, offsetY } = getCoordinates(e);
        const ctx = canvasRef.current.getContext('2d');
        if (!ctx) return;
        ctx.lineTo(offsetX, offsetY);
        ctx.stroke();
        setHasSignature(true);
    };

    const stopDrawing = () => {
        const ctx = canvasRef.current.getContext('2d');
        if (ctx) ctx.closePath();
        setIsDrawing(false);
    };

    // --- TOUCH EVENTS (Móvil/Tablet) ---
    // Helper para obtener coordenadas relativas al canvas
    const getCoordinates = (e) => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        if (!rect) return { offsetX: 0, offsetY: 0 };

        let clientX, clientY;

        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        } else {
            clientX = e.clientX || (e.nativeEvent && e.nativeEvent.clientX);
            clientY = e.clientY || (e.nativeEvent && e.nativeEvent.clientY);
        }

        return {
            offsetX: clientX - rect.left,
            offsetY: clientY - rect.top
        };
    };

    // Wrappers para Touch
    const startDrawingTouch = (e) => {
        e.preventDefault(); // Evitar scroll
        startDrawing(e);
    };

    const drawTouch = (e) => {
        e.preventDefault();
        draw(e);
    };

    // --- ACCIONES ---
    const clearCanvas = () => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
        setHasSignature(false);
    };

    const handleSave = () => {
        if (!hasSignature) return;
        const canvas = canvasRef.current;
        const dataUrl = canvas.toDataURL('image/png');
        onSave(dataUrl);
    };

    // [MODIFICADO] Renderizado Condicional: Modal vs Embebido
    const content = (
        <div
            className={`bg-white rounded-xl ${!props.isEmbedded ? 'shadow-2xl p-6 w-full max-w-lg' : 'p-2 w-full h-full'}`}
        >
            {!props.isEmbedded && (
                <div className="text-center mb-4">
                    <h3 className="text-xl font-bold text-slate-800">Firma Digital (Táctil)</h3>
                    <p className="text-sm text-slate-500">Dibuja tu firma en el recuadro usando tu dedo o mouse.</p>
                </div>
            )}

            <div
                className={`border-2 border-dashed border-slate-300 rounded-lg mb-2 bg-slate-50 relative ${props.isEmbedded ? 'h-32' : ''}`}
            >
                <canvas
                    ref={canvasRef}
                    width={props.width || 400}
                    height={props.height || 200}
                    className="w-full touch-none cursor-crosshair bg-white rounded-lg"
                    onMouseDown={startDrawing}
                    onMouseMove={draw}
                    onMouseUp={stopDrawing}
                    onMouseLeave={stopDrawing}
                    onTouchStart={startDrawingTouch}
                    onTouchMove={drawTouch}
                    onTouchEnd={stopDrawing}
                />
                {!hasSignature && (
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
                        <span className={`text-slate-400 font-cursive ${props.isEmbedded ? 'text-xl' : 'text-4xl'}`}>
                            Firmar aquí
                        </span>
                    </div>
                )}
            </div>

            <div className={`flex gap-2 justify-end ${props.isEmbedded ? 'text-xs' : ''}`}>
                <button
                    onClick={clearCanvas}
                    className={`px-3 py-1 text-red-600 bg-red-50 hover:bg-red-100 rounded transition-colors ${props.isEmbedded ? 'text-xs' : 'text-sm'}`}
                >
                    Borrar
                </button>
                {!props.isEmbedded && (
                    <button
                        onClick={onCancel}
                        className="px-4 py-2 text-sm text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors border border-slate-200"
                    >
                        Cancelar
                    </button>
                )}
                {/* En modo embebido, el guardado puede ser manual o automático, dejamos el botón por claridad */}
                <button
                    onClick={handleSave}
                    disabled={!hasSignature}
                    className={`px-4 py-1 font-bold text-white rounded transition-all ${
                        hasSignature ? 'bg-blue-600 hover:bg-blue-700 shadow-sm' : 'bg-slate-300 cursor-not-allowed'
                    } ${props.isEmbedded ? 'text-xs' : 'text-sm'}`}
                >
                    {props.isEmbedded ? 'Guardar' : 'Aceptar y Firmar'}
                </button>
            </div>
            {props.footerContent}
        </div>
    );

    if (props.isEmbedded) {
        return content;
    }

    return <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">{content}</div>;
};

export default SignaturePad;
