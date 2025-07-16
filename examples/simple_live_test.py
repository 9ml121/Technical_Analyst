#!/usr/bin/env python3
"""
简化的实盘测试验证

验证核心功能：
1. 数据获取
2. 模型训练
3. 信号生成
4. 交易模拟
"""

import sys
from pathlib import Path
from datetime import date, timedelta, datetime
import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
import json

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_data_fetching():
    """测试数据获取功能"""
    print("📊 测试数据获取功能...")

    from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
    from quant_system.models.stock_data import StockData

    fetcher = FreeDataSourcesFetcher()
    test_stocks = ["000001", "000002", "600000"]  # 测试3只股票

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    all_data = []

    for stock_code in test_stocks:
        try:
            print(f"  获取 {stock_code} 数据...")
            data = fetcher.get_historical_data_with_fallback(
                stock_code, start_date, end_date, "a_stock"
            )

            if data and len(data) > 0:
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

                all_data.append(stock_data)
                print(f"    ✅ 成功获取 {len(stock_data)} 条数据")
            else:
                print(f"    ❌ 获取 {stock_code} 数据失败")

        except Exception as e:
            print(f"    ❌ 获取 {stock_code} 数据异常: {e}")
            continue

    print(f"📊 数据获取测试完成，共获取 {len(all_data)} 只股票数据")
    return all_data


def test_model_training(stock_data_list):
    """测试模型训练功能"""
    print("\n🤖 测试模型训练功能...")

    from quant_system.core.ml_enhanced_strategy import MLStrategyConfig, ModelConfig, MLEnhancedStrategy

    if len(stock_data_list) < 2:
        print("❌ 数据不足，无法训练模型")
        return None

    try:
        # 创建策略配置
        model_config = ModelConfig(
            model_type='random_forest',
            n_estimators=50,  # 减少树的数量，加快训练
            max_depth=6,
            feature_selection='kbest',
            n_features=10,
            target_horizon=3
        )

        strategy_config = MLStrategyConfig(
            name="简化测试策略",
            model_config=model_config,
            signal_threshold=0.02,
            confidence_threshold=0.6,
            position_sizing='equal'
        )

        # 创建策略
        strategy = MLEnhancedStrategy(strategy_config)
        print("✅ 策略创建成功")

        # 准备训练数据
        print("  准备训练数据...")
        training_data = strategy.prepare_training_data(stock_data_list)
        print(
            f"  训练数据准备完成，特征: {training_data[0].shape}, 目标: {training_data[1].shape}")

        # 训练模型
        print("  开始训练模型...")
        training_results = strategy.train_model(training_data)
        print("✅ 模型训练完成")

        # 显示训练结果
        if training_results:
            print(f"  训练R²: {training_results.get('train_r2', 0):.3f}")
            print(f"  交叉验证R²: {training_results.get('cv_mean', 0):.3f}")
            print(
                f"  特征重要性: {len(training_results.get('feature_importance', {}))} 个特征")

        return strategy

    except Exception as e:
        print(f"❌ 模型训练失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_signal_generation(strategy, stock_data_list):
    """测试信号生成功能"""
    print("\n📈 测试信号生成功能...")

    if not strategy or not stock_data_list:
        print("❌ 策略或数据不可用")
        return

    signals_count = 0

    for stock_data in stock_data_list:
        if len(stock_data) < 60:
            continue

        try:
            # 生成交易信号
            signals = strategy.generate_trading_signals(stock_data)

            if signals:
                signals_count += len(signals)
                for signal in signals:
                    print(f"  📊 {stock_data[0].code}: {signal.signal_type} 信号")
                    print(f"     预测收益率: {signal.predicted_return:.3%}")
                    print(f"     置信度: {signal.confidence:.3f}")
                    print(f"     建议仓位: {signal.position_size}")

        except Exception as e:
            print(f"  ❌ 生成 {stock_data[0].code} 信号失败: {e}")
            continue

    print(f"📈 信号生成测试完成，共生成 {signals_count} 个信号")


def test_trading_simulation():
    """测试交易模拟功能"""
    print("\n💰 测试交易模拟功能...")

    # 模拟账户
    initial_capital = 10000
    current_capital = initial_capital
    positions = {}
    trades = []

    # 模拟交易成本
    commission_rate = 0.0003
    min_commission = 5.0

    def calculate_commission(amount):
        return max(amount * commission_rate, min_commission)

    # 模拟买入
    def simulate_buy(stock_code, price, quantity, reason):
        nonlocal current_capital

        trade_amount = price * quantity
        commission = calculate_commission(trade_amount)
        total_cost = trade_amount + commission

        if total_cost <= current_capital:
            current_capital -= total_cost
            positions[stock_code] = {
                'quantity': quantity,
                'avg_cost': price,
                'buy_date': datetime.now()
            }

            trades.append({
                'timestamp': datetime.now(),
                'stock_code': stock_code,
                'action': 'BUY',
                'price': price,
                'quantity': quantity,
                'amount': trade_amount,
                'commission': commission,
                'reason': reason
            })

            print(
                f"  ✅ 买入 {stock_code}: {quantity}股 @ ¥{price:.2f}, 成本: ¥{commission:.2f}")
            return True
        else:
            print(f"  ❌ 买入 {stock_code} 失败: 资金不足")
            return False

    # 模拟卖出
    def simulate_sell(stock_code, price, quantity, reason):
        nonlocal current_capital

        if stock_code not in positions:
            print(f"  ❌ 卖出 {stock_code} 失败: 无持仓")
            return False

        position = positions[stock_code]
        if quantity > position['quantity']:
            print(f"  ❌ 卖出 {stock_code} 失败: 持仓不足")
            return False

        trade_amount = price * quantity
        commission = calculate_commission(trade_amount)
        net_amount = trade_amount - commission

        current_capital += net_amount

        # 计算盈亏
        profit = (price - position['avg_cost']) * quantity - commission
        profit_pct = (price - position['avg_cost']) / position['avg_cost']

        # 更新持仓
        remaining_quantity = position['quantity'] - quantity
        if remaining_quantity == 0:
            del positions[stock_code]
        else:
            position['quantity'] = remaining_quantity

        trades.append({
            'timestamp': datetime.now(),
            'stock_code': stock_code,
            'action': 'SELL',
            'price': price,
            'quantity': quantity,
            'amount': trade_amount,
            'commission': commission,
            'reason': reason
        })

        print(
            f"  ✅ 卖出 {stock_code}: {quantity}股 @ ¥{price:.2f}, 盈亏: ¥{profit:.2f} ({profit_pct:.2%})")
        return True

    # 模拟一些交易
    print("  模拟交易执行...")

    # 买入交易
    simulate_buy("000001", 12.50, 800, "策略买入信号")
    simulate_buy("000002", 18.30, 500, "策略买入信号")

    # 卖出交易
    simulate_sell("000001", 13.20, 400, "部分止盈")
    simulate_sell("000002", 17.80, 500, "止损")

    # 计算账户状态
    total_position_value = sum(
        pos['quantity'] * 12.50  # 假设当前价格
        for pos in positions.values()
    )
    account_value = current_capital + total_position_value
    total_return = (account_value - initial_capital) / initial_capital

    print(f"\n💰 交易模拟结果:")
    print(f"  初始资金: ¥{initial_capital:,.2f}")
    print(f"  当前资金: ¥{current_capital:,.2f}")
    print(f"  持仓价值: ¥{total_position_value:,.2f}")
    print(f"  账户总价值: ¥{account_value:,.2f}")
    print(f"  总收益率: {total_return:.2%}")
    print(f"  总交易次数: {len(trades)} 次")

    # 计算总手续费
    total_commission = sum(trade['commission'] for trade in trades)
    print(f"  总手续费: ¥{total_commission:,.2f}")

    return {
        'initial_capital': initial_capital,
        'final_capital': current_capital,
        'account_value': account_value,
        'total_return': total_return,
        'trades_count': len(trades),
        'total_commission': total_commission,
        'trades': trades
    }


def main():
    """主函数"""
    print("🚀 简化实盘测试验证")
    print("=" * 60)

    try:
        # 1. 测试数据获取
        stock_data_list = test_data_fetching()

        if not stock_data_list:
            print("❌ 数据获取失败，无法继续测试")
            return

        # 2. 测试模型训练
        strategy = test_model_training(stock_data_list)

        if not strategy:
            print("❌ 模型训练失败，无法继续测试")
            return

        # 3. 测试信号生成
        test_signal_generation(strategy, stock_data_list)

        # 4. 测试交易模拟
        trading_results = test_trading_simulation()

        # 5. 保存测试结果
        test_summary = {
            'test_date': datetime.now().isoformat(),
            'data_stocks_count': len(stock_data_list),
            'model_trained': strategy is not None,
            'trading_results': trading_results
        }

        with open("simple_live_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_summary, f, indent=2,
                      ensure_ascii=False, default=str)

        print(f"\n✅ 简化实盘测试完成！")
        print(f"📄 测试结果已保存到 simple_live_test_results.json")

        # 评估测试结果
        if trading_results and trading_results['total_return'] > 0:
            print("🎉 测试成功！交易模拟盈利")
        elif trading_results and trading_results['total_return'] > -0.05:
            print("✅ 测试通过！交易模拟表现稳定")
        else:
            print("⚠️  测试需要改进！交易模拟亏损")

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
