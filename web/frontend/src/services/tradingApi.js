/**
 * 交易API服务
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

class TradingAPI {
  /**
   * 通用请求方法
   */
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API请求失败 [${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * 获取账户概览
   */
  async getAccountSummary(accountId = 1) {
    return await this.request(`/accounts/${accountId}/summary`);
  }

  /**
   * 获取持仓列表
   */
  async getPositions(accountId = 1) {
    return await this.request(`/accounts/${accountId}/positions`);
  }

  /**
   * 获取策略列表
   */
  async getStrategies() {
    return await this.request('/strategies/');
  }

  /**
   * 获取单个策略信息
   */
  async getStrategy(strategyId) {
    return await this.request(`/strategies/${strategyId}`);
  }

  /**
   * 启动策略
   */
  async startStrategy(strategyId) {
    return await this.request(`/strategies/${strategyId}/start`, {
      method: 'POST',
    });
  }

  /**
   * 暂停策略
   */
  async pauseStrategy(strategyId) {
    return await this.request(`/strategies/${strategyId}/pause`, {
      method: 'POST',
    });
  }

  /**
   * 停止策略
   */
  async stopStrategy(strategyId) {
    return await this.request(`/strategies/${strategyId}/stop`, {
      method: 'POST',
    });
  }

  /**
   * 获取市场指数数据
   */
  async getMarketIndices() {
    return await this.request('/market/realtime/indices');
  }

  /**
   * 获取市场统计数据
   */
  async getMarketStats() {
    return await this.request('/market/realtime/stats');
  }

  /**
   * 卖出股票
   */
  async sellPosition(accountId, symbol, quantity) {
    return await this.request(`/accounts/${accountId}/positions/sell`, {
      method: 'POST',
      body: JSON.stringify({
        symbol,
        quantity,
      }),
    });
  }

  /**
   * 获取交易记录
   */
  async getTrades(accountId = 1, limit = 50) {
    return await this.request(`/accounts/${accountId}/trades?limit=${limit}`);
  }

  /**
   * 获取账户列表
   */
  async getAccounts() {
    return await this.request('/accounts/');
  }

  /**
   * 启动实时数据更新
   * @param {Function} callback 数据更新回调函数
   * @param {number} interval 更新间隔（毫秒）
   * @returns {Function} 清理函数
   */
  startRealtimeUpdates(callback, interval = 2000) {
    const updateData = async () => {
      try {
        const [accountSummary, marketData] = await Promise.all([
          this.getAccountSummary(),
          this.getMarketIndices(),
        ]);

        callback({
          account: accountSummary,
          market: marketData,
          timestamp: new Date().toISOString(),
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
    return () => {
      clearInterval(intervalId);
    };
  }

  /**
   * 获取性能数据
   */
  async getPerformanceData(accountId = 1, days = 30) {
    return await this.request(`/performance/account/${accountId}?days=${days}`);
  }

  /**
   * 获取交易信号
   */
  async getTradingSignals(limit = 20) {
    return await this.request(`/market/signals?limit=${limit}`);
  }

  /**
   * 健康检查
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
}

// 创建单例实例
const tradingAPI = new TradingAPI();

export default tradingAPI;
