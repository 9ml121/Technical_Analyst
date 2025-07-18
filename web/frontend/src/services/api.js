/**
 * API服务 - 封装所有后端API调用
 */

import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

/**
 * 模拟实盘交易API
 */
export class TradingAPI {
  
  // 账户相关API
  static async getAccountSummary(accountId = 1) {
    return api.get(`/accounts/${accountId}/summary`);
  }

  static async getAccountList() {
    return api.get('/accounts/');
  }

  static async getPositions(accountId = 1) {
    return api.get(`/accounts/${accountId}/positions`);
  }

  static async sellPosition(accountId, symbol, quantity) {
    return api.post(`/accounts/${accountId}/positions/sell`, {
      symbol,
      quantity
    });
  }

  // 市场数据API
  static async getRealtimeIndices() {
    return api.get('/market/realtime/indices');
  }

  static async getMarketStats() {
    return api.get('/market/stats');
  }

  static async getMarketOverview() {
    return api.get('/market/overview');
  }

  // 策略相关API
  static async getStrategies() {
    return api.get('/strategies/');
  }

  static async getStrategy(strategyId) {
    return api.get(`/strategies/${strategyId}`);
  }

  static async startStrategy(strategyId) {
    return api.post(`/strategies/${strategyId}/start`);
  }

  static async pauseStrategy(strategyId) {
    return api.post(`/strategies/${strategyId}/pause`);
  }

  static async stopStrategy(strategyId) {
    return api.post(`/strategies/${strategyId}/stop`);
  }

  static async getStrategyPerformance(strategyId) {
    return api.get(`/strategies/${strategyId}/performance`);
  }

  // 交易相关API
  static async getTrades(accountId = 1, params = {}) {
    const queryParams = new URLSearchParams({
      account_id: accountId,
      ...params
    });
    return api.get(`/trades/?${queryParams}`);
  }

  static async getTradingSignals(params = {}) {
    const queryParams = new URLSearchParams(params);
    return api.get(`/trades/signals?${queryParams}`);
  }

  static async createOrder(orderData) {
    return api.post('/trades/order', orderData);
  }

  // 性能分析API
  static async getAccountPerformance(accountId, timeFrame = 'week') {
    return api.get(`/performance/account/${accountId}?time_frame=${timeFrame}`);
  }

  static async getStrategyPerformanceDetail(strategyId, timeFrame = 'week') {
    return api.get(`/performance/strategy/${strategyId}?time_frame=${timeFrame}`);
  }

  static async getPerformanceComparison(accountIds, strategyIds = null, timeFrame = 'month') {
    const params = new URLSearchParams({
      account_ids: accountIds.join(','),
      time_frame: timeFrame
    });
    if (strategyIds) {
      params.append('strategy_ids', strategyIds.join(','));
    }
    return api.get(`/performance/comparison?${params}`);
  }

  // WebSocket连接管理
  static createWebSocketConnection(clientId = 'web_client') {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/connect/${clientId}`;

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket连接已建立');
      // 订阅市场数据和账户更新
      ws.send(JSON.stringify({
        type: 'subscribe',
        topics: ['market_data', 'account_updates']
      }));
    };

    ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket连接已关闭');
    };

    return ws;
  }

  // WebSocket连接（暂时用轮询模拟）
  static startRealtimeUpdates(callback, interval = 5000) {
    const updateData = async () => {
      try {
        const [accountSummary, marketData] = await Promise.all([
          this.getAccountSummary(),
          this.getRealtimeIndices()
        ]);

        callback({
          account: accountSummary,
          market: marketData,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('实时数据更新失败:', error);
      }
    };

    // 立即执行一次
    updateData();

    // 设置定时更新
    const intervalId = setInterval(updateData, interval);

    // 返回清理函数
    return () => clearInterval(intervalId);
  }
}

export default TradingAPI;
