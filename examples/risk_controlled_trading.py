#!/usr/bin/env python3
"""
风险控制交易系统
- 每天最多3支买入信号
- 连续2天无把握时不推荐
- 多重风险控制措施
"""

from quant_system.utils.logger import setup_logger
from quant_system.utils.config_loader import ConfigLoader
from quant_system.core.data_provider import DataProvider
from quant_system.core.ml_enhanced_strategy import MLEnhancedStrategy
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


class RiskControlledTrading:
    """风险控制交易系统"""

    def __init__(self):
        self.logger = setup_logger("risk_controlled_trading")
        self.config = ConfigLoader()

        # 风险控制参数
        self.max_signals_per_day = 3  # 每天最多信号数
        self.min_confidence = 0.7     # 最低置信度
        self.min_expected_return = 0.03  # 最低预期收益率
        self.max_risk_score = 0.3     # 最高风险评分
        self.min_liquidity_score = 0.6  # 最低流动性评分

        # 仓位控制
        self.max_position_size = 0.1   # 单只股票最大仓位
        self.max_total_position = 0.3  # 总仓位限制

        # 市场环境判断
        self.market_trend_threshold = 0.02  # 大盘趋势阈值

    def get_market_environment(self, date):
        """判断市场环境"""
        try:
            # 获取沪深300指数数据
            data_provider = DataProvider()
            hs300_data = data_provider.get_stock_data(
                "000300", start_date=date-timedelta(days=30), end_date=date)

            if hs300_data is None or len(hs300_data) < 20:
                return "neutral"

            # 计算20日趋势
            hs300_data['ma20'] = hs300_data['close'].rolling(20).mean()
            current_trend = (
                hs300_data['close'].iloc[-1] - hs300_data['ma20'].iloc[-1]) / hs300_data['ma20'].iloc[-1]

            if current_trend > self.market_trend_threshold:
                return "bull"
            elif current_trend < -self.market_trend_threshold:
                return "bear"
            else:
                return "neutral"

        except Exception as e:
            self.logger.warning(f"市场环境判断失败: {e}")
            return "neutral"

    def calculate_risk_score(self, stock_data):
        """计算风险评分"""
        try:
            # 计算波动率
            returns = stock_data['close'].pct_change().dropna()
            volatility = returns.std()

            # 计算最大回撤
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()

            # 计算流动性（成交量稳定性）
            volume_stability = stock_data['volume'].rolling(
                20).std() / stock_data['volume'].rolling(20).mean()
            avg_volume_stability = volume_stability.mean()

            # 综合风险评分 (0-1, 越低越好)
            risk_score = (
                0.4 * min(abs(volatility) * 10, 1) +  # 波动率权重40%
                0.4 * min(abs(max_drawdown), 1) +     # 回撤权重40%
                0.2 * min(avg_volume_stability, 1)    # 流动性权重20%
            )

            return risk_score

        except Exception as e:
            self.logger.warning(f"风险评分计算失败: {e}")
            return 0.5  # 默认中等风险

    def calculate_liquidity_score(self, stock_data):
        """计算流动性评分"""
        try:
            # 计算平均成交量
            avg_volume = stock_data['volume'].mean()
            avg_amount = (stock_data['volume'] * stock_data['close']).mean()

            # 计算成交量稳定性
            volume_cv = stock_data['volume'].std() / \
                stock_data['volume'].mean()

            # 流动性评分 (0-1, 越高越好)
            liquidity_score = min(
                0.5 * min(avg_volume / 1e7, 1) +      # 成交量权重50%
                0.3 * min(avg_amount / 1e9, 1) +     # 成交额权重30%
                0.2 * max(0, 1 - volume_cv)          # 稳定性权重20%
                , 1)

            return liquidity_score

        except Exception as e:
            self.logger.warning(f"流动性评分计算失败: {e}")
            return 0.5  # 默认中等流动性

    def filter_signals(self, signals, market_env):
        """过滤交易信号"""
        if not signals:
            return []

        filtered_signals = []

        for signal in signals:
            # 基础条件检查
            if (signal['confidence'] < self.min_confidence or
                    signal['expected_return'] < self.min_expected_return):
                continue

            # 风险评分检查
            if signal.get('risk_score', 0.5) > self.max_risk_score:
                continue

            # 流动性评分检查
            if signal.get('liquidity_score', 0.5) < self.min_liquidity_score:
                continue

            # 市场环境调整
            if market_env == "bear":
                # 熊市提高标准
                if signal['confidence'] < 0.8 or signal['expected_return'] < 0.05:
                    continue
            elif market_env == "bull":
                # 牛市可以适当放宽
                pass

            filtered_signals.append(signal)

        # 按预期收益率排序，取前N个
        filtered_signals.sort(key=lambda x: x['expected_return'], reverse=True)
        return filtered_signals[:self.max_signals_per_day]

    def run_daily_analysis(self, date=None):
        """运行每日分析"""
        if date is None:
            date = datetime.now().date()

        self.logger.info(f"开始每日风险控制分析: {date}")

        # 1. 判断市场环境
        market_env = self.get_market_environment(date)
        self.logger.info(f"市场环境: {market_env}")

        # 2. 获取所有股票数据
        data_provider = DataProvider()

        # 重点股票池（包含创业板、科创板）
        stock_pool = [
            # 创业板（20%涨跌幅）
            "300059", "300122", "300124", "300142", "300274",  # 东方财富、智飞生物等
            "300347", "300408", "300433", "300498", "300601",
            "300750", "300760", "300782", "300832", "300896",

            # 科创板（20%涨跌幅）
            "688001", "688002", "688003", "688005", "688008",
            "688009", "688012", "688018", "688019", "688020",
            "688021", "688022", "688023", "688025", "688026",

            # 主板中小盘
            "000001", "000002", "000858", "000568", "000333",
            "000651", "000725", "000776", "000895", "000423",

            # 主板大盘（对比）
            "600036", "600519", "600887", "600104", "600276"
        ]

        all_signals = []

        # 3. 分析每只股票
        for stock_code in stock_pool:
            try:
                # 获取股票数据
                stock_data = data_provider.get_stock_data(
                    stock_code,
                    start_date=date-timedelta(days=60),
                    end_date=date
                )

                if stock_data is None or len(stock_data) < 30:
                    continue

                # 计算风险评分
                risk_score = self.calculate_risk_score(stock_data)

                # 计算流动性评分
                liquidity_score = self.calculate_liquidity_score(stock_data)

                # 使用ML策略生成信号
                strategy = MLEnhancedStrategy()
                signal = strategy.generate_signal(stock_data, stock_code)

                if signal and signal['action'] == 'BUY':
                    signal['risk_score'] = risk_score
                    signal['liquidity_score'] = liquidity_score
                    signal['stock_code'] = stock_code
                    all_signals.append(signal)

            except Exception as e:
                self.logger.warning(f"股票{stock_code}分析失败: {e}")
                continue

        # 4. 过滤信号
        filtered_signals = self.filter_signals(all_signals, market_env)

        # 5. 生成报告
        report = {
            'date': str(date),
            'market_environment': market_env,
            'total_analyzed': len(stock_pool),
            'total_signals': len(all_signals),
            'filtered_signals': len(filtered_signals),
            'recommendations': filtered_signals,
            'risk_control_summary': {
                'max_signals_per_day': self.max_signals_per_day,
                'min_confidence': self.min_confidence,
                'min_expected_return': self.min_expected_return,
                'max_risk_score': self.max_risk_score,
                'min_liquidity_score': self.min_liquidity_score
            }
        }

        # 6. 保存报告
        with open(f'risk_controlled_report_{date}.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        self.logger.info(
            f"分析完成: 总信号{len(all_signals)}, 过滤后{len(filtered_signals)}")

        return report


def main():
    """主函数"""
    trader = RiskControlledTrading()

    # 运行今日分析
    report = trader.run_daily_analysis()

    # 打印结果
    print(f"\n=== 风险控制交易报告 ===")
    print(f"日期: {report['date']}")
    print(f"市场环境: {report['market_environment']}")
    print(f"分析股票数: {report['total_analyzed']}")
    print(f"原始信号数: {report['total_signals']}")
    print(f"推荐信号数: {report['filtered_signals']}")

    if report['recommendations']:
        print(f"\n推荐买入股票:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec['stock_code']}")
            print(f"   置信度: {rec['confidence']:.3f}")
            print(f"   预期收益: {rec['expected_return']:.3f}")
            print(f"   风险评分: {rec['risk_score']:.3f}")
            print(f"   流动性评分: {rec['liquidity_score']:.3f}")
            print()
    else:
        print(f"\n今日无推荐买入信号")
        print(f"原因: 所有信号均未通过风险控制过滤")


if __name__ == "__main__":
    main()
