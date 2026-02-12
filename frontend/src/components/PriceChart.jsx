import React, { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import clsx from 'clsx';

// Simulated data generator for fallback or smooth rendering
const generateData = (points = 30) => {
    return Array.from({ length: points }, (_, i) => ({
        time: `10:${i < 10 ? '0' + i : i}`,
        gold: 2020 + Math.random() * 10,
        silver: 22 + Math.random() * 1
    }));
};

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700 p-3 rounded-lg shadow-xl text-xs">
                <p className="text-slate-400 mb-1">{label}</p>
                <p className="text-yellow-400 font-mono font-bold">黃金: NT$ {payload[0].value.toLocaleString()}</p>
                <p className="text-slate-300 font-mono font-bold">白銀: NT$ {payload[1].value.toLocaleString()}</p>
            </div>
        );
    }
    return null;
};

const PriceChart = ({ historicalData, period, onPeriodChange }) => {
    // data handling ...
    const data = historicalData || generateData(50);
    const tabs = ['1D', '1W', '1M', '3M'];

    return (
        <div className="glass-card rounded-2xl p-6 h-[450px] flex flex-col relative overflow-hidden">
            <div className="flex justify-between items-center mb-6 relative z-10">
                <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
                    <span className="w-2 h-6 bg-blue-500 rounded-full"></span>
                    價格趨勢
                </h2>

                <div className="flex bg-slate-950/50 p-1 rounded-lg border border-white/5">
                    {tabs.map(tab => (
                        <button
                            key={tab}
                            onClick={() => onPeriodChange(tab)}
                            className={clsx(
                                "px-4 py-1.5 rounded-md text-xs font-bold transition-all duration-300",
                                period === tab
                                    ? "bg-blue-600 text-white shadow-lg shadow-blue-500/25"
                                    : "text-slate-400 hover:text-white hover:bg-white/5"
                            )}
                        >
                            {tab}
                        </button>
                    ))}
                </div>
            </div>

            <div className="flex-1 w-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="colorGold" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#fbbf24" stopOpacity={0.2} />
                                <stop offset="95%" stopColor="#fbbf24" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorSilver" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#e2e8f0" stopOpacity={0.2} />
                                <stop offset="95%" stopColor="#e2e8f0" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} vertical={false} />
                        <XAxis
                            dataKey="time"
                            stroke="#64748b"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            dy={10}
                        />
                        <YAxis
                            stroke="#64748b"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            domain={['auto', 'auto']}
                            dx={-10}
                        />
                        <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#fff', strokeWidth: 0.5, opacity: 0.5 }} />
                        <Area
                            type="monotone"
                            dataKey="gold"
                            stroke="#fbbf24"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorGold)"
                            activeDot={{ r: 6, fill: "#fbbf24", stroke: "#fff", strokeWidth: 2 }}
                        />
                        <Area
                            type="monotone"
                            dataKey="silver"
                            stroke="#e2e8f0"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorSilver)"
                            activeDot={{ r: 6, fill: "#e2e8f0", stroke: "#fff", strokeWidth: 2 }}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default PriceChart;
