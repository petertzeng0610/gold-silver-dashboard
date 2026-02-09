/**
 * AI洞察面板組件 - 顯示AI分析結果
 */
import React from 'react';

const AIInsights = ({ aiAnalysis }) => {
    if (!aiAnalysis) {
        return (
            <div style={styles.container}>
                <h2 style={styles.title}>🤖 AI市場分析</h2>
                <p style={styles.noData}>暫無AI分析數據</p>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <h2 style={styles.title}>🤖 AI市場分析</h2>

            <div style={styles.section}>
                <h3 style={styles.sectionTitle}>📊 市場分析</h3>
                <div style={styles.content}>
                    {aiAnalysis.market_analysis || '暫無數據'}
                </div>
            </div>

            <div style={styles.section}>
                <h3 style={styles.sectionTitle}>📈 趨勢預測</h3>
                <div style={styles.content}>
                    {aiAnalysis.trend_prediction || '暫無數據'}
                </div>
            </div>

            <div style={styles.section}>
                <h3 style={styles.sectionTitle}>💡 投資建議</h3>
                <div style={styles.content}>
                    {aiAnalysis.investment_advice || '暫無數據'}
                </div>
            </div>

            <div style={styles.section}>
                <h3 style={styles.sectionTitle}>⚠️ 風險提示</h3>
                <div style={{ ...styles.content, ...styles.warningContent }}>
                    {aiAnalysis.risk_warning || '暫無數據'}
                </div>
            </div>

            {aiAnalysis.timestamp && (
                <div style={styles.timestamp}>
                    更新時間：{new Date(aiAnalysis.timestamp).toLocaleString('zh-TW')}
                </div>
            )}
        </div>
    );
};

const styles = {
    container: {
        backgroundColor: '#fff',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        marginTop: '20px',
    },
    title: {
        fontSize: '24px',
        fontWeight: 'bold',
        marginBottom: '20px',
        color: '#333',
        borderBottom: '2px solid #4CAF50',
        paddingBottom: '10px',
    },
    section: {
        marginBottom: '20px',
    },
    sectionTitle: {
        fontSize: '18px',
        fontWeight: '600',
        marginBottom: '10px',
        color: '#555',
    },
    content: {
        fontSize: '15px',
        lineHeight: '1.6',
        color: '#666',
        backgroundColor: '#f5f5f5',
        padding: '15px',
        borderRadius: '6px',
        whiteSpace: 'pre-wrap',
    },
    warningContent: {
        backgroundColor: '#fff3cd',
        borderLeft: '4px solid #ff9800',
    },
    noData: {
        textAlign: 'center',
        color: '#999',
        padding: '40px',
        fontSize: '16px',
    },
    timestamp: {
        textAlign: 'right',
        color: '#999',
        fontSize: '14px',
        marginTop: '15px',
        fontStyle: 'italic',
    },
};

export default AIInsights;
