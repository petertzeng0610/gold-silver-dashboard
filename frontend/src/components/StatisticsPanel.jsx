/**
 * 統計面板組件 - 顯示價格統計數據
 */
import React from 'react';

const StatisticsPanel = ({ currentPrices, statistics }) => {
    return (
        <div style={styles.container}>
            <h2 style={styles.title}>📊 價格統計（最近30天）</h2>

            {/* 當前價格 */}
            <div style={styles.currentPrices}>
                <div style={styles.priceCard}>
                    <div style={styles.priceLabel}>當前金價</div>
                    <div style={{ ...styles.priceValue, color: '#FFD700' }}>
                        {currentPrices?.gold_price?.toFixed(2) || '--'}
                        <span style={styles.unit}>TWD/錢</span>
                    </div>
                </div>
                <div style={styles.priceCard}>
                    <div style={styles.priceLabel}>當前銀價</div>
                    <div style={{ ...styles.priceValue, color: '#C0C0C0' }}>
                        {currentPrices?.silver_price?.toFixed(2) || '--'}
                        <span style={styles.unit}>TWD/錢</span>
                    </div>
                </div>
            </div>

            {/* 統計數據 */}
            {statistics && (
                <div style={styles.statsGrid}>
                    {/* 金價統計 */}
                    <div style={styles.statsSection}>
                        <h3 style={styles.statsTitle}>金價 (元/錢)</h3>
                        <div style={styles.statsItems}>
                            <div style={styles.statItem}>
                                <span style={styles.statLabel}>平均:</span>
                                <span style={styles.statValue}>{statistics.gold?.avg?.toFixed(2) || '--'}</span>
                            </div>
                            <div style={styles.statItem}>
                                <span style={styles.statLabel}>最高:</span>
                                <span style={{ ...styles.statValue, color: '#f44336' }}>
                                    {statistics.gold?.max?.toFixed(2) || '--'}
                                </span>
                            </div>
                            <div style={styles.statItem}>
                                <span style={styles.statLabel}>最低:</span>
                                <span style={{ ...styles.statValue, color: '#4CAF50' }}>
                                    {statistics.gold?.min?.toFixed(2) || '--'}
                                </span>
                            </div>
                            <div style={styles.statItem}>
                                <span style={styles.statLabel}>標準差:</span>
                                <span style={styles.statValue}>{statistics.gold?.std?.toFixed(2) || '--'}</span>
                            </div>
                        </div>
                    </div>

                    {/* 銀價統計 */}
                    <div style={styles.statsSection}>
                        <h3 style={styles.statsTitle}>銀價 (元/錢)</h3>
                        <div style={styles.statsItems}>
                            <div style={styles.statItem}>
                                <span style={styles.statLabel}>平均:</span>
                                <span style={styles.statValue}>{statistics.silver?.avg?.toFixed(2) || '--'}</span>
                            </div>
                            <div style={styles.statItem}>
                                <span style={styles.statLabel}>最高:</span>
                                <span style={{ ...styles.statValue, color: '#f44336' }}>
                                    {statistics.silver?.max?.toFixed(2) || '--'}
                                </span>
                            </div>
                            <div style={styles.statItem}>
                                <span style={styles.statLabel}>最低:</span>
                                <span style={{ ...styles.statValue, color: '#4CAF50' }}>
                                    {statistics.silver?.min?.toFixed(2) || '--'}
                                </span>
                            </div>
                            <div style={styles.statItem}>
                                <span style={styles.statLabel}>標準差:</span>
                                <span style={styles.statValue}>{statistics.silver?.std?.toFixed(2) || '--'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {currentPrices?.timestamp && (
                <div style={styles.timestamp}>
                    更新時間：{new Date(currentPrices.timestamp).toLocaleString('zh-TW')}
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
        borderBottom: '2px solid #2196F3',
        paddingBottom: '10px',
    },
    currentPrices: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px',
        marginBottom: '30px',
    },
    priceCard: {
        backgroundColor: '#f8f9fa',
        padding: '20px',
        borderRadius: '8px',
        textAlign: 'center',
        border: '2px solid #e0e0e0',
    },
    priceLabel: {
        fontSize: '14px',
        color: '#666',
        marginBottom: '10px',
    },
    priceValue: {
        fontSize: '32px',
        fontWeight: 'bold',
    },
    unit: {
        fontSize: '16px',
        fontWeight: 'normal',
        marginLeft: '5px',
        color: '#666',
    },
    statsGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '20px',
    },
    statsSection: {
        backgroundColor: '#f5f5f5',
        padding: '20px',
        borderRadius: '8px',
    },
    statsTitle: {
        fontSize: '18px',
        fontWeight: '600',
        marginBottom: '15px',
        color: '#555',
    },
    statsItems: {
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
    },
    statItem: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 12px',
        backgroundColor: '#fff',
        borderRadius: '4px',
    },
    statLabel: {
        fontSize: '15px',
        color: '#666',
    },
    statValue: {
        fontSize: '16px',
        fontWeight: '600',
        color: '#333',
    },
    timestamp: {
        textAlign: 'right',
        color: '#999',
        fontSize: '14px',
        marginTop: '20px',
        fontStyle: 'italic',
    },
};

export default StatisticsPanel;
