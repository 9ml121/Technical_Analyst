#!/usr/bin/env python3
"""
简化版风险控制交易系统
- 每天最多3支买入信号
- 多重风险控制措施
- 避免复杂模块依赖
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
import warnings
warnings.filterwarnings('ignore')

# 设置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("simple_risk_control")


class SimpleRiskControl:
    """简化版风险控制交易系统"""

    def __init__(self):
        # 风险控制参数
        self.max_signals_per_day = 3  # 每天最多信号数
        self.min_confidence = 0.6     # 降低最低置信度
        self.min_expected_return = 0.02  # 降低最低预期收益率
        self.max_risk_score = 0.5     # 提高最高风险评分容忍度
        self.min_liquidity_score = 0.4  # 降低最低流动性评分

        # 仓位控制
        self.max_position_size = 0.1   # 单只股票最大仓位
        self.max_total_position = 0.3  # 总仓位限制

        # 市场环境判断
        self.market_trend_threshold = 0.02  # 大盘趋势阈值

        # 模拟股票池（包含创业板、科创板）
        self.stock_pool = [
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

    def generate_mock_data(self, stock_code):
        """生成模拟股票数据"""
        try:
            # 生成60天的模拟数据
            dates = pd.date_range(end=datetime.now(), periods=60, freq='D')

            # 模拟价格数据
            base_price = 20 + np.random.random() * 30  # 20-50元
            price_changes = np.random.normal(0, 0.02, 60)  # 2%日波动
            prices = [base_price]

            for change in price_changes[1:]:
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 1))  # 最低1元

            # 模拟成交量数据
            base_volume = 1e6 + np.random.random() * 5e6  # 100万-600万
            volumes = np.random.normal(base_volume, base_volume * 0.3, 60)
            volumes = np.maximum(volumes, 1e5)  # 最低10万

            # 创建DataFrame
            data = pd.DataFrame({
                'date': dates,
                'open': prices,
                'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
                'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
                'close': prices,
                'volume': volumes
            })

            return data

        except Exception as e:
            logger.warning(f"生成模拟数据失败: {e}")
            return None

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
            logger.warning(f"风险评分计算失败: {e}")
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
            logger.warning(f"流动性评分计算失败: {e}")
            return 0.5  # 默认中等流动性

    def generate_signal(self, stock_data, stock_code):
        """生成交易信号"""
        try:
            # 计算技术指标
            returns = stock_data['close'].pct_change().dropna()
            recent_return = returns.tail(5).mean()  # 5日平均收益
            volatility = returns.tail(20).std()     # 20日波动率

            # 计算动量指标
            momentum_5d = (stock_data['close'].iloc[-1] /
                           stock_data['close'].iloc[-6] - 1) if len(stock_data) > 5 else 0
            momentum_10d = (
                stock_data['close'].iloc[-1] / stock_data['close'].iloc[-11] - 1) if len(stock_data) > 10 else 0

            # 计算成交量指标
            volume_ratio = stock_data['volume'].tail(
                5).mean() / stock_data['volume'].tail(20).mean()

            # 信号生成逻辑
            confidence = 0.5  # 基础置信度
            expected_return = 0.03  # 基础预期收益

            # 根据指标调整
            if momentum_5d > 0.02:  # 5日涨幅>2%
                confidence += 0.2
                expected_return += 0.02

            if momentum_10d > 0.05:  # 10日涨幅>5%
                confidence += 0.15
                expected_return += 0.015

            if volume_ratio > 1.2:  # 成交量放大
                confidence += 0.1
                expected_return += 0.01

            if volatility < 0.025:  # 波动率较低
                confidence += 0.05

            # 创业板、科创板加分
            if stock_code.startswith(('300', '688')):
                confidence += 0.1
                expected_return += 0.01

            # 限制范围
            confidence = min(confidence, 0.95)
            expected_return = min(expected_return, 0.15)

            # 判断是否生成买入信号
            if confidence > 0.6 and expected_return > 0.03:
                return {
                    'action': 'BUY',
                    'confidence': confidence,
                    'expected_return': expected_return,
                    'stock_code': stock_code,
                    'momentum_5d': momentum_5d,
                    'momentum_10d': momentum_10d,
                    'volume_ratio': volume_ratio,
                    'volatility': volatility
                }

            return None

        except Exception as e:
            logger.warning(f"信号生成失败: {e}")
            return None

    def filter_signals(self, signals, market_env="neutral"):
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

    def run_daily_analysis(self):
        """运行每日分析"""
        date = datetime.now().date()
        logger.info(f"开始每日风险控制分析: {date}")

        all_signals = []

        # 分析每只股票
        for stock_code in self.stock_pool:
            try:
                # 获取股票数据（模拟）
                stock_data = self.generate_mock_data(stock_code)

                if stock_data is None or len(stock_data) < 30:
                    continue

                # 计算风险评分
                risk_score = self.calculate_risk_score(stock_data)

                # 计算流动性评分
                liquidity_score = self.calculate_liquidity_score(stock_data)

                # 生成信号
                signal = self.generate_signal(stock_data, stock_code)

                if signal and signal['action'] == 'BUY':
                    signal['risk_score'] = risk_score
                    signal['liquidity_score'] = liquidity_score
                    all_signals.append(signal)

            except Exception as e:
                logger.warning(f"股票{stock_code}分析失败: {e}")
                continue

        # 过滤信号
        filtered_signals = self.filter_signals(all_signals)

        # 生成报告
        report = {
            'date': str(date),
            'market_environment': 'neutral',  # 简化版暂时固定
            'total_analyzed': len(self.stock_pool),
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

        # 保存报告
        with open(f'simple_risk_report_{date}.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"分析完成: 总信号{len(all_signals)}, 过滤后{len(filtered_signals)}")

        return report


def main():
    """主函数"""
    trader = SimpleRiskControl()

    # 运行今日分析
    report = trader.run_daily_analysis()

    # 打印结果
    print(f"\n=== 简化版风险控制交易报告 ===")
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
            print(f"   5日动量: {rec['momentum_5d']:.3f}")
            print(f"   10日动量: {rec['momentum_10d']:.3f}")
            print(f"   成交量比: {rec['volume_ratio']:.3f}")
            print()
    else:
        print(f"\n今日无推荐买入信号")
        print(f"原因: 所有信号均未通过风险控制过滤")
        print(f"风险控制标准:")
        print(f"- 最低置信度: {trader.min_confidence}")
        print(f"- 最低预期收益: {trader.min_expected_return}")
        print(f"- 最高风险评分: {trader.max_risk_score}")
        print(f"- 最低流动性评分: {trader.min_liquidity_score}")


if __name__ == "__main__":
    main()
