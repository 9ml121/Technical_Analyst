"""
量化投资系统架构定义

定义量化投资系统的基础架构接口和核心类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Any
from enum import Enum

# 导入现有的数据模型
from quant_system.models.stock_data import StockData
from quant_system.models.strategy_models import (
    TradingSignal, Position, SelectionCriteria, SignalType
)


class DataProvider(ABC):
    """数据提供者接口"""

    @abstractmethod
    def get_stock_list(self, market: str = "A") -> List[tuple]:
        """获取股票列表"""
        pass

    @abstractmethod
    def get_historical_data(self, code: str, start_date: date, end_date: date) -> List[StockData]:
        """获取历史数据"""
        pass

    @abstractmethod
    def get_realtime_data(self, codes: List[str]) -> Dict[str, StockData]:
        """获取实时数据"""
        pass


class StrategyEngine(ABC):
    """策略引擎接口"""

    @abstractmethod
    def load_selection_criteria(self, config_file: str) -> SelectionCriteria:
        """加载选股条件"""
        pass

    @abstractmethod
    def screen_stocks(self, criteria: SelectionCriteria, data_provider: DataProvider) -> List[Dict]:
        """筛选股票"""
        pass

    @abstractmethod
    def generate_trading_signals(self, stock_data: List[StockData]) -> List[TradingSignal]:
        """生成交易信号"""
        pass


class BacktestEngine(ABC):
    """回测引擎接口"""

    @abstractmethod
    def run_backtest(self, strategy: StrategyEngine, start_date: date, end_date: date,
                     config: Optional[Dict] = None) -> Dict:
        """运行回测"""
        pass

    @abstractmethod
    def calculate_performance(self, trades: List[Dict]) -> Dict:
        """计算性能指标"""
        pass


@dataclass
class TradeRecord:
    """交易记录"""
    code: str
    name: str
    action: str  # 'BUY' or 'SELL'
    quantity: int
    price: float
    amount: float
    fee: float
    date: date
    realized_pnl: Optional[float] = None
    reason: Optional[str] = None


# 为了兼容性，添加一些别名
class QuantitativeTradingStrategy:
    """量化交易策略基类"""

    def __init__(self):
        self.name = "量化交易策略"
        self.description = "基础量化交易策略"

    def select_stocks(self, market_data: List[StockData]) -> List[str]:
        """选股方法"""
        return []

    def generate_signals(self, stocks: List[str]) -> List[TradingSignal]:
        """生成交易信号"""
        return []

    def manage_risk(self, portfolio: Dict) -> List[Dict]:
        """风险管理"""
        return []


# 导出所有需要的类和接口
__all__ = [
    'DataProvider',
    'StrategyEngine',
    'BacktestEngine',
    'StockData',
    'TradingSignal',
    'Position',
    'SelectionCriteria',
    'TradeRecord',
    'QuantitativeTradingStrategy',
    'SignalType'
]
