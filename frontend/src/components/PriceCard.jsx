import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import clsx from 'clsx';

// Type definitions for props would be here if TS
// props: { title, price, change, isUp, color, icon }

// Simulated sparkline data
const generateSparkData = () => {
    return Array.from({ length: 20 }, (_, i) => ({
        value: 50 + Math.random() * 20
    }));
};

const PriceCard = ({ title, price, change, isUp, colorCode, icon }) => {
    const [flash, setFlash] = useState(null);
    const prevPriceRef = useRef(price);
    const [sparkData, setSparkData] = useState(generateSparkData());

    useEffect(() => {
        if (prevPriceRef.current !== price) {
            if (isUp) setFlash('green');
            else setFlash('red');

            const timer = setTimeout(() => setFlash(null), 500);
            prevPriceRef.current = price;

            // Update sparkline on price change
            setSparkData(prev => [...prev.slice(1), { value: 50 + Math.random() * 20 }]);

            return () => clearTimeout(timer);
        }
    }, [price, isUp]);

    // Determine specific styles based on metal type
    const isGold = title.includes('黃金') || title.includes('Gold');
    // Gradient border logic: Gold gets yellow/orange, Silver gets white/blue
    const borderClass = isGold
        ? "border-yellow-500/30 group-hover:border-yellow-400/50"
        : "border-slate-400/30 group-hover:border-slate-200/50";

    const shadowClass = isGold
        ? "shadow-[0_0_30px_-5px_rgba(251,191,36,0.15)] group-hover:shadow-[0_0_40px_-5px_rgba(251,191,36,0.3)]"
        : "shadow-[0_0_30px_-5px_rgba(226,232,240,0.15)] group-hover:shadow-[0_0_40px_-5px_rgba(226,232,240,0.3)]";

    const chartColor = isGold ? "#fbbf24" : "#e2e8f0";

    return (
        <div className={clsx(
            "relative overflow-hidden rounded-2xl p-6 group transition-all duration-300 bg-slate-900/60 backdrop-blur-xl border",
            borderClass,
            shadowClass
        )}>

            {/* Dynamic Background Flash */}
            <AnimatePresence>
                {flash && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 0.15 }}
                        exit={{ opacity: 0 }}
                        className={clsx(
                            "absolute inset-0 pointer-events-none z-0",
                            flash === 'green' ? "bg-emerald-500" : "bg-rose-500"
                        )}
                    />
                )}
            </AnimatePresence>

            <div className="relative z-10 grid grid-cols-2 gap-4 h-full">
                {/* Left Side: Info */}
                <div className="flex flex-col justify-between">
                    <div className="flex items-center gap-2">
                        {icon}
                        <span className={clsx("font-bold text-sm tracking-widest", isGold ? "text-yellow-100" : "text-slate-100")}>
                            {title}
                        </span>
                    </div>

                    <div>
                        <div className={clsx("text-4xl font-bold tracking-tight mb-2 tabular-nums", colorCode)}>
                            <span className="text-xl opacity-50 mr-1">NT$</span>{price}
                        </div>

                        <div className={clsx(
                            "inline-flex items-center gap-1 font-bold text-sm",
                            isUp ? "text-neon-green" : "text-neon-red"
                        )}>
                            {isUp ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                            <span>{change}</span>
                        </div>
                    </div>
                </div>

                {/* Right Side: Sparkline */}
                <div className="h-full min-h-[80px] w-full flex items-end opacity-80 group-hover:opacity-100 transition-opacity">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={sparkData}>
                            <defs>
                                <linearGradient id={`gradient-${title}`} x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={chartColor} stopOpacity={0.3} />
                                    <stop offset="95%" stopColor={chartColor} stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <Area
                                type="monotone"
                                dataKey="value"
                                stroke={chartColor}
                                strokeWidth={2}
                                fill={`url(#gradient-${title})`}
                                isAnimationActive={false}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Top light reflection effect */}
            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-50"></div>
        </div>
    );
};

export default PriceCard;
