#!/usr/bin/env python3
"""
测试共享模型和工具 - 微服务架构迁移验证
验证所有迁移到shared/目录下的模型和工具是否正常工作
"""

import sys
import os
from pathlib import Path
from datetime import date

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_shared_models():
    """测试共享模型"""
    print("=" * 60)
    print("测试共享模型")
    print("=" * 60)

    try:
        # 测试基础模型导入
        from shared.models import (
            StockData, TradingSignal, Position, TradeRecord,
            SignalType, TradeAction, OrderType, OrderStatus, StrategyType
        )
        print("✓ 基础模型导入成功")

        # 测试市场数据模型
        from shared.models.market_data import (
            StockData, StockInfo, MarketIndex, TradingSession,
            StockDataValidator, StockDataProcessor
        )
        print("✓ 市场数据模型导入成功")

        # 测试策略模型
        from shared.models.strategy import (
            SelectionCriteria, StrategyConfig, StrategyExecution,
            StrategyBacktest, StrategyOptimization, StrategyValidation
        )
        print("✓ 策略模型导入成功")

        # 测试ML策略模型
        from shared.models.ml_strategy import (
            ModelConfig, MLStrategyConfig, RiskManagementConfig,
            ModelPerformance, MLPrediction, MLSignal,
            ModelType, FeatureSelectionMethod, PositionSizingMethod
        )
        print("✓ ML策略模型导入成功")

        # 测试模型实例化
        stock_data = StockData(
            code="000001",
            date=date(2024, 1, 1),
            open_price=10.0,
            close_price=10.5,
            high_price=10.8,
            low_price=9.8,
            volume=1000000,
            amount=10500000.0,
            name="平安银行"
        )
        print(f"✓ StockData实例化成功: {stock_data.code}")

        trading_signal = TradingSignal(
            stock_code="000001",
            signal_type=SignalType.BUY,
            signal_time=date(2024, 1, 1),
            price=10.5,
            confidence=0.8,
            reason="技术指标金叉",
            strategy_name="动量策略"
        )
        print(f"✓ TradingSignal实例化成功: {trading_signal.stock_code}")

        position = Position(
            stock_code="000001",
            stock_name="平安银行",
            quantity=1000,
            avg_cost=10.0,
            current_price=10.5,
            market_value=10500.0,
            unrealized_pnl=500.0,
            unrealized_pnl_pct=0.05,
            buy_date=date(2024, 1, 1),
            holding_days=1
        )
        print(f"✓ Position实例化成功: {position.stock_code}")

        # 测试ML策略配置
        model_config = ModelConfig(
            model_type=ModelType.RANDOM_FOREST,
            n_estimators=200,
            max_depth=15,
            feature_selection=FeatureSelectionMethod.KBEST,
            n_features=20
        )
        print(f"✓ ModelConfig实例化成功: {model_config.model_type.value}")

        risk_config = RiskManagementConfig(
            max_position_pct=0.15,
            max_positions=8,
            stop_loss_pct=0.04,
            take_profit_pct=0.08
        )
        print(f"✓ RiskManagementConfig实例化成功")

        ml_strategy_config = MLStrategyConfig(
            name="ML增强策略",
            model_config=model_config,
            signal_threshold=0.02,
            confidence_threshold=0.6,
            position_sizing=PositionSizingMethod.KELLY,
            risk_management=risk_config
        )
        print(f"✓ MLStrategyConfig实例化成功: {ml_strategy_config.name}")

        return True

    except Exception as e:
        print(f"✗ 共享模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_shared_utils():
    """测试共享工具"""
    print("\n" + "=" * 60)
    print("测试共享工具")
    print("=" * 60)

    try:
        # 测试配置工具
        from shared.utils.config import ConfigLoader, ConfigValidator
        print("✓ 配置工具导入成功")

        # 测试日志工具
        from shared.utils.logger import get_logger, setup_logging, QuantLogger
        print("✓ 日志工具导入成功")

        # 测试异常类
        from shared.utils.exceptions import (
            QuantSystemError, ConfigError, DataError, StrategyError,
            BacktestError, ValidationError
        )
        print("✓ 异常类导入成功")

        # 测试辅助函数
        from shared.utils.helpers import (
            ensure_dir, safe_divide, format_percentage, calculate_returns,
            calculate_sharpe_ratio, calculate_volatility, is_valid_stock_code
        )
        print("✓ 辅助函数导入成功")

        # 测试验证器
        from shared.utils.validators import (
            DataValidator, ConfigValidator as ValidationUtils,
            validate_stock_data, validate_trading_signal, validate_config
        )
        print("✓ 验证器导入成功")

        # 测试日志器
        logger = get_logger("test_logger")
        logger.info("测试日志功能")
        print("✓ 日志器功能正常")

        # 测试辅助函数
        result = safe_divide(10, 2)
        assert result == 5.0, f"safe_divide测试失败: {result}"
        print("✓ safe_divide函数正常")

        percentage = format_percentage(0.1234)
        assert percentage == "12.34%", f"format_percentage测试失败: {percentage}"
        print("✓ format_percentage函数正常")

        returns = calculate_returns([100, 110, 105, 115])
        assert len(returns) == 3, f"calculate_returns测试失败: {len(returns)}"
        print("✓ calculate_returns函数正常")

        sharpe = calculate_sharpe_ratio([0.01, 0.02, -0.01, 0.03])
        assert isinstance(
            sharpe, float), f"calculate_sharpe_ratio测试失败: {sharpe}"
        print("✓ calculate_sharpe_ratio函数正常")

        is_valid = is_valid_stock_code("000001")
        assert is_valid == True, f"is_valid_stock_code测试失败: {is_valid}"
        print("✓ is_valid_stock_code函数正常")

        # 测试验证器
        validator = DataValidator()
        stock_data_dict = {
            'code': '000001',
            'date': '2024-01-01',
            'open_price': 10.0,
            'close_price': 10.5,
            'high_price': 10.8,
            'low_price': 9.8,
            'volume': 1000000
        }
        is_valid = validator.validate_stock_data(stock_data_dict)
        assert is_valid == True, f"股票数据验证失败: {validator.get_errors()}"
        print("✓ 数据验证器正常")

        # 测试异常处理
        try:
            raise ConfigError("测试配置错误", "test.yaml", "test_key")
        except ConfigError as e:
            assert e.error_code == "CONFIG_ERROR", f"异常错误代码错误: {e.error_code}"
            print("✓ 异常处理正常")

        return True

    except Exception as e:
        print(f"✗ 共享工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """测试集成功能"""
    print("\n" + "=" * 60)
    print("测试集成功能")
    print("=" * 60)

    try:
        from datetime import date
        from shared.models import StockData, TradingSignal, SignalType
        from shared.utils.logger import get_logger
        from shared.utils.helpers import calculate_returns, calculate_sharpe_ratio
        from shared.utils.validators import validate_stock_data

        logger = get_logger("integration_test")

        # 创建股票数据
        stock_data = StockData(
            code="000001",
            date=date(2024, 1, 1),
            open_price=10.0,
            close_price=10.5,
            high_price=10.8,
            low_price=9.8,
            volume=1000000,
            amount=10500000.0,
            name="平安银行"
        )

        # 验证数据
        stock_dict = {
            'code': stock_data.code,
            'date': str(stock_data.date),
            'open_price': stock_data.open_price,
            'close_price': stock_data.close_price,
            'high_price': stock_data.high_price,
            'low_price': stock_data.low_price,
            'volume': stock_data.volume
        }

        is_valid, errors = validate_stock_data(stock_dict)
        assert is_valid, f"数据验证失败: {errors}"

        # 创建交易信号
        signal = TradingSignal(
            stock_code=stock_data.code,
            signal_type=SignalType.BUY,
            signal_time=stock_data.date,
            price=stock_data.close_price,
            confidence=0.8,
            reason="价格突破",
            strategy_name="突破策略"
        )

        # 计算收益率
        prices = [10.0, 10.5, 10.2, 11.0, 10.8]
        returns = calculate_returns(prices)
        sharpe = calculate_sharpe_ratio(returns)

        logger.info(
            f"股票: {stock_data.code}, 信号: {signal.signal_type.value}, 夏普比率: {sharpe:.4f}")

        print("✓ 集成测试成功")
        return True

    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("开始测试共享模型和工具...")

    # 测试共享模型
    models_ok = test_shared_models()

    # 测试共享工具
    utils_ok = test_shared_utils()

    # 测试集成功能
    integration_ok = test_integration()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    if models_ok and utils_ok and integration_ok:
        print("🎉 所有测试通过！共享模型和工具迁移成功！")
        print("\n✅ 已成功迁移:")
        print("  - 基础数据模型 (TradingSignal, Position, TradeRecord等)")
        print("  - 市场数据模型 (StockData, StockInfo等)")
        print("  - 策略配置模型 (SelectionCriteria, StrategyConfig等)")
        print("  - ML策略模型 (ModelConfig, MLStrategyConfig等)")
        print("  - 配置工具 (ConfigLoader, ConfigValidator)")
        print("  - 日志工具 (QuantLogger, get_logger)")
        print("  - 异常类 (QuantSystemError及其子类)")
        print("  - 辅助函数 (safe_divide, calculate_returns等)")
        print("  - 验证器 (DataValidator, SchemaValidator)")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
