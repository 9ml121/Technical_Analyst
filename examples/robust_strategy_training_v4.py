#!/usr/bin/env python3
"""
鲁棒策略训练系统 V4 - 高性能版本

使用并行处理、缓存优化和批量处理大幅提升训练速度
支持大规模股票池训练（1000+股票）
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
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp
from functools import partial
import warnings
warnings.filterwarnings('ignore')

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HighPerformanceTrainerV4:
    """高性能策略训练器 V4"""

    def __init__(self, max_workers: int = None, use_processes: bool = False):
        """
        初始化高性能训练器

        Args:
            max_workers: 最大工作线程/进程数
            use_processes: 是否使用进程池（CPU密集型任务）
        """
        self.max_workers = max_workers or 1  # 降低到1，减少并发压力
        self.use_processes = False  # 强制使用线程池，避免进程间通信开销
        self.training_data = []
        self.market_periods = {}
        self.strategy = None
        self.training_results = {}

        # 性能统计
        self.performance_stats = {
            'data_fetch_time': 0,
            'processing_time': 0,
            'training_time': 0,
            'total_time': 0
        }

        print(f"🚀 高性能训练器初始化完成")
        print(f"   工作线程数: {self.max_workers}")
        print(f"   使用进程池: {self.use_processes}")

    def get_top_performing_stocks(self, start_date: date, end_date: date) -> List[str]:
        """获取涨幅最高的股票（并行处理）"""
        print(f"🔍 并行获取涨幅领先股票...")

        try:
            from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
            fetcher = FreeDataSourcesFetcher()

            # 获取所有A股代码
            all_stocks = self._get_all_a_stocks(fetcher)
            print(f"   获取到 {len(all_stocks)} 只A股")

            # 并行计算涨幅
            stock_returns = self._calculate_returns_parallel(
                fetcher, all_stocks, start_date, end_date)

            # 按板块分类并排序
            top_stocks = self._select_top_stocks_by_board(stock_returns)

            print(f"✅ 筛选完成，共 {len(top_stocks)} 只股票")
            return top_stocks

        except Exception as e:
            print(f"❌ 获取涨幅数据失败: {e}")
            return []

    def _get_all_a_stocks(self, fetcher) -> List[str]:
        """获取所有A股代码"""
        try:
            # 使用akshare获取股票列表
            import akshare as ak

            stock_codes = []

            # 获取A股股票列表
            try:
                df = ak.stock_info_a_code_name()
                if not df.empty:
                    # 提取股票代码
                    codes = df['code'].tolist()
                    stock_codes.extend(
                        [code for code in codes if self._is_valid_stock(code)])
                    print(f"   从akshare获取到 {len(stock_codes)} 只A股")
            except Exception as e:
                print(f"   ⚠️ akshare获取股票列表失败: {e}")

            # 如果akshare失败，使用默认股票池
            if not stock_codes:
                print("   ⚠️ 使用默认股票池")
                return self._get_default_stock_pool()

            # 限制数量避免过载
            return stock_codes[:1000]

        except Exception as e:
            print(f"⚠️ 获取股票列表失败，使用默认股票池: {e}")
            return self._get_default_stock_pool()

    def _is_valid_stock(self, code: str) -> bool:
        """检查股票是否有效"""
        code_str = str(code)
        # 排除ST股票和新股
        if 'ST' in code_str or '*' in code_str:
            return False
        # 排除特殊代码
        if len(code_str) != 6:
            return False
        return True

    def _get_default_stock_pool(self) -> List[str]:
        """获取默认股票池"""
        # 返回3只代表性股票进行极简测试
        return [
            '000001',  # 平安银行
            '000002',  # 万科A
            '600036'   # 招商银行
        ]

    def _calculate_returns_parallel(self, fetcher, stock_codes: List[str],
                                    start_date: date, end_date: date) -> Dict[str, float]:
        """并行计算股票涨幅"""
        print(f"   并行计算 {len(stock_codes)} 只股票的涨幅...")

        # 分批处理，避免内存溢出
        batch_size = 50
        all_returns = {}

        for i in range(0, len(stock_codes), batch_size):
            batch = stock_codes[i:i + batch_size]
            print(
                f"   处理批次 {i//batch_size + 1}/{(len(stock_codes) + batch_size - 1)//batch_size}")

            batch_returns = self._process_stock_batch(
                fetcher, batch, start_date, end_date)
            all_returns.update(batch_returns)

        return all_returns

    def _process_stock_batch(self, fetcher, stock_codes: List[str],
                             start_date: date, end_date: date) -> Dict[str, float]:
        """处理一批股票"""
        executor_class = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor

        with executor_class(max_workers=self.max_workers) as executor:
            # 提交任务
            future_to_code = {
                executor.submit(self._calculate_single_stock_return, fetcher, code, start_date, end_date): code
                for code in stock_codes
            }

            # 收集结果
            returns = {}
            for future in as_completed(future_to_code):
                code = future_to_code[future]
                try:
                    result = future.result(timeout=30)  # 30秒超时
                    if result is not None:
                        returns[code] = result
                    # 添加请求间隔，降低API频率
                    time.sleep(1)
                except Exception as e:
                    print(f"   ⚠️ 计算股票 {code} 涨幅失败: {e}")
                    time.sleep(1)  # 即使失败也要等待
                    continue

        return returns

    def _calculate_single_stock_return(self, fetcher, code: str,
                                       start_date: date, end_date: date) -> float:
        """计算单只股票的涨幅"""
        try:
            # 获取历史数据
            data = fetcher.get_historical_data_with_fallback(
                code, start_date, end_date)
            if not data or len(data) < 10:  # 至少需要10天数据
                return None

            # 计算涨幅
            if len(data) >= 2:
                start_price = data[0].get('close', 0)
                end_price = data[-1].get('close', 0)

                if start_price > 0:
                    return (end_price - start_price) / start_price

            return None

        except Exception as e:
            return None

    def _select_top_stocks_by_board(self, stock_returns: Dict[str, float]) -> List[str]:
        """按板块选择涨幅最高的股票"""
        # 按板块分类
        main_board = []
        gem_board = []
        star_board = []

        for code, return_rate in stock_returns.items():
            if return_rate is None:
                continue

            code_str = str(code)
            if code_str.startswith(('60', '00')):
                main_board.append((code, return_rate))
            elif code_str.startswith('30'):
                gem_board.append((code, return_rate))
            elif code_str.startswith('68'):
                star_board.append((code, return_rate))

        # 按涨幅排序，选择前20
        main_board.sort(key=lambda x: x[1], reverse=True)
        gem_board.sort(key=lambda x: x[1], reverse=True)
        star_board.sort(key=lambda x: x[1], reverse=True)

        # 选择前20只
        top_stocks = []
        top_stocks.extend([code for code, _ in main_board[:20]])
        top_stocks.extend([code for code, _ in gem_board[:20]])
        top_stocks.extend([code for code, _ in star_board[:20]])

        print(
            f"   主板前20: {len([s for s in top_stocks if str(s).startswith(('60', '00'))])}")
        print(
            f"   创业板前20: {len([s for s in top_stocks if str(s).startswith('30')])}")
        print(
            f"   科创板前20: {len([s for s in top_stocks if str(s).startswith('68')])}")

        return top_stocks

    def get_odd_months_data(self, years: int = 3) -> Dict[str, List]:
        """获取奇数月份数据（高性能版本）"""
        print(f"📊 获取奇数月份数据...")

        start_time = time.time()

        # 获取涨幅最高的股票
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        top_stocks = self.get_top_performing_stocks(start_date, end_date)

        if not top_stocks:
            print("❌ 无法获取涨幅排名数据")
            return {}

        # 并行获取历史数据
        stock_data = self._get_historical_data_parallel(top_stocks, years)

        self.performance_stats['data_fetch_time'] = time.time() - start_time
        print(f"✅ 数据获取完成，耗时: {self.performance_stats['data_fetch_time']:.2f}s")

        return stock_data

    def _get_historical_data_parallel(self, stock_codes: List[str], years: int) -> Dict[str, List]:
        """并行获取历史数据"""
        print(f"   并行获取 {len(stock_codes)} 只股票的历史数据...")

        try:
            from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
            from quant_system.models.stock_data import StockData

            fetcher = FreeDataSourcesFetcher()

            # 计算时间范围
            end_date = date.today()
            start_date = end_date - timedelta(days=365 * years)

            # 分批处理
            batch_size = 20
            all_data = {}

            for i in range(0, len(stock_codes), batch_size):
                batch = stock_codes[i:i + batch_size]
                print(
                    f"   处理批次 {i//batch_size + 1}/{(len(stock_codes) + batch_size - 1)//batch_size}")

                batch_data = self._process_data_batch(
                    fetcher, batch, start_date, end_date)
                all_data.update(batch_data)

            return all_data

        except Exception as e:
            print(f"❌ 获取历史数据失败: {e}")
            return {}

    def _process_data_batch(self, fetcher, stock_codes: List[str],
                            start_date: date, end_date: date) -> Dict[str, List]:
        """处理一批股票的历史数据"""
        executor_class = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor

        with executor_class(max_workers=self.max_workers) as executor:
            # 提交任务
            future_to_code = {
                executor.submit(self._get_single_stock_history, fetcher, code, start_date, end_date): code
                for code in stock_codes
            }

            # 收集结果
            batch_data = {}
            for future in as_completed(future_to_code):
                code = future_to_code[future]
                try:
                    result = future.result(timeout=60)  # 60秒超时
                    if result:
                        batch_data[code] = result
                    # 添加请求间隔，降低API频率
                    time.sleep(1)
                except Exception as e:
                    print(f"   ⚠️ 获取股票 {code} 历史数据失败: {e}")
                    time.sleep(1)  # 即使失败也要等待
                    continue

        return batch_data

    def _get_single_stock_history(self, fetcher, code: str,
                                  start_date: date, end_date: date) -> List:
        """获取单只股票的历史数据"""
        try:
            data = fetcher.get_historical_data_with_fallback(
                code, start_date, end_date)
            if data and len(data) > 30:  # 至少需要30天数据
                return data
            return None
        except Exception as e:
            return None

    def train_strategy(self, stock_data: Dict[str, List]) -> Dict[str, Any]:
        """训练策略（高性能版本）"""
        print(f"🎯 开始高性能策略训练...")

        start_time = time.time()

        try:
            from quant_system.core.ml_enhanced_strategy import MLEnhancedStrategy, MLStrategyConfig, ModelConfig

            # 创建鲁棒策略配置
            model_config = ModelConfig(
                model_type='random_forest',
                n_estimators=100,
                max_depth=3,
                feature_selection='rfe',
                n_features=15,
                target_horizon=5
            )

            strategy_config = MLStrategyConfig(
                name="高性能鲁棒策略V4",
                model_config=model_config,
                signal_threshold=0.01,  # 降低信号阈值
                confidence_threshold=0.4,  # 降低置信度要求
                position_sizing='equal',
                risk_management={
                    "max_position_pct": 0.20,
                    "max_positions": 10,
                    "stop_loss_pct": 0.05,
                    "take_profit_pct": 0.10,
                    "max_drawdown_pct": 0.10,
                    "min_confidence": 0.4
                }
            )

            # 创建策略实例
            self.strategy = MLEnhancedStrategy(strategy_config)

            # 准备训练数据
            print(f"   准备训练数据...")
            training_data = self.strategy.prepare_training_data(stock_data)

            if not training_data or len(training_data) < 100:
                print(
                    f"❌ 训练数据不足: {len(training_data) if training_data else 0}")
                return {}

            # 训练模型
            print(f"   开始模型训练...")
            training_results = self.strategy.train_model(training_data)

            self.performance_stats['training_time'] = time.time() - start_time
            print(f"✅ 训练完成，耗时: {self.performance_stats['training_time']:.2f}s")

            return training_results

        except Exception as e:
            print(f"❌ 策略训练失败: {e}")
            return {}

    def generate_signals(self, stock_data: Dict[str, List]) -> List[Dict[str, Any]]:
        """生成交易信号（高性能版本）"""
        print(f"📈 生成交易信号...")

        if not self.strategy:
            print("❌ 策略未训练")
            return []

        try:
            # 并行生成信号
            signals = self.strategy.generate_signals(stock_data)

            # 过滤和排序信号
            filtered_signals = []
            for signal in signals:
                if signal.confidence >= 0.4 and signal.signal_type == 'buy':
                    filtered_signals.append({
                        'stock_code': signal.stock_code,
                        'signal_type': signal.signal_type,
                        'confidence': signal.confidence,
                        'predicted_return': signal.predicted_return,
                        'reason': signal.reason
                    })

            # 按置信度排序
            filtered_signals.sort(key=lambda x: x['confidence'], reverse=True)

            print(f"✅ 生成 {len(filtered_signals)} 个有效信号")
            return filtered_signals

        except Exception as e:
            print(f"❌ 信号生成失败: {e}")
            return []

    def run_training_pipeline(self) -> Dict[str, Any]:
        """运行完整的高性能训练流程"""
        print("🚀 高性能鲁棒策略训练系统 V4")
        print("=" * 60)

        start_time = time.time()

        try:
            # 1. 获取训练数据
            stock_data = self.get_odd_months_data(years=3)

            if not stock_data:
                print("❌ 无法获取训练数据")
                return {}

            print(f"📊 获取到 {len(stock_data)} 只股票的训练数据")

            # 2. 训练策略
            training_results = self.train_strategy(stock_data)

            if not training_results:
                print("❌ 策略训练失败")
                return {}

            # 3. 生成信号
            signals = self.generate_signals(stock_data)

            # 4. 汇总结果
            self.training_results = {
                'training_results': training_results,
                'signals': signals,
                'performance_stats': self.performance_stats,
                'stock_count': len(stock_data),
                'signal_count': len(signals),
                'timestamp': datetime.now().isoformat()
            }

            self.performance_stats['total_time'] = time.time() - start_time

            # 5. 保存结果
            self._save_results()

            # 6. 打印总结
            self._print_summary()

            return self.training_results

        except Exception as e:
            print(f"❌ 训练流程失败: {e}")
            return {}

    def _save_results(self):
        """保存训练结果"""
        try:
            results_file = "robust_strategy_training_results_v4.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_results, f,
                          ensure_ascii=False, indent=2)
            print(f"💾 结果已保存到: {results_file}")
        except Exception as e:
            print(f"⚠️ 保存结果失败: {e}")

    def _print_summary(self):
        """打印训练总结"""
        print("\n" + "=" * 60)
        print("🎉 高性能训练完成总结")
        print("=" * 60)

        stats = self.performance_stats
        results = self.training_results

        print(f"📊 数据统计:")
        print(f"   股票数量: {results.get('stock_count', 0)}")
        print(f"   信号数量: {results.get('signal_count', 0)}")

        print(f"⏱️ 性能统计:")
        print(f"   数据获取: {stats['data_fetch_time']:.2f}s")
        print(f"   模型训练: {stats['training_time']:.2f}s")
        print(f"   总耗时: {stats['total_time']:.2f}s")

        if 'training_results' in results:
            train_results = results['training_results']
            print(f"📈 训练结果:")
            print(f"   训练R²: {train_results.get('train_r2', 0):.4f}")
            print(f"   验证R²: {train_results.get('val_r2', 0):.4f}")
            print(f"   特征数量: {train_results.get('feature_count', 0)}")

        if 'signals' in results and results['signals']:
            signals = results['signals']
            print(f"📈 信号分析:")
            print(f"   最高置信度: {max(s['confidence'] for s in signals):.4f}")
            print(
                f"   平均置信度: {np.mean([s['confidence'] for s in signals]):.4f}")
            print(
                f"   最高预测收益: {max(s['predicted_return'] for s in signals):.4f}")

        print("=" * 60)


def main():
    """主函数"""
    print("🚀 启动高性能鲁棒策略训练系统 V4")

    # 创建高性能训练器
    trainer = HighPerformanceTrainerV4(
        max_workers=1,  # 降低到1个工作线程，减少并发压力
        use_processes=False  # 使用线程池（IO密集型）
    )

    # 运行训练流程
    results = trainer.run_training_pipeline()

    if results:
        print("🎉 高性能训练完成！")
    else:
        print("❌ 训练失败")


if __name__ == "__main__":
    main()
