import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Zap, Server } from 'lucide-react';
import { motion } from 'framer-motion';
import PriceCard from './components/PriceCard';
import PriceChart from './components/PriceChart';
import AnalysisSection from './components/AnalysisSection';
import { apiService } from './services/api';

import './App.css';

function App() {
    const [latestData, setLatestData] = useState(null);
    const [historicalData, setHistoricalData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [period, setPeriod] = useState('1M'); // 1D, 1W, 1M, 3M
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [manualAnalysis, setManualAnalysis] = useState(null);

    // Initial Data Load
    const loadData = useCallback(async () => {
        try {
            if (!latestData) setLoading(true);

            const daysMap = { '1D': 1, '1W': 7, '1M': 30, '3M': 90 };
            const days = daysMap[period] || 30;

            // Fetch data (simulated or real)
            const [latest, historical] = await Promise.all([
                apiService.getLatestData(),
                apiService.getHistoricalData(days),
            ]);

            if (latest.status === 'success') {
                setLatestData(latest.data);
            }
            if (historical.status === 'success') {
                // Transform backend data (separate arrays) to Recharts format (array of objects)
                const { timestamps, gold_prices, silver_prices, platinum_prices } = historical.data;
                if (timestamps && gold_prices && silver_prices) {
                    const formattedData = timestamps.map((time, index) => {
                        const date = new Date(time);
                        return {
                            time: date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit', hour12: false }),
                            gold: gold_prices[index],
                            silver: silver_prices[index],
                            platinum: platinum_prices ? platinum_prices[index] : null
                        };
                    });
                    setHistoricalData(formattedData);
                }
            }

            setLastUpdate(new Date());
        } catch (err) {
            console.error('Failed to load data:', err);
        } finally {
            setLoading(false);
        }
    }, [period]); // Removed latestData to prevent infinite loop

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 5000);
        return () => clearInterval(interval);
    }, [loadData]);

    const handleManualAnalysis = async () => {
        setIsAnalyzing(true);
        console.log("Triggering manual analysis...");
        try {
            const result = await apiService.triggerCollection();
            console.log("Analysis result:", result);
            if (result.status === 'success') {
                // If backend returns analysis directly, set it
                if (result.data && result.data.ai_analysis) {
                    // Update global latestData to reflect new analysis immediately
                    setLatestData(prev => ({
                        ...prev,
                        ai_analysis: result.data.ai_analysis
                    }));
                }
                await loadData();
            }
        } catch (e) {
            console.error("Analysis failed:", e);
        } finally {
            setIsAnalyzing(false);
        }
    };

    if (loading && !latestData) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-200">
                <div className="flex flex-col items-center gap-4">
                    <div className="relative">
                        <div className="w-16 h-16 border-4 border-slate-800 border-t-emerald-500 rounded-full animate-spin"></div>
                        <div className="absolute inset-0 flex items-center justify-center">
                            <Zap size={20} className="text-emerald-500 animate-pulse" />
                        </div>
                    </div>
                    <span className="font-mono text-sm tracking-widest uppercase text-slate-500">系統初始化中...</span>
                </div>
            </div>
        );
    }

    const { prices, ai_analysis } = latestData || {};

    // Format AI Analysis Content
    const formatAnalysisContent = (analysis) => {
        if (!analysis) return null;
        // If content exists (legacy), return it
        if (analysis.content) return analysis.content;

        // Concatenate structured fields
        const sections = [
            analysis.market_analysis && `### 市場分析\n${analysis.market_analysis}`,
            analysis.trend_prediction && `### 趨勢預測\n${analysis.trend_prediction}`,
            analysis.investment_advice && `### 投資建議\n${analysis.investment_advice}`,
            analysis.risk_warning && `### 風險提示\n${analysis.risk_warning}`
        ].filter(Boolean);

        return sections.join('\n\n');
    };

    const analysisContent = formatAnalysisContent(ai_analysis);

    // Calculate previous prices from history for trend (using transformed data)
    const prevGold = historicalData?.length > 1 ? historicalData[historicalData.length - 2].gold : prices?.gold_price;
    const prevSilver = historicalData?.length > 1 ? historicalData[historicalData.length - 2].silver : prices?.silver_price;
    const prevPlatinum = historicalData?.length > 1 ? historicalData[historicalData.length - 2].platinum : prices?.platinum_price;

    const goldChangeVal = prices?.gold_price && prevGold ? (prices.gold_price - prevGold) : 0;
    const silverChangeVal = prices?.silver_price && prevSilver ? (prices.silver_price - prevSilver) : 0;
    const platinumChangeVal = prices?.platinum_price && prevPlatinum ? (prices.platinum_price - prevPlatinum) : 0;

    const goldPercent = prevGold ? ((goldChangeVal / prevGold) * 100).toFixed(2) : '0.00';
    const silverPercent = prevSilver ? ((silverChangeVal / prevSilver) * 100).toFixed(2) : '0.00';
    const platinumPercent = prevPlatinum ? ((platinumChangeVal / prevPlatinum) * 100).toFixed(2) : '0.00';

    const goldChangeStr = `${goldChangeVal >= 0 ? '+' : ''}${goldPercent}%`;
    const silverChangeStr = `${silverChangeVal >= 0 ? '+' : ''}${silverPercent}%`;
    const platinumChangeStr = `${platinumChangeVal >= 0 ? '+' : ''}${platinumPercent}%`;

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="min-h-screen bg-slate-950 text-slate-200 p-4 md:p-8 space-y-6 font-sans"
        >

            {/* Header */}
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <Activity className="text-white" size={24} />
                        </div>
                        金銀價格追蹤系統
                    </h1>
                    <div className="flex items-center gap-3 mt-2">
                        <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/10 rounded-full border border-emerald-500/20">
                            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]"></div>
                            <span className="text-emerald-400 text-xs font-bold tracking-wider">系統運行中</span>
                        </div>
                    </div>
                </div>

                <div className="text-right hidden md:block bg-slate-900/50 px-4 py-2 rounded-xl border border-slate-800">
                    <div className="text-[10px] text-slate-500 font-mono uppercase tracking-wider mb-0.5">最後更新</div>
                    <div className="font-mono text-xl text-slate-200 font-bold">
                        {lastUpdate ? lastUpdate.toLocaleTimeString('zh-TW') : '--:--:--'}
                    </div>
                </div>
            </header>

            {/* Ticker Section - Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <PriceCard
                    title="黃金 (TWD/錢)"
                    price={prices?.gold_price?.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                    change={goldChangeStr}
                    isUp={goldChangeVal >= 0}
                    colorCode="text-yellow-400"
                    icon={<Zap size={14} className="text-yellow-500" />}
                />
                <PriceCard
                    title="白銀 (TWD/錢)"
                    price={prices?.silver_price?.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                    change={silverChangeStr}
                    isUp={silverChangeVal >= 0}
                    colorCode="text-slate-200"
                    icon={<Server size={14} className="text-slate-400" />}
                />
                <PriceCard
                    title="白金 (TWD/錢)"
                    price={prices?.platinum_price?.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                    change={platinumChangeStr}
                    isUp={platinumChangeVal >= 0}
                    colorCode="text-sky-300"
                    icon={<Activity size={14} className="text-sky-400" />}
                />
            </div>

            {/* Central Dashboard Grid */}
            {/* Central Dashboard - Vertical Layout */}
            <div className="flex flex-col gap-6">

                {/* Chart Section (Full width) */}
                <div className="w-full h-[400px]">
                    <PriceChart
                        historicalData={historicalData}
                        period={period}
                        onPeriodChange={setPeriod}
                    />
                </div>

                {/* AI Analysis Section (Full width) */}
                <div className="w-full">
                    <AnalysisSection
                        onAnalyze={handleManualAnalysis}
                        isAnalyzing={isAnalyzing}
                        analysisText={manualAnalysis ? formatAnalysisContent(manualAnalysis) : analysisContent}
                        lastUpdated={ai_analysis?.timestamp ? new Date(ai_analysis.timestamp).toLocaleString('zh-TW') : ''}
                    />
                </div>
            </div>
        </motion.div>
    );
}

export default App;
