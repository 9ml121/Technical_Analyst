"""
数据模型单元测试

测试股票数据、策略模型、回测模型等数据结构
"""
import pytest
from datetime import date, datetime
from decimal import Decimal

# 添加src目录到Python路径
import sys
from pathlib import Path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from quant_system.models.stock_data import StockData, StockInfo, StockDataValidator
from quant_system.models.strategy_models import (
    SelectionCriteria, TradingStrategy, TradingSignal, Position, Portfolio,
    StrategyType, SignalType
)
from quant_system.models.backtest_models import (
    BacktestConfig, Order, TradeRecord, BacktestResult,
    OrderType, OrderStatus, TradeAction
)

class TestStockData:
    """股票数据模型测试"""
    
    def test_stock_data_creation(self):
        """测试股票数据创建"""
        stock_data = StockData(
            code="000001",
            name="平安银行",
            date=date(2024, 1, 15),
            open_price=12.50,
            close_price=12.80,
            high_price=13.00,
            low_price=12.30,
            volume=1000000,
            amount=12800000
        )
        
        assert stock_data.code == "000001"
        assert stock_data.name == "平安银行"
        assert stock_data.date == date(2024, 1, 15)
        assert stock_data.open_price == 12.50
        assert stock_data.close_price == 12.80
        assert stock_data.high_price == 13.00
        assert stock_data.low_price == 12.30
        assert stock_data.volume == 1000000
        assert stock_data.amount == 12800000
    
    def test_stock_data_with_optional_fields(self):
        """测试包含可选字段的股票数据"""
        stock_data = StockData(
            code="000001",
            name="平安银行",
            date=date(2024, 1, 15),
            open_price=12.50,
            close_price=12.80,
            high_price=13.00,
            low_price=12.30,
            volume=1000000,
            amount=12800000,
            pre_close=12.50,
            change=0.30,
            pct_change=0.024,
            turnover_rate=0.05
        )
        
        assert stock_data.pre_close == 12.50
        assert stock_data.change == 0.30
        assert stock_data.pct_change == 0.024
        assert stock_data.turnover_rate == 0.05
    
    def test_stock_info_creation(self):
        """测试股票信息创建"""
        stock_info = StockInfo(
            code="000001",
            name="平安银行",
            industry="银行",
            sector="金融",
            market="深市主板",
            list_date=date(1991, 4, 3)
        )
        
        assert stock_info.code == "000001"
        assert stock_info.name == "平安银行"
        assert stock_info.industry == "银行"
        assert stock_info.sector == "金融"
        assert stock_info.market == "深市主板"
        assert stock_info.list_date == date(1991, 4, 3)

class TestStockDataValidator:
    """股票数据验证器测试"""
    
    def test_validate_stock_code_a_share(self):
        """测试A股代码验证"""
        validator = StockDataValidator()
        
        # 有效的A股代码
        assert validator.validate_stock_code("000001", "A") is True  # 深市主板
        assert validator.validate_stock_code("300001", "A") is True  # 创业板
        assert validator.validate_stock_code("600000", "A") is True  # 沪市主板
        assert validator.validate_stock_code("688001", "A") is True  # 科创板
        
        # 无效的A股代码
        assert validator.validate_stock_code("123456", "A") is False
        assert validator.validate_stock_code("00001", "A") is False   # 长度不对
        assert validator.validate_stock_code("", "A") is False        # 空字符串
    
    def test_validate_price_data(self):
        """测试价格数据验证"""
        validator = StockDataValidator()
        
        # 有效价格
        assert validator.validate_price_data(12.50) is True
        assert validator.validate_price_data(0.01) is True
        assert validator.validate_price_data(1000.0) is True
        
        # 无效价格
        assert validator.validate_price_data(-1.0) is False
        assert validator.validate_price_data(0) is False
        assert validator.validate_price_data(10001.0) is False
    
    def test_validate_volume_data(self):
        """测试成交量数据验证"""
        validator = StockDataValidator()
        
        # 有效成交量
        assert validator.validate_volume_data(1000000) is True
        assert validator.validate_volume_data(0) is True
        
        # 无效成交量
        assert validator.validate_volume_data(-1000) is False

class TestStrategyModels:
    """策略模型测试"""
    
    def test_selection_criteria_creation(self):
        """测试选股条件创建"""
        criteria = SelectionCriteria(
            consecutive_days=3,
            min_total_return=0.15,
            max_drawdown=0.05,
            min_stock_price=5.0,
            max_stock_price=200.0
        )
        
        assert criteria.consecutive_days == 3
        assert criteria.min_total_return == 0.15
        assert criteria.max_drawdown == 0.05
        assert criteria.min_stock_price == 5.0
        assert criteria.max_stock_price == 200.0
        assert criteria.exclude_limit_up_first_day is True  # 默认值
    
    def test_trading_strategy_creation(self):
        """测试交易策略创建"""
        strategy = TradingStrategy(
            name="测试策略",
            strategy_type=StrategyType.MOMENTUM,
            description="用于测试的动量策略"
        )
        
        assert strategy.name == "测试策略"
        assert strategy.strategy_type == StrategyType.MOMENTUM
        assert strategy.description == "用于测试的动量策略"
        assert len(strategy.buy_rules) == 0
        assert len(strategy.sell_rules) == 0
        assert len(strategy.risk_rules) == 0
    
    def test_trading_signal_creation(self):
        """测试交易信号创建"""
        signal = TradingSignal(
            stock_code="000001",
            signal_type=SignalType.BUY,
            signal_time=date(2024, 1, 15),
            price=12.80,
            confidence=0.85,
            reason="满足动量条件",
            strategy_name="动量策略"
        )
        
        assert signal.stock_code == "000001"
        assert signal.signal_type == SignalType.BUY
        assert signal.signal_time == date(2024, 1, 15)
        assert signal.price == 12.80
        assert signal.confidence == 0.85
        assert signal.reason == "满足动量条件"
        assert signal.strategy_name == "动量策略"
    
    def test_position_creation_and_update(self):
        """测试持仓创建和更新"""
        position = Position(
            stock_code="000001",
            stock_name="平安银行",
            quantity=1000,
            avg_cost=12.50,
            current_price=12.80,
            market_value=12800,
            unrealized_pnl=300,
            unrealized_pnl_pct=0.024,
            buy_date=date(2024, 1, 10),
            holding_days=5
        )
        
        assert position.stock_code == "000001"
        assert position.quantity == 1000
        assert position.avg_cost == 12.50
        assert position.current_price == 12.80
        
        # 测试价格更新
        position.update_price(13.00)
        assert position.current_price == 13.00
        assert position.market_value == 13000
        assert position.unrealized_pnl == 500
        assert position.unrealized_pnl_pct == 0.04
    
    def test_portfolio_management(self):
        """测试投资组合管理"""
        portfolio = Portfolio(
            total_value=1000000,
            cash=500000,
            market_value=500000
        )
        
        # 添加持仓
        position = Position(
            stock_code="000001",
            stock_name="平安银行",
            quantity=1000,
            avg_cost=12.50,
            current_price=12.80,
            market_value=12800,
            unrealized_pnl=300,
            unrealized_pnl_pct=0.024,
            buy_date=date(2024, 1, 10),
            holding_days=5
        )
        
        portfolio.add_position(position)
        assert "000001" in portfolio.positions
        
        # 移除持仓
        portfolio.remove_position("000001")
        assert "000001" not in portfolio.positions

class TestBacktestModels:
    """回测模型测试"""
    
    def test_backtest_config_creation(self):
        """测试回测配置创建"""
        config = BacktestConfig(
            start_date=date(2023, 1, 1),
            end_date=date(2024, 1, 1),
            initial_capital=1000000.0,
            max_positions=5,
            position_size_pct=0.20
        )
        
        assert config.start_date == date(2023, 1, 1)
        assert config.end_date == date(2024, 1, 1)
        assert config.initial_capital == 1000000.0
        assert config.max_positions == 5
        assert config.position_size_pct == 0.20
        assert config.commission_rate == 0.0003  # 默认值
    
    def test_backtest_config_validation(self):
        """测试回测配置验证"""
        # 测试无效的日期范围
        with pytest.raises(ValueError, match="开始日期必须早于结束日期"):
            BacktestConfig(
                start_date=date(2024, 1, 1),
                end_date=date(2023, 1, 1),
                initial_capital=1000000.0
            )
        
        # 测试无效的初始资金
        with pytest.raises(ValueError, match="初始资金必须大于0"):
            BacktestConfig(
                start_date=date(2023, 1, 1),
                end_date=date(2024, 1, 1),
                initial_capital=0
            )
        
        # 测试无效的仓位比例
        with pytest.raises(ValueError, match="仓位比例必须在0-1之间"):
            BacktestConfig(
                start_date=date(2023, 1, 1),
                end_date=date(2024, 1, 1),
                initial_capital=1000000.0,
                position_size_pct=1.5
            )
    
    def test_order_creation(self):
        """测试订单创建"""
        order = Order(
            order_id="ORDER_001",
            stock_code="000001",
            action=TradeAction.BUY,
            order_type=OrderType.MARKET,
            quantity=1000,
            price=12.80,
            order_time=datetime(2024, 1, 15, 9, 30, 0)
        )
        
        assert order.order_id == "ORDER_001"
        assert order.stock_code == "000001"
        assert order.action == TradeAction.BUY
        assert order.order_type == OrderType.MARKET
        assert order.quantity == 1000
        assert order.price == 12.80
        assert order.status == OrderStatus.PENDING  # 默认状态
    
    def test_trade_record_creation(self):
        """测试交易记录创建"""
        trade = TradeRecord(
            trade_id="TRADE_001",
            stock_code="000001",
            stock_name="平安银行",
            action=TradeAction.BUY,
            quantity=1000,
            price=12.80,
            amount=12800,
            commission=3.84,
            date=date(2024, 1, 15),
            time=datetime(2024, 1, 15, 9, 30, 0)
        )
        
        assert trade.trade_id == "TRADE_001"
        assert trade.stock_code == "000001"
        assert trade.stock_name == "平安银行"
        assert trade.action == TradeAction.BUY
        assert trade.quantity == 1000
        assert trade.price == 12.80
        assert trade.amount == 12800
        assert trade.commission == 3.84
        assert trade.stamp_tax == 0.0  # 默认值
    
    def test_backtest_result_metrics_calculation(self):
        """测试回测结果指标计算"""
        config = BacktestConfig(
            start_date=date(2023, 1, 1),
            end_date=date(2024, 1, 1),
            initial_capital=1000000.0
        )
        
        result = BacktestResult(
            config=config,
            start_date=date(2023, 1, 1),
            end_date=date(2024, 1, 1),
            initial_capital=1000000.0,
            final_capital=1200000.0,
            total_return=0.0,
            annual_return=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            win_rate=0.0,
            profit_loss_ratio=0.0,
            total_trades=0,
            avg_holding_days=0.0,
            turnover_rate=0.0,
            benchmark_return=0.0,
            excess_return=0.0,
            tracking_error=0.0,
            information_ratio=0.0,
            volatility=0.0,
            downside_volatility=0.0
        )
        
        # 添加一些模拟的日度绩效数据
        from quant_system.models.backtest_models import DailyPerformance
        
        daily_returns = [0.01, -0.005, 0.02, -0.01, 0.015]
        for i, ret in enumerate(daily_returns):
            daily_perf = DailyPerformance(
                date=date(2023, 1, i+1),
                portfolio_value=1000000 * (1 + ret),
                cash=500000,
                market_value=500000 * (1 + ret),
                daily_return=ret,
                cumulative_return=sum(daily_returns[:i+1]),
                drawdown=0.0
            )
            result.daily_performance.append(daily_perf)
        
        # 计算指标
        result.calculate_metrics()
        
        # 验证计算结果
        assert result.total_return > 0  # 应该有正收益
        assert result.annual_return != 0  # 年化收益率应该被计算
        assert result.volatility >= 0  # 波动率应该非负

# 测试夹具
@pytest.fixture
def sample_stock_data():
    """示例股票数据夹具"""
    return StockData(
        code="000001",
        name="平安银行",
        date=date(2024, 1, 15),
        open_price=12.50,
        close_price=12.80,
        high_price=13.00,
        low_price=12.30,
        volume=1000000,
        amount=12800000
    )

@pytest.fixture
def sample_backtest_config():
    """示例回测配置夹具"""
    return BacktestConfig(
        start_date=date(2023, 1, 1),
        end_date=date(2024, 1, 1),
        initial_capital=1000000.0,
        max_positions=5,
        position_size_pct=0.20
    )

def test_data_models_integration(sample_stock_data, sample_backtest_config):
    """数据模型集成测试"""
    # 验证股票数据
    validator = StockDataValidator()
    assert validator.validate_stock_code(sample_stock_data.code, "A") is True
    assert validator.validate_price_data(sample_stock_data.close_price) is True
    
    # 验证回测配置
    assert sample_backtest_config.start_date < sample_backtest_config.end_date
    assert sample_backtest_config.initial_capital > 0
    assert 0 < sample_backtest_config.position_size_pct <= 1
