import React from 'react';

const IndicatorButton = ({ label, active, color, icon }) => (
    <div
        className={`flex flex-col items-center justify-center p-3 h-28 rounded-xl border-2 transition-all duration-300 ${active ? `bg-${color}-50 border-${color}-500 shadow-md scale-105` : 'bg-slate-50 border-slate-200 opacity-60 grayscale'}`}
    >
        <div
            className={`mb-2 transform transition-transform duration-500 ${active ? `text-${color}-600 scale-110` : 'text-slate-400'}`}
        >
            {icon}
        </div>
        <span
            className={`font-bold text-center text-[10px] uppercase tracking-wider leading-tight ${active ? `text-${color}-800` : 'text-slate-400'}`}
        >
            {label}
        </span>
        <div
            className={`h-1.5 w-1.5 rounded-full mt-2 ${active ? `bg-${color}-500 animate-pulse` : 'bg-slate-300'}`}
        ></div>
    </div>
);

export default IndicatorButton;
