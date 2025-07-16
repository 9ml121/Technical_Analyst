#!/usr/bin/env python3
"""
鲁棒策略训练系统 V3 - 解决过拟合问题

使用A股最近3个月涨幅最高的股票进行训练，
重点解决过拟合问题，确保能生成有效交易信号。
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
import calendar

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RobustStrategyTrainerV3:
    """鲁棒策略训练器 V3 - 解决过拟合问题"""

    def __init__(self):
        """初始化训练器"""
        self.training_data = []
        self.market_periods = {}
        self.strategy = None
        self.training_results = {}

        print("🚀 鲁棒策略训练系统 V3 初始化完成")

    def get_top_performing_stocks_data(self, years: int = 3) -> Dict[str, List]:
        """获取最近3个月内涨幅最高的股票数据"""
        print(f"📊 获取最近3个月涨幅最高的股票数据...")

        from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
        from quant_system.models.stock_data import StockData

        fetcher = FreeDataSourcesFetcher()

        # 计算3个月前的日期
        end_date = date.today()
        start_date = end_date - timedelta(days=90)  # 3个月

        print(f"  筛选时间范围: {start_date} 到 {end_date}")

        # 获取各板块涨幅前20的股票
        top_stocks = self._get_top_performing_stocks(
            fetcher, start_date, end_date)

        if not top_stocks:
            print("❌ 无法获取涨幅排名数据")
            return {}

        print(f"📊 筛选出 {len(top_stocks)} 只涨幅领先股票")
        print("  主板前20:", len([s for s in top_stocks if str(
            s).startswith('60') or str(s).startswith('00')]))
        print("  创业板前20:", len(
            [s for s in top_stocks if str(s).startswith('30')]))
        print("  科创板前20:", len(
            [s for s in top_stocks if str(s).startswith('68')]))

        all_stock_data = {}
        market_periods = {}

        for stock_code in top_stocks:
            try:
                print(f"  获取 {stock_code} 历史数据...")

                # 获取完整历史数据（3年）
                data_start_date = end_date - timedelta(days=years * 365)
                data = fetcher.get_historical_data_with_fallback(
                    stock_code, data_start_date, end_date, "a_stock"
                )

                if data and len(data) > 100:  # 确保有足够数据
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

                    all_stock_data[stock_code] = stock_data

                    # 分析市场环境
                    market_periods[stock_code] = self._analyze_market_periods(
                        stock_data)

                    print(f"    ✅ 成功获取 {len(stock_data)} 条数据")
                else:
                    print(f"    ❌ {stock_code} 数据不足")

            except Exception as e:
                print(f"    ❌ 获取 {stock_code} 数据异常: {e}")
                continue

        self.market_periods = market_periods
        print(f"📊 数据获取完成，共获取 {len(all_stock_data)} 只股票数据")

        return all_stock_data

    def _get_top_performing_stocks(self, fetcher, start_date: date, end_date: date) -> List[str]:
        """获取最近3个月内涨幅最高的股票"""
        print("🔍 筛选涨幅领先股票...")

        try:
            import akshare as ak

            # 获取A股所有股票列表
            stock_list = ak.stock_info_a_code_name()

            # 按板块分类
            main_board = []  # 主板 (60开头 + 00开头)
            gem_board = []   # 创业板 (30开头)
            star_board = []  # 科创板 (68开头)

            for _, row in stock_list.iterrows():
                code = row['code']
                name = row['name']

                # 排除ST股票和新上市股票
                if 'ST' in name or '*' in name:
                    continue

                # 按板块分类
                if str(code).startswith('60') or str(code).startswith('00'):
                    main_board.append(code)
                elif str(code).startswith('30'):
                    gem_board.append(code)
                elif str(code).startswith('68'):
                    star_board.append(code)

            print(f"  主板股票数量: {len(main_board)}")
            print(f"  创业板股票数量: {len(gem_board)}")
            print(f"  科创板股票数量: {len(star_board)}")

            # 计算各板块涨幅排名
            top_stocks = []

            # 处理主板
            print("  计算主板涨幅排名...")
            main_board_top = self._calculate_returns_ranking(
                fetcher, main_board, start_date, end_date, 20)
            top_stocks.extend(main_board_top)

            # 处理创业板
            print("  计算创业板涨幅排名...")
            gem_board_top = self._calculate_returns_ranking(
                fetcher, gem_board, start_date, end_date, 20)
            top_stocks.extend(gem_board_top)

            # 处理科创板
            print("  计算科创板涨幅排名...")
            star_board_top = self._calculate_returns_ranking(
                fetcher, star_board, start_date, end_date, 20)
            top_stocks.extend(star_board_top)

            print(f"✅ 筛选完成，共选出 {len(top_stocks)} 只涨幅领先股票")
            return top_stocks

        except Exception as e:
            print(f"❌ 获取涨幅排名失败: {e}")
            # 如果akshare失败，使用备用方案
            return self._get_fallback_stocks()

    def _calculate_returns_ranking(self, fetcher, stock_codes: List[str], start_date: date, end_date: date, top_n: int) -> List[str]:
        """计算股票涨幅排名"""
        returns_data = []

        for code in stock_codes[:100]:  # 限制处理数量，避免请求过多
            try:
                # 获取3个月数据
                data = fetcher.get_historical_data_with_fallback(
                    code, start_date, end_date, "a_stock"
                )

                if data and len(data) >= 10:  # 至少10个交易日
                    # 计算涨幅
                    first_price = float(data[0]['close'])
                    last_price = float(data[-1]['close'])
                    returns = (last_price - first_price) / first_price

                    returns_data.append({
                        'code': code,
                        'returns': returns,
                        'first_price': first_price,
                        'last_price': last_price
                    })

            except Exception as e:
                continue

        # 按涨幅排序，取前N名
        returns_data.sort(key=lambda x: x['returns'], reverse=True)
        top_stocks = [item['code'] for item in returns_data[:top_n]]

        print(f"    涨幅前{top_n}股票:")
        for i, item in enumerate(returns_data[:top_n]):
            print(f"      {i+1}. {item['code']}: {item['returns']:.2%}")

        return top_stocks

    def _get_fallback_stocks(self) -> List[str]:
        """备用股票池，如果涨幅计算失败则使用"""
        print("⚠️  使用备用股票池...")

        # 各板块代表性股票
        fallback_stocks = [
            # 主板前20
            "600519", "000858", "600036", "601318", "600887", "000001", "601166", "601328", "601398", "600276",
            "600104", "600309", "600690", "000002", "000568", "000333", "000651", "000776", "000895", "000423",

            # 创业板前20
            "300059", "300122", "300124", "300142", "300347", "300408", "300433", "300498", "300601", "300750",
            "300760", "300782", "300832", "300896", "300015", "300033", "300014", "300146", "300073", "300999",

            # 科创板前20
            "688001", "688002", "688003", "688005", "688008", "688009", "688012", "688018", "688019", "688020",
            "688021", "688022", "688023", "688025", "688026", "688027", "688028", "688029", "688030", "688031"
        ]

        return fallback_stocks

    def _analyze_market_periods(self, stock_data: List) -> Dict:
        """分析市场环境周期"""
        if len(stock_data) < 60:
            return {}

        # 按日期排序
        stock_data.sort(key=lambda x: x.date)

        # 计算价格序列
        prices = [d.close_price for d in stock_data]
        dates = [d.date for d in stock_data]

        # 计算移动平均线
        ma20 = []
        ma60 = []

        for i in range(len(prices)):
            if i >= 19:
                ma20.append(np.mean(prices[i-19:i+1]))
            else:
                ma20.append(prices[i])

            if i >= 59:
                ma60.append(np.mean(prices[i-59:i+1]))
            else:
                ma60.append(prices[i])

        # 分析市场环境
        periods = {
            'bull_market': [],    # 牛市
            'bear_market': [],    # 熊市
            'sideways_market': []  # 震荡市
        }

        for i in range(60, len(prices)):
            current_date = dates[i]
            current_price = prices[i]
            current_ma20 = ma20[i]
            current_ma60 = ma60[i]

            # 计算趋势强度
            trend_strength = (current_ma20 - current_ma60) / current_ma60

            # 计算波动率
            if i >= 20:
                returns = [(prices[j] - prices[j-1]) / prices[j-1]
                           for j in range(i-19, i+1)]
                volatility = np.std(returns)
            else:
                volatility = 0

            # 判断市场环境
            if trend_strength > 0.05 and current_price > current_ma20 > current_ma60:
                periods['bull_market'].append(current_date)
            elif trend_strength < -0.05 and current_price < current_ma20 < current_ma60:
                periods['bear_market'].append(current_date)
            else:
                periods['sideways_market'].append(current_date)

        return periods

    def create_robust_strategy_v3(self):
        """创建鲁棒策略 V3 - 解决过拟合问题"""
        print("🤖 创建鲁棒策略 V3...")

        from quant_system.core.ml_enhanced_strategy import MLStrategyConfig, ModelConfig, MLEnhancedStrategy

        # 创建鲁棒策略配置 - 重点解决过拟合问题
        model_config = ModelConfig(
            model_type='random_forest',      # 随机森林，减少过拟合
            n_estimators=100,                # 减少树数量
            max_depth=3,                     # 降低深度，控制过拟合
            feature_selection='rfe',         # 递归特征消除
            n_features=15,                   # 减少特征数量
            target_horizon=5                 # 预测5日收益率
        )

        strategy_config = MLStrategyConfig(
            name="短期爆发力策略V3",
            model_config=model_config,
            signal_threshold=0.001,          # 更低信号阈值，确保有信号生成
            confidence_threshold=0.25,       # 更低置信度门槛，确保信号生成
            position_sizing='kelly',
            risk_management={
                "max_position_pct": 0.10,    # 单股最大仓位更严格
                "max_positions": 15,         # 持仓更分散
                "stop_loss_pct": 0.05,       # 更严格的止损
                "take_profit_pct": 0.15,     # 更保守的止盈
                "max_drawdown_pct": 0.08,
                "min_confidence": 0.50       # 降低最小置信度要求
            }
        )

        self.strategy = MLEnhancedStrategy(strategy_config)
        print("✅ 鲁棒策略 V3 创建完成")

    def train_robust_model_v3(self, stock_data_list: List[List]):
        """训练鲁棒模型 V3 - 解决过拟合问题"""
        print("🎯 开始训练鲁棒模型 V3...")

        if len(stock_data_list) < 5:
            print("❌ 训练数据不足，需要至少5只股票")
            return False

        try:
            # 准备训练数据
            print("  准备训练数据...")
            training_data = self.strategy.prepare_training_data(
                stock_data_list)

            if training_data[0].empty or training_data[1].empty:
                print("❌ 训练数据为空")
                return False

            print(
                f"  训练数据准备完成，特征: {training_data[0].shape}, 目标: {training_data[1].shape}")

            # 训练模型
            print("  开始训练模型...")
            training_results = self.strategy.train_model(training_data)

            if training_results:
                self.training_results = training_results
                print("✅ 鲁棒模型 V3 训练完成")

                # 显示训练结果
                print(f"  训练R²: {training_results.get('train_r2', 0):.3f}")
                print(f"  交叉验证R²: {training_results.get('cv_mean', 0):.3f}")
                print(
                    f"  特征重要性: {len(training_results.get('feature_importance', {}))} 个特征")

                # 显示重要特征
                feature_importance = training_results.get(
                    'feature_importance', {})
                if feature_importance:
                    print("  重要特征 (前10):")
                    sorted_features = sorted(
                        feature_importance.items(), key=lambda x: x[1], reverse=True)
                    for i, (feature, importance) in enumerate(sorted_features[:10]):
                        print(f"    {i+1}. {feature}: {importance:.4f}")

                # 检查过拟合
                train_r2 = training_results.get('train_r2', 0)
                cv_r2 = training_results.get('cv_mean', 0)

                if train_r2 - cv_r2 > 0.3:
                    print("⚠️  检测到过拟合，建议调整模型参数")
                else:
                    print("✅ 模型泛化能力良好")

                return True
            else:
                print("❌ 模型训练失败")
                return False

        except Exception as e:
            print(f"❌ 模型训练异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_robust_signals_v3(self, stock_data_list: List[List]) -> List[Dict]:
        """生成鲁棒交易信号 V3 - 确保有信号生成"""
        print("📈 生成鲁棒交易信号 V3...")

        if not self.strategy:
            print("❌ 策略未训练")
            return []

        all_signals = []

        for stock_data in stock_data_list:
            if len(stock_data) < 60:
                continue

            try:
                # 生成交易信号
                signals = self.strategy.generate_trading_signals(stock_data)

                if signals:
                    for signal in signals:
                        # 计算预测收益率（从信号原因中提取）
                        predicted_return = 0.0
                        if hasattr(signal, 'predicted_return'):
                            predicted_return = signal.predicted_return
                        elif 'ML预测收益率' in signal.reason:
                            try:
                                import re
                                match = re.search(
                                    r'ML预测收益率: ([-\d.]+)%', signal.reason)
                                if match:
                                    predicted_return = float(
                                        match.group(1)) / 100
                            except:
                                pass

                        # 计算建议仓位
                        position_size = 0.0
                        if hasattr(signal, 'position_size'):
                            position_size = signal.position_size
                        else:
                            # 基于置信度计算建议仓位
                            position_size = signal.confidence * 0.10  # 最大10%仓位

                        signal_info = {
                            'stock_code': stock_data[0].code,
                            'signal_type': signal.signal_type.value if hasattr(signal.signal_type, 'value') else str(signal.signal_type),
                            'predicted_return': predicted_return,
                            'confidence': signal.confidence,
                            'position_size': position_size,
                            'date': stock_data[-1].date,
                            'current_price': stock_data[-1].close_price,
                            'reason': signal.reason
                        }
                        all_signals.append(signal_info)

                        print(
                            f"  📊 {stock_data[0].code}: {signal.signal_type} 信号")
                        print(f"     预测收益率: {predicted_return:.3%}")
                        print(f"     置信度: {signal.confidence:.3f}")
                        print(f"     建议仓位: {position_size:.1%}")
                        print(f"     原因: {signal.reason}")

            except Exception as e:
                print(f"  ❌ 生成 {stock_data[0].code} 信号失败: {e}")
                continue

        print(f"📈 信号生成完成，共生成 {len(all_signals)} 个信号")
        return all_signals

    def analyze_market_adaptability_v3(self, signals: List[Dict]) -> Dict:
        """分析市场适应性 V3"""
        print("🔍 分析市场适应性 V3...")

        adaptability_analysis = {
            'total_signals': len(signals),
            'buy_signals': len([s for s in signals if s['signal_type'] == 'BUY']),
            'sell_signals': len([s for s in signals if s['signal_type'] == 'SELL']),
            'avg_confidence': np.mean([s['confidence'] for s in signals]) if signals else 0,
            'avg_predicted_return': np.mean([s['predicted_return'] for s in signals]) if signals else 0,
            'market_periods_coverage': {}
        }

        # 分析不同市场环境下的信号分布
        for stock_code, periods in self.market_periods.items():
            stock_signals = [
                s for s in signals if s['stock_code'] == stock_code]

            if stock_signals:
                adaptability_analysis['market_periods_coverage'][stock_code] = {
                    'total_signals': len(stock_signals),
                    'bull_market_signals': 0,
                    'bear_market_signals': 0,
                    'sideways_market_signals': 0
                }

        print(f"🔍 市场适应性分析完成")
        print(f"  总信号数: {adaptability_analysis['total_signals']}")
        print(f"  买入信号: {adaptability_analysis['buy_signals']}")
        print(f"  卖出信号: {adaptability_analysis['sell_signals']}")
        print(f"  平均置信度: {adaptability_analysis['avg_confidence']:.3f}")
        print(
            f"  平均预测收益率: {adaptability_analysis['avg_predicted_return']:.3%}")

        return adaptability_analysis

    def save_training_results_v3(self, signals: List[Dict], adaptability: Dict):
        """保存训练结果 V3"""
        print("💾 保存训练结果 V3...")

        results = {
            'training_date': datetime.now().isoformat(),
            'strategy_name': '鲁棒多因子策略V3',
            'training_results': self.training_results,
            'market_periods': self.market_periods,
            'signals': signals,
            'adaptability_analysis': adaptability,
            'model_performance': {
                'train_r2': self.training_results.get('train_r2', 0),
                'cv_mean': self.training_results.get('cv_mean', 0),
                'overfitting_score': self.training_results.get('train_r2', 0) - self.training_results.get('cv_mean', 0),
                'feature_count': len(self.training_results.get('feature_importance', {})),
                'top_features': self.training_results.get('top_features', [])
            }
        }

        with open("robust_strategy_training_results_v3.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        print("✅ 训练结果已保存到 robust_strategy_training_results_v3.json")

    def run_robust_training_v3(self):
        """运行鲁棒训练流程 V3"""
        print("🚀 开始鲁棒策略训练流程 V3")
        print("=" * 60)

        try:
            # 1. 获取历史数据
            all_stock_data = self.get_top_performing_stocks_data(years=3)

            if not all_stock_data:
                print("❌ 无法获取历史数据")
                return False

            # 2. 创建鲁棒策略 V3
            self.create_robust_strategy_v3()

            # 3. 训练模型 V3
            stock_data_list = list(all_stock_data.values())
            if not self.train_robust_model_v3(stock_data_list):
                print("❌ 模型训练失败")
                return False

            # 4. 生成信号 V3
            signals = self.generate_robust_signals_v3(stock_data_list)

            # 5. 分析市场适应性 V3
            adaptability = self.analyze_market_adaptability_v3(signals)

            # 6. 保存结果 V3
            self.save_training_results_v3(signals, adaptability)

            print("\n🎉 鲁棒策略训练 V3 完成！")

            # 评估结果
            if adaptability['total_signals'] > 0:
                if adaptability['avg_confidence'] > 0.5:
                    print("✅ 策略表现良好，置信度较高")
                else:
                    print("⚠️  策略需要优化，置信度偏低")

                if adaptability['avg_predicted_return'] > 0.01:
                    print("✅ 预测收益率合理")
                else:
                    print("⚠️  预测收益率偏低，需要调整")
            else:
                print("⚠️  未生成有效信号，需要进一步调整参数")

            return True

        except Exception as e:
            print(f"❌ 训练流程异常: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    print("🚀 鲁棒策略训练系统 V3")
    print("=" * 60)

    trainer = RobustStrategyTrainerV3()
    success = trainer.run_robust_training_v3()

    if success:
        print("\n💡 下一步建议:")
        print("1. 分析训练结果，评估策略表现")
        print("2. 根据市场适应性分析调整策略参数")
        print("3. 进行回测验证策略有效性")
        print("4. 考虑增加更多股票和更长时间数据")
        print("5. 准备进行实盘测试")
    else:
        print("\n🔧 请检查:")
        print("1. 网络连接是否正常")
        print("2. 数据源是否可用")
        print("3. 训练参数是否合理")
        print("4. 系统资源是否充足")


if __name__ == "__main__":
    main()
