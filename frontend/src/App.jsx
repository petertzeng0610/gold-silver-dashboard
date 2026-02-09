/**
 * 主應用組件
 */
import React, { useState, useEffect } from 'react';
import PriceChart from './components/PriceChart';
import StatisticsPanel from './components/StatisticsPanel';
import AIInsights from './components/AIInsights';
import { apiService } from './services/api';
import './App.css';

function App() {
    const [latestData, setLatestData] = useState(null);
    const [historicalData, setHistoricalData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);

    // 載入數據
    const loadData = async () => {
        try {
            setLoading(true);
            setError(null);

            // 並行載入所有數據
            const [latest, historical] = await Promise.all([
                apiService.getLatestData(),
                apiService.getHistoricalData(30),
            ]);

            if (latest.status === 'success') {
                setLatestData(latest.data);
            }

            if (historical.status === 'success') {
                setHistoricalData(historical.data);
            }

            setLastUpdate(new Date());
        } catch (err) {
            console.error('載入數據失敗:', err);
            setError(err.message || '載入數據失敗');
        } finally {
            setLoading(false);
        }
    };

    // 初始載入
    useEffect(() => {
        loadData();

        // 每2分鐘自動刷新（與後端採集頻率同步）
        const interval = setInterval(() => {
            loadData();
        }, 120000); // 2分鐘

        return () => clearInterval(interval);
    }, []);

    // 手動刷新
    const handleRefresh = async () => {
        await loadData();
    };

    if (loading && !latestData) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>載入數據中...</p>
            </div>
        );
    }

    return (
        <div className="app">
            <header className="app-header">
                <h1>🏆 台灣金銀價格追蹤與分析系統</h1>
                <p className="subtitle">每2分鐘自動更新 · AI智能分析</p>
                <div className="header-actions">
                    <button onClick={handleRefresh} className="refresh-button" disabled={loading}>
                        {loading ? '刷新中...' : '🔄 手動刷新'}
                    </button>
                    {lastUpdate && (
                        <span className="last-update">
                            最後更新：{lastUpdate.toLocaleTimeString('zh-TW')}
                        </span>
                    )}
                </div>
            </header>

            <main className="app-main">
                {error && (
                    <div className="error-banner">
                        ⚠️ {error}
                    </div>
                )}

                {/* 價格圖表 */}
                <section className="chart-section">
                    <PriceChart historicalData={historicalData} />
                </section>

                {/* 統計面板 */}
                <section className="stats-section">
                    <StatisticsPanel
                        currentPrices={latestData?.prices}
                        statistics={latestData?.statistics}
                    />
                </section>

                {/* AI分析面板 */}
                <section className="ai-section">
                    <AIInsights aiAnalysis={latestData?.ai_analysis} />
                </section>
            </main>

            <footer className="app-footer">
                <p>© 2026 台灣金銀價格追蹤系統 · 採用多Agent架構 · Powered by Gemini AI</p>
            </footer>
        </div>
    );
}

export default App;
