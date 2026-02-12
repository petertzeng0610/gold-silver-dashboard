import React, { useState } from 'react';
import { Bot, RefreshCw, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';

/**
 * AnalysisPanel Component
 * Displays AI analysis and allows manual triggering.
 * 
 * @param {object} aiAnalysis - The AI analysis data object
 * @param {function} onRefresh - Callback after successful refresh
 */
const AnalysisPanel = ({ aiAnalysis, onRefresh }) => {
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState(null);

    const handleGenerateAnalysis = async () => {
        try {
            setIsGenerating(true);
            setError(null);

            // Call the collect endpoint which triggers the full pipeline including AI analysis
            await apiService.triggerCollection();

            // Wait a moment for DB to update (optional, but good for UX)
            // Then refresh the parent data
            if (onRefresh) {
                await onRefresh();
            }
        } catch (err) {
            console.error("Analysis generation failed:", err);
            setError("無法生成分析，請稍後再試。");
        } finally {
            setIsGenerating(false);
        }
    };

    // Helper to format text with line breaks
    const formatAnalysisText = (text) => {
        if (!text) return "暫無分析數據...";
        return text.split('\n').map((line, i) => (
            <p key={i} style={{ marginBottom: '0.5rem', lineHeight: '1.6' }}>{line}</p>
        ));
    };

    return (
        <div className="card ai-card">
            <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <Bot size={24} color="var(--color-accent)" />
                    <h2 style={{ margin: 0, fontSize: '1.25rem' }}>AI 智能市場分析</h2>
                </div>
                <button
                    className="btn-primary"
                    onClick={handleGenerateAnalysis}
                    disabled={isGenerating}
                >
                    <RefreshCw size={18} className={isGenerating ? "spin-animation" : ""} />
                    {isGenerating ? "正在分析中..." : "生成最新分析"}
                </button>
            </div>

            {error && (
                <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-down)', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <AlertCircle size={18} />
                    {error}
                </div>
            )}

            <div className="analysis-content" style={{ color: 'var(--text-secondary)' }}>
                {aiAnalysis ? (
                    <>
                        <div style={{ marginBottom: '1.5rem' }}>
                            <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>市場趨勢預測</h4>
                            <div style={{ fontSize: '1.1rem', fontWeight: '500', color: aiAnalysis.trend_direction === '看漲' ? 'var(--color-up)' : aiAnalysis.trend_direction === '看跌' ? 'var(--color-down)' : 'var(--text-primary)' }}>
                                {aiAnalysis.trend_direction || '中性'}
                            </div>
                        </div>

                        <div className="analysis-text">
                            {formatAnalysisText(aiAnalysis.analysis_content)}
                        </div>

                        <div style={{ marginTop: '1.5rem', fontSize: '0.8rem', color: '#64748b', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
                            分析時間: {new Date(aiAnalysis.timestamp).toLocaleString('zh-TW')}
                        </div>
                    </>
                ) : (
                    <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
                        <Bot size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
                        <p>尚無分析數據，請點擊上方按鈕生成。</p>
                    </div>
                )}
            </div>

            <style>{`
                .spin-animation {
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
};

export default AnalysisPanel;
