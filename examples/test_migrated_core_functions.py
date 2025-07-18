"""
测试迁移的核心功能模块
验证特征提取、交易策略和回测引擎是否正常工作
"""
import sys
import os
import logging
from datetime import date, timedelta
import numpy as np
import pandas as pd

# 正确添加项目根目录到sys.path，保证shared包可用
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 添加微服务路径到Python路径（保持原有逻辑，防止app包找不到）
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'services', 'core-service'))
sys.path.insert(0, os.path.join(project_root, 'shared'))

# 设置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_feature_extraction():
    """测试特征提取功能"""
    logger.info("=" * 50)
    logger.info("测试特征提取功能")
    logger.info("=" * 50)

    try:
        from app.processors.feature_calculator import QuantitativeFeatureExtractor
        from shared.models.market_data import StockData

        # 创建特征提取器
        extractor = QuantitativeFeatureExtractor()
        logger.info("✅ 特征提取器初始化成功")

        # 生成测试数据
        test_data = []
        base_price = 10.0

        for i in range(60):
            test_date = date.today() - timedelta(days=60-i)

            # 生成价格数据
            price_change = np.random.normal(0, 0.02)
            close_price = base_price * (1 + price_change)
            open_price = close_price * (1 + np.random.normal(0, 0.01))
            high_price = max(open_price, close_price) * \
                (1 + abs(np.random.normal(0, 0.005)))
            low_price = min(open_price, close_price) * \
                (1 - abs(np.random.normal(0, 0.005)))

            # 生成成交量数据
            volume = np.random.randint(1000000, 10000000)
            amount = volume * close_price

            stock_data = StockData(
                code="000001",
                date=test_date,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=volume,
                amount=amount
            )
            test_data.append(stock_data)
            base_price = close_price

        logger.info(f"✅ 生成测试数据成功，共 {len(test_data)} 条记录")

        # 提取特征
        features = extractor.extract_features(test_data)
        logger.info(f"✅ 特征提取成功，共提取 {len(features)} 个特征")

        # 显示部分特征
        feature_names = list(features.keys())[:10]
        logger.info(f"特征示例: {feature_names}")

        # 测试批量特征提取
        stock_data_dict = {"000001": test_data}
        feature_df = extractor.extract_batch_features(stock_data_dict)
        logger.info(f"✅ 批量特征提取成功，DataFrame形状: {feature_df.shape}")

        return True

    except Exception as e:
        logger.error(f"❌ 特征提取测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trading_strategy():
    """测试交易策略功能"""
    logger.info("=" * 50)
    logger.info("测试交易策略功能")
    logger.info("=" * 50)

    try:
        from app.strategies.base_strategy import QuantitativeTradingStrategy
        from shared.models.market_data import StockData

        # 创建交易策略
        strategy = QuantitativeTradingStrategy()
        logger.info("✅ 交易策略初始化成功")

        # 测试策略列表
        strategies = strategy.list_strategies()
        logger.info(f"✅ 可用策略: {strategies}")

        # 测试策略切换
        if "momentum" in strategies:
            success = strategy.set_strategy("momentum")
            logger.info(f"✅ 切换到动量策略: {success}")

        # 生成测试数据
        test_data = []
        base_price = 10.0

        for i in range(60):
            test_date = date.today() - timedelta(days=60-i)

            # 生成价格数据
            price_change = np.random.normal(0, 0.02)
            close_price = base_price * (1 + price_change)
            open_price = close_price * (1 + np.random.normal(0, 0.01))
            high_price = max(open_price, close_price) * \
                (1 + abs(np.random.normal(0, 0.005)))
            low_price = min(open_price, close_price) * \
                (1 - abs(np.random.normal(0, 0.005)))

            # 生成成交量数据
            volume = np.random.randint(1000000, 10000000)
            amount = volume * close_price

            stock_data = StockData(
                code="000001",
                date=test_date,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=volume,
                amount=amount
            )
            test_data.append(stock_data)
            base_price = close_price

        # 测试买入信号生成
        signals = strategy.generate_trading_signals(test_data)
        logger.info(f"✅ 信号生成成功，共生成 {len(signals)} 个信号")

        if signals:
            for signal in signals:
                logger.info(
                    f"信号: {signal.signal_type} {signal.code} @{signal.price:.2f} 置信度:{signal.confidence:.2f}")

        # 测试策略摘要
        summary = strategy.get_strategy_summary()
        logger.info(f"✅ 策略摘要: {summary['name']} - {summary['description']}")

        return True

    except Exception as e:
        logger.error(f"❌ 交易策略测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backtest_engine():
    """测试回测引擎功能"""
    logger.info("=" * 50)
    logger.info("测试回测引擎功能")
    logger.info("=" * 50)

    try:
        from app.backtesting.backtest_engine import QuantitativeBacktestEngine, BacktestConfig
        from app.strategies.base_strategy import QuantitativeTradingStrategy
        from datetime import date, timedelta

        # 创建回测引擎
        backtest_engine = QuantitativeBacktestEngine()
        logger.info("✅ 回测引擎初始化成功")

        # 创建策略
        strategy = QuantitativeTradingStrategy()
        strategy.set_strategy("momentum")
        logger.info("✅ 策略初始化成功")

        # 配置回测参数
        end_date = date.today()
        start_date = end_date - timedelta(days=30)  # 30天回测

        config = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            initial_capital=100000,  # 10万初始资金
            max_positions=3
        )

        logger.info(f"回测期间: {start_date} 到 {end_date}")
        logger.info(f"初始资金: {config.initial_capital:,.0f}")

        # 运行回测
        results = backtest_engine.run_backtest(
            strategy, start_date, end_date, config)

        if results:
            logger.info("✅ 回测运行成功")
            logger.info(f"总收益率: {results['total_return']:.2%}")
            logger.info(f"年化收益率: {results['annual_return']:.2%}")
            logger.info(f"最大回撤: {results['max_drawdown']:.2%}")
            logger.info(f"夏普比率: {results['sharpe_ratio']:.2f}")
            logger.info(f"胜率: {results['win_rate']:.2%}")
            logger.info(f"总交易次数: {results['total_trades']}")
            logger.info(f"平均持仓天数: {results['avg_holding_days']:.1f}")

            # 测试获取交易记录
            trade_records = backtest_engine.get_trade_records()
            logger.info(f"✅ 获取交易记录成功，共 {len(trade_records)} 条")

            # 测试获取持仓
            positions = backtest_engine.get_positions()
            logger.info(f"✅ 获取持仓成功，共 {len(positions)} 个持仓")

            # 测试获取组合历史
            portfolio_history = backtest_engine.get_portfolio_history()
            logger.info(f"✅ 获取组合历史成功，共 {len(portfolio_history)} 条记录")

        else:
            logger.warning("⚠️ 回测未返回结果")

        return True

    except Exception as e:
        logger.error(f"❌ 回测引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """测试模块集成"""
    logger.info("=" * 50)
    logger.info("测试模块集成")
    logger.info("=" * 50)

    try:
        from app.processors.feature_calculator import QuantitativeFeatureExtractor
        from app.strategies.base_strategy import QuantitativeTradingStrategy
        from app.backtesting.backtest_engine import QuantitativeBacktestEngine, BacktestConfig
        from shared.models.market_data import StockData
        from datetime import date, timedelta

        # 创建所有组件
        feature_extractor = QuantitativeFeatureExtractor()
        strategy = QuantitativeTradingStrategy()
        strategy.set_strategy("momentum")
        backtest_engine = QuantitativeBacktestEngine()

        logger.info("✅ 所有组件初始化成功")

        # 生成测试数据
        test_data = []
        base_price = 10.0

        for i in range(60):
            test_date = date.today() - timedelta(days=60-i)

            price_change = np.random.normal(0, 0.02)
            close_price = base_price * (1 + price_change)
            open_price = close_price * (1 + np.random.normal(0, 0.01))
            high_price = max(open_price, close_price) * \
                (1 + abs(np.random.normal(0, 0.005)))
            low_price = min(open_price, close_price) * \
                (1 - abs(np.random.normal(0, 0.005)))

            volume = np.random.randint(1000000, 10000000)
            amount = volume * close_price

            stock_data = StockData(
                code="000001",
                date=test_date,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=volume,
                amount=amount
            )
            test_data.append(stock_data)
            base_price = close_price

        # 测试完整流程
        # 1. 特征提取
        features = feature_extractor.extract_features(test_data)
        logger.info(f"✅ 特征提取: {len(features)} 个特征")

        # 2. 策略信号生成
        signals = strategy.generate_trading_signals(test_data)
        logger.info(f"✅ 策略信号: {len(signals)} 个信号")

        # 3. 回测
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        config = BacktestConfig(start_date=start_date,
                                end_date=end_date, initial_capital=100000)

        results = backtest_engine.run_backtest(
            strategy, start_date, end_date, config)
        logger.info(f"✅ 回测完成: 收益率 {results.get('total_return', 0):.2%}")

        return True

    except Exception as e:
        logger.error(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    logger.info("开始测试迁移的核心功能模块")
    logger.info("=" * 60)

    test_results = []

    # 测试各个模块
    test_results.append(("特征提取", test_feature_extraction()))
    test_results.append(("交易策略", test_trading_strategy()))
    test_results.append(("回测引擎", test_backtest_engine()))
    test_results.append(("模块集成", test_integration()))

    # 输出测试结果
    logger.info("=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)

    passed = 0
    total = len(test_results)

    for module_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{module_name}: {status}")
        if result:
            passed += 1

    logger.info("=" * 60)
    logger.info(f"总体结果: {passed}/{total} 个模块测试通过")

    if passed == total:
        logger.info("🎉 所有核心功能模块测试通过！")
    else:
        logger.warning("⚠️ 部分模块测试失败，请检查错误信息")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
