/**
 * API服務 - 與後端通訊
 */
import axios from 'axios';

let baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// 如果 VITE_API_URL 包含網域但漏了 http/https，自動補上 https (解決 Zeabur URL 常見問題)
if (baseURL && !baseURL.startsWith('http') && baseURL.includes('.')) {
    baseURL = `https://${baseURL}`;
}

const api = axios.create({
    baseURL: baseURL,
    timeout: 10000,
});

export const apiService = {
    /**
     * 獲取最新綜合數據
     */
    async getLatestData() {
        const response = await api.get('/latest');
        return response.data;
    },

    /**
     * 獲取歷史數據
     * @param {number} days - 獲取最近幾天的數據
     */
    async getHistoricalData(days = 30) {
        const response = await api.get('/history', { params: { days } });
        return response.data;
    },

    /**
     * 獲取當前價格
     */
    async getCurrentPrices() {
        const response = await api.get('/prices/current');
        return response.data;
    },

    /**
     * 獲取月度統計
     */
    async getMonthlyStatistics() {
        const response = await api.get('/statistics/monthly');
        return response.data;
    },

    /**
     * 獲取最新AI分析
     */
    async getLatestAIAnalysis() {
        const response = await api.get('/ai-analysis/latest');
        return response.data;
    },

    /**
     * 手動觸發數據採集
     */
    async triggerCollection() {
        // Use API Key from env or default
        const apiKey = import.meta.env.VITE_ADMIN_API_KEY || 'your-secret-api-key';
        const response = await api.post('/collect', {}, {
            headers: {
                'X-API-Key': apiKey
            }
        });
        return response.data;
    },

    /**
     * 健康檢查
     */
    async healthCheck() {
        const response = await api.get('/health');
        return response.data;
    },
};
