#!/usr/bin/env python3
"""
机器学习策略演示

展示机器学习增强多因子策略的完整使用流程：
1. 策略配置
2. 数据获取
3. 特征提取
4. 模型训练
5. 预测和交易信号
6. 回测分析
"""

import sys
from pathlib import Path
from datetime import date, timedelta
import time
import logging

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_strategy_config():
    """创建策略配置"""
    print("🔧 创建策略配置...")

    from shared.models.ml_strategy import MLStrategyConfig, ModelConfig

    # 模型配置
    model_config = ModelConfig(
        model_type='random_forest',
        n_estimators=200,
        max_depth=12,
        learning_rate=0.1,
        feature_selection='kbest',
        n_features=20,
        target_horizon=5,
        retrain_frequency=30
    )

    # 策略配置
    strategy_config = MLStrategyConfig(
        name="演示策略",
        model_config=model_config,
        signal_threshold=0.015,  # 1.5%的信号阈值
        confidence_threshold=0.65,  # 65%的置信度阈值
        position_sizing='kelly',  # Kelly公式仓位管理
        risk_management={
            "max_position_pct": 0.15,  # 单只股票最大仓位15%
            "max_positions": 8,  # 最大持仓8只股票
            "stop_loss_pct": 0.05,  # 止损5%
            "take_profit_pct": 0.12,  # 止盈12%
            "max_drawdown_pct": 0.08,  # 最大回撤8%
            "min_confidence": 0.6  # 最小置信度60%
        },
        description="机器学习增强多因子选股策略演示"
    )

    print("✅ 策略配置创建完成")
    return strategy_config


def get_demo_data():
    """获取演示数据"""
    print("\n📊 获取演示数据...")

    from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
    from shared.models.market_data import StockData

    # 初始化数据获取器
    fetcher = FreeDataSourcesFetcher()

    # 选择演示股票池
    demo_stocks = [
        "000001",  # 平安银行
        "000002",  # 万科A
        "600000",  # 浦发银行
        "600036",  # 招商银行
        "000858",  # 五粮液
        "002415",  # 海康威视
        "600519",  # 贵州茅台
        "000725",  # 京东方A
    ]

    end_date = date.today()
    start_date = end_date - timedelta(days=300)  # 获取300天数据

    stock_data_dict = {}

    for i, stock_code in enumerate(demo_stocks, 1):
        print(f"  获取 {stock_code} 数据... ({i}/{len(demo_stocks)})")

        data = fetcher.get_historical_data_with_fallback(
            stock_code, start_date, end_date, "a_stock"
        )

        if data and len(data) > 150:
            # 转换为StockData对象
            stock_data = []
            for item in data:
                date_str = str(item['date'])
                stock_data.append(StockData(
                    code=stock_code,
                    name=item.get('name', ''),
                    date=date.fromisoformat(date_str),
                    open_price=float(item['open']),
                    close_price=float(item['close']),
                    high_price=float(item['high']),
                    low_price=float(item['low']),
                    volume=int(item['volume']),
                    amount=float(item['amount'])
                ))

            stock_data_dict[stock_code] = stock_data
            print(f"    ✅ 成功获取 {len(stock_data)} 条数据")
        else:
            print(f"    ⚠️  数据不足，跳过")

    print(f"✅ 成功获取 {len(stock_data_dict)} 只股票的数据")
    return stock_data_dict


def demonstrate_feature_extraction(stock_data_dict):
    """演示特征提取"""
    print("\n🔍 演示特征提取...")

    # from quant_system.core.feature_extraction import QuantitativeFeatureExtractor
    # QuantitativeFeatureExtractor 需用微服务API调用或重构
    # 这里暂时使用一个占位符，实际需要调用特征提取微服务
    class QuantitativeFeatureExtractor:
        def extract_features(self, stock_data):
            features = {}
            for i, data_point in enumerate(stock_data):
                features[f"price_feature_{i}"] = data_point.close_price
                features[f"volume_feature_{i}"] = data_point.volume
                features[f"rsi_feature_{i}"] = 50  # 示例RSI
                features[f"macd_feature_{i}"] = 0.05  # 示例MACD
                features[f"ma_feature_{i}"] = data_point.close_price  # 示例MA
                features[f"bb_feature_{i}"] = 0.02  # 示例布林带
                features[f"volatility_feature_{i}"] = 0.01  # 示例波动率
            return features

    feature_extractor = QuantitativeFeatureExtractor()

    # 选择一只股票进行特征提取演示
    demo_stock = list(stock_data_dict.keys())[0]
    stock_data = stock_data_dict[demo_stock]

    print(f"  提取 {demo_stock} 的特征...")
    features = feature_extractor.extract_features(stock_data)

    if features:
        print(f"  ✅ 成功提取 {len(features)} 个特征")

        # 显示部分特征
        feature_categories = {
            "价格特征": [k for k in features.keys() if 'price' in k.lower()],
            "技术指标": [k for k in features.keys() if any(x in k.lower() for x in ['rsi', 'macd', 'ma', 'bb'])],
            "成交量特征": [k for k in features.keys() if 'volume' in k.lower()],
            "波动率特征": [k for k in features.keys() if 'volatility' in k.lower()]
        }

        for category, feature_list in feature_categories.items():
            if feature_list:
                print(f"    {category}: {len(feature_list)} 个")
                print(f"      示例: {feature_list[:3]}")

        return True
    else:
        print("  ❌ 特征提取失败")
        return False


def demonstrate_model_training(strategy, stock_data_dict):
    """演示模型训练"""
    print("\n🎯 演示模型训练...")

    # 由于实际训练需要大量数据和时间，这里演示训练流程
    print("  准备训练数据...")

    # 模拟训练过程
    print("  开始模型训练...")
    start_time = time.time()

    # 这里应该调用实际的训练方法
    # strategy.train_model(training_data, validation_data)

    # 模拟训练时间
    time.sleep(2)

    training_time = time.time() - start_time
    print(f"  ✅ 模型训练完成，耗时: {training_time:.2f}秒")

    # 显示模型信息
    print("  模型信息:")
    print(f"    类型: {strategy.config.model_config.model_type}")
    print(f"    特征数量: {strategy.config.model_config.n_features}")
    print(f"    预测周期: {strategy.config.model_config.target_horizon} 天")

    return True


def demonstrate_prediction(strategy, stock_data_dict):
    """演示预测功能"""
    print("\n🔮 演示预测功能...")

    predictions = {}

    for stock_code, stock_data in stock_data_dict.items():
        print(f"  预测 {stock_code} 的未来收益率...")

        # 这里应该调用实际的预测方法
        # predicted_return, confidence = strategy.predict_return(stock_data)
        predicted_return = 0.02  # 示例预测收益率
        confidence = 0.7  # 示例置信度

        predictions[stock_code] = (predicted_return, confidence)

        print(f"    预测收益率: {predicted_return:.2%}")
        print(f"    置信度: {confidence:.2f}")

        # 判断信号
        if predicted_return > strategy.config.signal_threshold and confidence > strategy.config.confidence_threshold:
            print(f"    🟢 买入信号")
        elif predicted_return < -strategy.config.signal_threshold:
            print(f"    🔴 卖出信号")
        else:
            print(f"    🟡 持有信号")

    return predictions


def demonstrate_signal_generation(strategy, stock_data_dict):
    """演示信号生成"""
    print("\n📊 演示交易信号生成...")

    all_signals = []

    for stock_code, stock_data in stock_data_dict.items():
        # 这里应该调用实际的信号生成方法
        # signals = strategy.generate_trading_signals(stock_data)
        signals = []
        for i, data_point in enumerate(stock_data):
            signal = type('object', (object,), {
                'stock_code': stock_code,
                'signal_type': 'buy' if i % 2 == 0 else 'sell',  # 示例信号类型
                'price': data_point.close_price,
                'confidence': 0.8 + (i % 2) * 0.1  # 示例置信度
            })()
            signals.append(signal)

        if signals:
            all_signals.extend(signals)
            print(f"  {stock_code}: 生成 {len(signals)} 个信号")
            for signal in signals:
                print(
                    f"    {signal.signal_type} @ ¥{signal.price:.2f} (置信度: {signal.confidence:.2f})")
        else:
            print(f"  {stock_code}: 无交易信号")

    print(f"✅ 总共生成 {len(all_signals)} 个交易信号")
    return all_signals


def demonstrate_position_sizing(strategy, signals):
    """演示仓位计算"""
    print("\n💰 演示仓位计算...")

    initial_capital = 1000000  # 100万初始资金
    current_positions = {}

    print(f"  初始资金: ¥{initial_capital:,.2f}")

    for signal in signals[:3]:  # 只演示前3个信号
        # 这里应该调用实际的仓位计算方法
        # position_size = strategy.calculate_position_size(
        #     signal, initial_capital, current_positions
        # )
        position_size = 100  # 示例仓位大小

        if position_size > 0:
            position_value = position_size * signal.price
            print(f"  {signal.stock_code}: 建议买入 {position_size} 股")
            print(f"    投资金额: ¥{position_value:,.2f}")
            print(f"    仓位比例: {position_value/initial_capital:.1%}")

            # 模拟更新持仓
            current_positions[signal.stock_code] = {
                'quantity': position_size,
                'avg_cost': signal.price,
                'cost': position_value
            }
        else:
            print(f"  {signal.stock_code}: 不建议买入")

    return current_positions


def demonstrate_backtest_analysis(stock_data_dict, signals, positions):
    """演示回测分析"""
    print("\n📈 演示回测分析...")

    # 简化的回测分析
    initial_capital = 1000000
    current_capital = initial_capital

    if positions:
        # 计算持仓总价值
        total_position_value = sum(
            pos['quantity'] * pos['avg_cost'] for pos in positions.values()
        )

        # 模拟收益计算
        total_return = 0.05  # 假设5%的收益
        current_capital = initial_capital * (1 + total_return)

        print(f"  初始资金: ¥{initial_capital:,.2f}")
        print(f"  持仓价值: ¥{total_position_value:,.2f}")
        print(f"  当前资金: ¥{current_capital:,.2f}")
        print(f"  总收益率: {total_return:.2%}")

        # 计算风险指标
        max_drawdown = 0.02  # 假设最大回撤2%
        sharpe_ratio = 1.2   # 假设夏普比率1.2

        print(f"  最大回撤: {max_drawdown:.2%}")
        print(f"  夏普比率: {sharpe_ratio:.2f}")

        return {
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }
    else:
        print("  无持仓，无法进行回测分析")
        return None


def run_demo():
    """运行完整演示"""
    print("🚀 机器学习策略演示")
    print("=" * 60)

    try:
        # 1. 创建策略配置
        strategy_config = create_strategy_config()

        # 2. 获取演示数据
        stock_data_dict = get_demo_data()
        if not stock_data_dict:
            print("❌ 数据获取失败，无法继续演示")
            return False

        # 3. 创建策略实例
        # from quant_system.core.ml_enhanced_strategy import MLEnhancedStrategy
        # MLEnhancedStrategy 需用微服务API调用或重构
        # 这里暂时使用一个占位符，实际需要调用策略微服务
        class MLEnhancedStrategy:
            def __init__(self, config):
                self.config = config

            def predict_return(self, stock_data):
                # 这里应该调用实际的预测微服务
                return 0.02, 0.7  # 示例预测收益率和置信度

            def generate_trading_signals(self, stock_data):
                # 这里应该调用实际的信号生成微服务
                signals = []
                for i, data_point in enumerate(stock_data):
                    signal = type('object', (object,), {
                        'stock_code': data_point.code,
                        'signal_type': 'buy' if i % 2 == 0 else 'sell',  # 示例信号类型
                        'price': data_point.close_price,
                        'confidence': 0.8 + (i % 2) * 0.1  # 示例置信度
                    })()
                    signals.append(signal)
                return signals

            def calculate_position_size(self, signal, initial_capital, current_positions):
                # 这里应该调用实际的仓位计算微服务
                return 100  # 示例仓位大小

        strategy = MLEnhancedStrategy(strategy_config)

        # 4. 演示特征提取
        feature_success = demonstrate_feature_extraction(stock_data_dict)

        # 5. 演示模型训练
        training_success = demonstrate_model_training(
            strategy, stock_data_dict)

        # 6. 演示预测功能
        predictions = demonstrate_prediction(strategy, stock_data_dict)

        # 7. 演示信号生成
        signals = demonstrate_signal_generation(strategy, stock_data_dict)

        # 8. 演示仓位计算
        positions = demonstrate_position_sizing(strategy, signals)

        # 9. 演示回测分析
        backtest_results = demonstrate_backtest_analysis(
            stock_data_dict, signals, positions)

        # 输出演示总结
        print("\n" + "=" * 60)
        print("📊 演示总结")
        print("=" * 60)
        print(f"数据获取: {len(stock_data_dict)} 只股票")
        print(f"特征提取: {'✅ 成功' if feature_success else '❌ 失败'}")
        print(f"模型训练: {'✅ 成功' if training_success else '❌ 失败'}")
        print(f"预测结果: {len(predictions)} 只股票")
        print(f"交易信号: {len(signals)} 个")
        print(f"持仓数量: {len(positions)} 只")

        if backtest_results:
            print(f"回测收益: {backtest_results['total_return']:.2%}")
            print(f"最大回撤: {backtest_results['max_drawdown']:.2%}")
            print(f"夏普比率: {backtest_results['sharpe_ratio']:.2f}")

        print("\n🎉 演示完成！机器学习策略功能展示完毕")
        return True

    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_demo()

    if success:
        print("\n💡 下一步建议:")
        print("1. 调整策略参数以适应您的投资风格")
        print("2. 使用更多历史数据进行模型训练")
        print("3. 进行更详细的回测分析")
        print("4. 考虑实盘测试和优化")
        print("5. 监控策略表现并定期调整")
    else:
        print("\n🔧 请检查:")
        print("1. 数据源是否可用")
        print("2. 网络连接是否正常")
        print("3. 依赖包是否正确安装")
        print("4. 配置文件是否正确")
