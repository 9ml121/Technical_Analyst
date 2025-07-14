#!/usr/bin/env python3
"""
回测系统示例

演示如何使用量化投资系统进行策略回测
"""

import sys
from pathlib import Path
from datetime import date, datetime

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from quant_system.utils.config_loader import ConfigLoader
from quant_system.utils.logger import get_logger

# 初始化日志
logger = get_logger(__name__)

def main():
    """主函数"""
    print("📈 量化投资系统 - 回测示例")
    print("=" * 50)
    
    try:
        # 1. 加载配置
        print("\n⚙️ 加载配置...")
        config_loader = ConfigLoader()
        
        # 加载默认配置
        default_config = config_loader.load_config('default')
        print(f"✅ 默认配置加载完成")
        
        # 加载策略配置
        try:
            strategy_config = config_loader.load_strategy_config('momentum_strategy')
            print(f"✅ 策略配置加载完成: {strategy_config.get('strategy_info', {}).get('name', 'N/A')}")
        except Exception as e:
            print(f"⚠️ 策略配置加载失败: {e}")
            print("使用默认策略配置...")
            strategy_config = create_default_strategy_config()
        
        # 2. 创建回测配置
        print("\n📊 创建回测配置...")
        backtest_config = create_backtest_config(default_config)
        
        print(f"  起始日期: {backtest_config['start_date']}")
        print(f"  结束日期: {backtest_config['end_date']}")
        print(f"  初始资金: ¥{backtest_config['initial_capital']:,.0f}")
        print(f"  最大持仓: {backtest_config['max_positions']} 只")
        print(f"  手续费率: {backtest_config['commission_rate']:.4f}")
        
        # 3. 模拟回测执行
        print("\n🚀 开始回测...")
        backtest_result = simulate_backtest(backtest_config, strategy_config)
        
        # 4. 显示回测结果
        print("\n📋 回测结果:")
        display_backtest_results(backtest_result)
        
        # 5. 性能分析
        print("\n📊 性能分析:")
        performance_metrics = calculate_performance_metrics(backtest_result)
        display_performance_metrics(performance_metrics)
        
        # 6. 风险分析
        print("\n⚠️ 风险分析:")
        risk_metrics = calculate_risk_metrics(backtest_result)
        display_risk_metrics(risk_metrics)
        
        # 7. 交易统计
        print("\n📈 交易统计:")
        trade_stats = calculate_trade_statistics(backtest_result)
        display_trade_statistics(trade_stats)
        
        print("\n✅ 回测示例完成！")
        
    except Exception as e:
        logger.error(f"回测执行出错: {e}", exc_info=True)
        print(f"\n❌ 回测执行出错: {e}")

def create_default_strategy_config():
    """创建默认策略配置"""
    return {
        'strategy_info': {
            'name': '默认动量策略',
            'version': '1.0.0',
            'description': '基于价格动量的选股策略',
            'strategy_type': 'momentum'
        },
        'selection_criteria': {
            'basic_criteria': {
                'consecutive_days': 3,
                'min_total_return': 0.15,
                'max_drawdown': 0.05
            },
            'price_filters': {
                'min_stock_price': 5.0,
                'max_stock_price': 200.0
            },
            'volume_filters': {
                'min_avg_volume': 10000000,
                'min_turnover_rate': 0.01
            }
        },
        'risk_management': {
            'stop_loss': {
                'method': 'percentage',
                'percentage': 0.05
            },
            'take_profit': {
                'method': 'percentage',
                'percentage': 0.20
            }
        }
    }

def create_backtest_config(default_config):
    """创建回测配置"""
    backtest_config = default_config.get('backtest', {})
    
    return {
        'start_date': backtest_config.get('start_date', '2023-01-01'),
        'end_date': backtest_config.get('end_date', '2024-01-01'),
        'initial_capital': backtest_config.get('initial_capital', 1000000.0),
        'max_positions': backtest_config.get('max_positions', 5),
        'position_size_pct': backtest_config.get('position_size_pct', 0.20),
        'commission_rate': backtest_config.get('commission_rate', 0.0003),
        'stamp_tax_rate': backtest_config.get('stamp_tax_rate', 0.001),
        'slippage_rate': backtest_config.get('slippage_rate', 0.001),
        'min_commission': backtest_config.get('min_commission', 5.0),
        'benchmark': backtest_config.get('benchmark', '000300.SH')
    }

def simulate_backtest(backtest_config, strategy_config):
    """模拟回测执行"""
    print("  📅 加载历史数据...")
    print("  🎯 执行选股策略...")
    print("  💰 模拟交易执行...")
    print("  📊 计算收益和风险...")
    
    # 模拟回测结果
    import random
    random.seed(42)  # 确保结果可重现
    
    # 模拟日度收益率
    trading_days = 250  # 一年约250个交易日
    daily_returns = []
    cumulative_return = 0
    max_drawdown = 0
    peak_value = backtest_config['initial_capital']
    
    for day in range(trading_days):
        # 模拟日收益率 (正态分布)
        daily_return = random.gauss(0.001, 0.02)  # 平均0.1%，标准差2%
        daily_returns.append(daily_return)
        
        # 计算累计收益
        cumulative_return = (1 + cumulative_return) * (1 + daily_return) - 1
        current_value = backtest_config['initial_capital'] * (1 + cumulative_return)
        
        # 更新最大回撤
        if current_value > peak_value:
            peak_value = current_value
        else:
            drawdown = (peak_value - current_value) / peak_value
            max_drawdown = max(max_drawdown, drawdown)
    
    # 模拟交易记录
    trades = []
    for i in range(20):  # 模拟20笔交易
        trade = {
            'date': f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            'code': f"{random.randint(0,999):03d}{random.randint(0,999):03d}",
            'name': f"股票{i+1}",
            'action': random.choice(['buy', 'sell']),
            'price': random.uniform(10, 50),
            'quantity': random.randint(100, 1000) * 100,
            'amount': 0,
            'commission': 0,
            'profit': random.uniform(-1000, 2000) if random.choice([True, False]) else 0
        }
        trade['amount'] = trade['price'] * trade['quantity']
        trade['commission'] = max(trade['amount'] * backtest_config['commission_rate'], 
                                backtest_config['min_commission'])
        trades.append(trade)
    
    final_value = backtest_config['initial_capital'] * (1 + cumulative_return)
    
    return {
        'config': backtest_config,
        'strategy': strategy_config,
        'start_date': backtest_config['start_date'],
        'end_date': backtest_config['end_date'],
        'initial_capital': backtest_config['initial_capital'],
        'final_capital': final_value,
        'total_return': cumulative_return,
        'daily_returns': daily_returns,
        'max_drawdown': max_drawdown,
        'trades': trades,
        'trading_days': trading_days
    }

def display_backtest_results(result):
    """显示回测结果"""
    print(f"  回测期间: {result['start_date']} 至 {result['end_date']}")
    print(f"  初始资金: ¥{result['initial_capital']:,.0f}")
    print(f"  最终资金: ¥{result['final_capital']:,.0f}")
    print(f"  总收益: ¥{result['final_capital'] - result['initial_capital']:,.0f}")
    print(f"  总收益率: {result['total_return']:+.2%}")
    print(f"  最大回撤: {result['max_drawdown']:.2%}")
    print(f"  交易次数: {len(result['trades'])} 次")

def calculate_performance_metrics(result):
    """计算性能指标"""
    daily_returns = result['daily_returns']
    trading_days = len(daily_returns)
    
    # 年化收益率
    annual_return = (1 + result['total_return']) ** (252 / trading_days) - 1
    
    # 波动率
    import statistics
    volatility = statistics.stdev(daily_returns) * (252 ** 0.5)
    
    # 夏普比率 (假设无风险利率为3%)
    risk_free_rate = 0.03
    sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
    
    # 索提诺比率
    downside_returns = [r for r in daily_returns if r < 0]
    downside_volatility = statistics.stdev(downside_returns) * (252 ** 0.5) if downside_returns else 0
    sortino_ratio = (annual_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0
    
    # 卡尔玛比率
    calmar_ratio = annual_return / result['max_drawdown'] if result['max_drawdown'] > 0 else 0
    
    return {
        'annual_return': annual_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'calmar_ratio': calmar_ratio,
        'max_drawdown': result['max_drawdown']
    }

def display_performance_metrics(metrics):
    """显示性能指标"""
    print(f"  年化收益率: {metrics['annual_return']:+.2%}")
    print(f"  年化波动率: {metrics['volatility']:.2%}")
    print(f"  夏普比率: {metrics['sharpe_ratio']:.2f}")
    print(f"  索提诺比率: {metrics['sortino_ratio']:.2f}")
    print(f"  卡尔玛比率: {metrics['calmar_ratio']:.2f}")

def calculate_risk_metrics(result):
    """计算风险指标"""
    daily_returns = result['daily_returns']
    
    # VaR (95%置信度)
    sorted_returns = sorted(daily_returns)
    var_95 = sorted_returns[int(len(sorted_returns) * 0.05)]
    
    # CVaR (条件风险价值)
    cvar_95 = sum(sorted_returns[:int(len(sorted_returns) * 0.05)]) / int(len(sorted_returns) * 0.05)
    
    # 最大连续亏损天数
    max_consecutive_losses = 0
    current_consecutive = 0
    
    for ret in daily_returns:
        if ret < 0:
            current_consecutive += 1
            max_consecutive_losses = max(max_consecutive_losses, current_consecutive)
        else:
            current_consecutive = 0
    
    return {
        'var_95': var_95,
        'cvar_95': cvar_95,
        'max_consecutive_losses': max_consecutive_losses,
        'max_drawdown': result['max_drawdown']
    }

def display_risk_metrics(metrics):
    """显示风险指标"""
    print(f"  VaR (95%): {metrics['var_95']:+.2%}")
    print(f"  CVaR (95%): {metrics['cvar_95']:+.2%}")
    print(f"  最大回撤: {metrics['max_drawdown']:.2%}")
    print(f"  最大连续亏损: {metrics['max_consecutive_losses']} 天")

def calculate_trade_statistics(result):
    """计算交易统计"""
    trades = result['trades']
    
    # 买入和卖出交易
    buy_trades = [t for t in trades if t['action'] == 'buy']
    sell_trades = [t for t in trades if t['action'] == 'sell']
    
    # 盈利交易
    profitable_trades = [t for t in trades if t.get('profit', 0) > 0]
    losing_trades = [t for t in trades if t.get('profit', 0) < 0]
    
    # 胜率
    win_rate = len(profitable_trades) / len(trades) if trades else 0
    
    # 平均盈利和亏损
    avg_profit = sum(t['profit'] for t in profitable_trades) / len(profitable_trades) if profitable_trades else 0
    avg_loss = sum(t['profit'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
    
    # 盈亏比
    profit_loss_ratio = abs(avg_profit / avg_loss) if avg_loss != 0 else 0
    
    # 总手续费
    total_commission = sum(t['commission'] for t in trades)
    
    return {
        'total_trades': len(trades),
        'buy_trades': len(buy_trades),
        'sell_trades': len(sell_trades),
        'win_rate': win_rate,
        'profitable_trades': len(profitable_trades),
        'losing_trades': len(losing_trades),
        'avg_profit': avg_profit,
        'avg_loss': avg_loss,
        'profit_loss_ratio': profit_loss_ratio,
        'total_commission': total_commission
    }

def display_trade_statistics(stats):
    """显示交易统计"""
    print(f"  总交易次数: {stats['total_trades']} 次")
    print(f"  买入交易: {stats['buy_trades']} 次")
    print(f"  卖出交易: {stats['sell_trades']} 次")
    print(f"  盈利交易: {stats['profitable_trades']} 次")
    print(f"  亏损交易: {stats['losing_trades']} 次")
    print(f"  胜率: {stats['win_rate']:.2%}")
    print(f"  平均盈利: ¥{stats['avg_profit']:,.0f}")
    print(f"  平均亏损: ¥{stats['avg_loss']:,.0f}")
    print(f"  盈亏比: {stats['profit_loss_ratio']:.2f}")
    print(f"  总手续费: ¥{stats['total_commission']:,.0f}")

def demo_strategy_comparison():
    """演示策略对比"""
    print("\n" + "="*50)
    print("🔄 策略对比演示")
    print("="*50)
    
    strategies = [
        {'name': '动量策略', 'return': 0.15, 'volatility': 0.18, 'sharpe': 0.83},
        {'name': '均值回归', 'return': 0.12, 'volatility': 0.15, 'sharpe': 0.80},
        {'name': '技术指标', 'return': 0.18, 'volatility': 0.22, 'sharpe': 0.82},
        {'name': '基准指数', 'return': 0.08, 'volatility': 0.16, 'sharpe': 0.50}
    ]
    
    print(f"{'策略名称':<12} {'年化收益':<10} {'波动率':<10} {'夏普比率':<10}")
    print("-" * 50)
    
    for strategy in strategies:
        print(f"{strategy['name']:<12} {strategy['return']:<10.2%} "
              f"{strategy['volatility']:<10.2%} {strategy['sharpe']:<10.2f}")

if __name__ == "__main__":
    # 运行主要示例
    main()
    
    # 运行策略对比演示
    demo_strategy_comparison()
    
    print("\n🎉 回测示例运行完成！")
    print("\n💡 提示:")
    print("  - 这是模拟回测结果，实际结果可能不同")
    print("  - 请根据实际需求调整策略参数")
    print("  - 建议进行多次回测验证策略稳定性")
    print("  - 实盘前请充分测试和验证策略")
