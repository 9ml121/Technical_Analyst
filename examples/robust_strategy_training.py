#!/usr/bin/env python3
"""
鲁棒策略训练系统

使用A股最近3年奇数月历史数据进行训练和信号生成，
确保覆盖牛市、熊市、震荡市等不同市场环境，提升策略适应性。
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


class RobustStrategyTrainer:
    """鲁棒策略训练器"""

    def __init__(self):
        """初始化训练器"""
        self.training_data = []
        self.market_periods = {}
        self.strategy = None
        self.training_results = {}

        print("🚀 鲁棒策略训练系统初始化完成")

    def get_odd_months_data(self, years: int = 3) -> Dict[str, List]:
        """获取最近N年的奇数月数据"""
        print(f"📊 获取最近{years}年奇数月历史数据...")

        from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
        from quant_system.models.stock_data import StockData

        fetcher = FreeDataSourcesFetcher()

        # 选择代表性股票，覆盖不同行业和市值，扩展到140支
        representative_stocks = [
            # 金融板块（25支）
            "000001", "600036", "601318", "601166", "601328", "601398", "601288", "601988", "600000", "600015",
            "600016", "601939", "601818", "601377", "601229", "601288", "601998", "601009", "601169", "601818",
            "601688", "600837", "601211", "601229", "601818",
            # 消费板块（30支）
            "000858", "600519", "000568", "000333", "000651", "600887", "600690", "600104", "600809", "600276",
            "600309", "600887", "600690", "600104", "600809", "600276", "600309", "000651", "000333", "000568",
            "000002", "000629", "000625", "000776", "000895", "000423", "000651", "000333", "000568", "000002",
            # 科技板块（35支）
            "002415", "000725", "002594", "300750", "300014", "300015", "300033", "300059", "300122", "300124",
            "300142", "300144", "300347", "300408", "300433", "300450", "300496", "300601", "300628", "300661",
            "300672", "300676", "300677", "300708", "300724", "300750", "300760", "300782", "300896", "300999",
            "600703", "600745", "600764", "600845", "600850",
            # 医药板块（25支）
            "600276", "600196", "600085", "600867", "600763", "600276", "600196", "600085", "600867", "600763",
            "000423", "000513", "000538", "000566", "000623", "000661", "000704", "000756", "000788", "000809",
            "000915", "000963", "000999", "002007", "002262",
            # 周期板块（15支）
            "600019", "600028", "600031", "600050", "600104", "600188", "600196", "600219", "600256", "600282",
            "600309", "600362", "600369", "600426", "600438",
            # 新能源板块（10支）
            "300750", "300014", "300015", "300033", "300059", "300122", "300124", "300142", "300144", "300347",
            # 大盘股（部分重复，市值>1000亿，60支）
            "600519", "601318", "601166", "601328", "601398", "601288", "601988", "600000", "600015", "600016",
            "601939", "601818", "601377", "601229", "601288", "601998", "601009", "601169", "601818", "601688",
            "600837", "601211", "601229", "601818", "000001", "600036", "000858", "000568", "000333", "000651",
            "600887", "600690", "600104", "600809", "600276", "600309", "000002", "000629", "000625", "000776",
            "000895", "000423", "000651", "000333", "000568", "000002", "002415", "000725", "002594", "300750",
            "300014", "300015", "300033", "300059", "300122", "300124", "300142", "300144",
            # 中盘股（50支，100-1000亿）
            "600703", "600745", "600764", "600845", "600850", "600276", "600196", "600085", "600867", "600763",
            "000423", "000513", "000538", "000566", "000623", "000661", "000704", "000756", "000788", "000809",
            "000915", "000963", "000999", "002007", "002262", "600019", "600028", "600031", "600050", "600104",
            "600188", "600196", "600219", "600256", "600282", "600309", "600362", "600369", "600426", "600438",
            "300750", "300014", "300015", "300033", "300059", "300122", "300124", "300142", "300144", "300347",
            # 小盘股（30支，<100亿）
            "300601", "300628", "300661", "300672", "300676", "300677", "300708", "300724", "300760", "300782",
            "300896", "300999", "600703", "600745", "600764", "600845", "600850", "600276", "600196", "600085",
            "600867", "600763", "000423", "000513", "000538", "000566", "000623", "000661", "000704", "000756"
        ]
        # 去重
        representative_stocks = list(set(representative_stocks))[:140]  # 保证数量为140支

        end_date = date.today()
        start_date = end_date - timedelta(days=years * 365)

        all_stock_data = {}
        market_periods = {}

        for stock_code in representative_stocks:
            try:
                print(f"  获取 {stock_code} 历史数据...")

                # 获取完整历史数据
                data = fetcher.get_historical_data_with_fallback(
                    stock_code, start_date, end_date, "a_stock"
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

    def filter_odd_months_data(self, all_stock_data: Dict[str, List]) -> List[List]:
        """筛选奇数月数据"""
        print("🔍 筛选奇数月数据...")

        odd_months_data = []

        for stock_code, stock_data in all_stock_data.items():
            # 筛选奇数月数据
            odd_month_data = []

            for data_point in stock_data:
                if data_point.date.month % 2 == 1:  # 奇数月
                    odd_month_data.append(data_point)

            if len(odd_month_data) > 30:  # 确保有足够数据
                odd_months_data.append(odd_month_data)
                print(f"  {stock_code}: {len(odd_month_data)} 条奇数月数据")

        print(f"🔍 奇数月数据筛选完成，共 {len(odd_months_data)} 只股票")
        return odd_months_data

    def create_robust_strategy(self):
        """创建鲁棒策略"""
        print("🤖 创建鲁棒策略...")

        from quant_system.core.ml_enhanced_strategy import MLStrategyConfig, ModelConfig, MLEnhancedStrategy

        # 创建鲁棒策略配置
        model_config = ModelConfig(
            model_type='gradient_boosting',  # 建议用梯度提升树提升泛化
            n_estimators=400,                # 增加树数量提升复杂度
            max_depth=8,                     # 控制过拟合
            learning_rate=0.05,              # 降低步长提升鲁棒性
            feature_selection='rfe',         # 递归特征消除
            n_features=40,                   # 保留更多特征
            target_horizon=5                 # 预测5天收益率
        )

        strategy_config = MLStrategyConfig(
            name="鲁棒多因子策略",
            model_config=model_config,
            signal_threshold=0.02,           # 略微降低信号阈值，提升信号数量
            confidence_threshold=0.60,       # 降低置信度门槛，兼顾覆盖面
            position_sizing='kelly',
            risk_management={
                "max_position_pct": 0.12,    # 单股最大仓位更严格
                "max_positions": 12,         # 持仓更分散
                "stop_loss_pct": 0.07,
                "take_profit_pct": 0.18,
                "max_drawdown_pct": 0.10,
                "min_confidence": 0.60
            }
        )

        self.strategy = MLEnhancedStrategy(strategy_config)
        print("✅ 鲁棒策略创建完成")

    def train_robust_model(self, stock_data_list: List[List]):
        """训练鲁棒模型"""
        print("🎯 开始训练鲁棒模型...")

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
                print("✅ 鲁棒模型训练完成")

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

                return True
            else:
                print("❌ 模型训练失败")
                return False

        except Exception as e:
            print(f"❌ 模型训练异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_robust_signals(self, stock_data_list: List[List]) -> List[Dict]:
        """生成鲁棒交易信号"""
        print("📈 生成鲁棒交易信号...")

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
                                match = re.search(r'ML预测收益率: ([-\d.]+)%', signal.reason)
                                if match:
                                    predicted_return = float(match.group(1)) / 100
                            except:
                                pass
                        
                        # 计算建议仓位
                        position_size = 0.0
                        if hasattr(signal, 'position_size'):
                            position_size = signal.position_size
                        else:
                            # 基于置信度计算建议仓位
                            position_size = signal.confidence * 0.15  # 最大15%仓位
                        
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

                        print(f"  📊 {stock_data[0].code}: {signal.signal_type} 信号")
                        print(f"     预测收益率: {predicted_return:.3%}")
                        print(f"     置信度: {signal.confidence:.3f}")
                        print(f"     建议仓位: {position_size:.1%}")
                        print(f"     原因: {signal.reason}")

            except Exception as e:
                print(f"  ❌ 生成 {stock_data[0].code} 信号失败: {e}")
                continue

        print(f"📈 信号生成完成，共生成 {len(all_signals)} 个信号")
        return all_signals

    def analyze_market_adaptability(self, signals: List[Dict]) -> Dict:
        """分析市场适应性"""
        print("🔍 分析市场适应性...")

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

    def save_training_results(self, signals: List[Dict], adaptability: Dict):
        """保存训练结果"""
        print("💾 保存训练结果...")

        results = {
            'training_date': datetime.now().isoformat(),
            'strategy_name': '鲁棒多因子策略',
            'training_results': self.training_results,
            'market_periods': self.market_periods,
            'signals': signals,
            'adaptability_analysis': adaptability,
            'model_performance': {
                'train_r2': self.training_results.get('train_r2', 0),
                'cv_mean': self.training_results.get('cv_mean', 0),
                'feature_count': len(self.training_results.get('feature_importance', {})),
                'top_features': self.training_results.get('top_features', [])
            }
        }

        with open("robust_strategy_training_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        print("✅ 训练结果已保存到 robust_strategy_training_results.json")

    def run_robust_training(self):
        """运行鲁棒训练流程"""
        print("🚀 开始鲁棒策略训练流程")
        print("=" * 60)

        try:
            # 1. 获取历史数据
            all_stock_data = self.get_odd_months_data(years=3)

            if not all_stock_data:
                print("❌ 无法获取历史数据")
                return False

            # 2. 筛选奇数月数据
            odd_months_data = self.filter_odd_months_data(all_stock_data)

            if len(odd_months_data) < 5:
                print("❌ 奇数月数据不足")
                return False

            # 3. 创建鲁棒策略
            self.create_robust_strategy()

            # 4. 训练模型
            if not self.train_robust_model(odd_months_data):
                print("❌ 模型训练失败")
                return False

            # 5. 生成信号
            signals = self.generate_robust_signals(odd_months_data)

            # 6. 分析市场适应性
            adaptability = self.analyze_market_adaptability(signals)

            # 7. 保存结果
            self.save_training_results(signals, adaptability)

            print("\n🎉 鲁棒策略训练完成！")

            # 评估结果
            if adaptability['total_signals'] > 0:
                if adaptability['avg_confidence'] > 0.6:
                    print("✅ 策略表现良好，置信度较高")
                else:
                    print("⚠️  策略需要优化，置信度偏低")

                if adaptability['avg_predicted_return'] > 0.02:
                    print("✅ 预测收益率合理")
                else:
                    print("⚠️  预测收益率偏低，需要调整")
            else:
                print("⚠️  未生成有效信号，需要检查数据质量")

            return True

        except Exception as e:
            print(f"❌ 训练流程异常: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    print("🚀 鲁棒策略训练系统")
    print("=" * 60)

    trainer = RobustStrategyTrainer()
    success = trainer.run_robust_training()

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
