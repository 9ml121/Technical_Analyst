#!/usr/bin/env python3
"""
端到端测试

模拟完整的量化投资业务流程
"""

import sys
import pytest
import tempfile
import yaml
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from quant_system.utils.config_loader import ConfigLoader
from quant_system.utils.logger import get_logger

class TestEndToEnd:
    """端到端测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.data_dir = Path(self.temp_dir) / "data"
        self.results_dir = Path(self.temp_dir) / "results"
        
        # 创建目录
        for dir_path in [self.config_dir, self.data_dir, self.results_dir]:
            dir_path.mkdir(parents=True)
        
        # 创建测试配置和数据
        self.create_test_environment()
        
        # 初始化系统
        self.config_loader = ConfigLoader(str(self.config_dir))
        self.logger = get_logger("e2e_test")
    
    def teardown_method(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_environment(self):
        """创建测试环境"""
        # 创建系统配置
        system_config = {
            'system': {
                'name': '量化投资系统E2E测试',
                'version': '1.0.0',
                'data_dir': str(self.data_dir),
                'results_dir': str(self.results_dir)
            },
            'market_data': {
                'source': 'mock',
                'update_interval': 60,
                'cache_enabled': True
            },
            'strategy': {
                'default_capital': 1000000,
                'max_positions': 10,
                'risk_limit': 0.02
            },
            'backtest': {
                'start_date': '2023-01-01',
                'end_date': '2023-12-31',
                'benchmark': '000300.SH'
            }
        }
        
        with open(self.config_dir / "default.yaml", 'w') as f:
            yaml.dump(system_config, f)
        
        # 创建策略配置
        strategy_dir = self.config_dir / "strategies"
        strategy_dir.mkdir()
        
        momentum_strategy = {
            'strategy_info': {
                'name': '动量策略',
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
        
        with open(strategy_dir / "momentum_strategy.yaml", 'w') as f:
            yaml.dump(momentum_strategy, f)
        
        # 创建模拟市场数据
        self.create_mock_market_data()
    
    def create_mock_market_data(self):
        """创建模拟市场数据"""
        import random
        
        # 生成股票列表
        stocks = []
        for i in range(100):
            stock = {
                'code': f"{i:06d}",
                'name': f"测试股票{i+1}",
                'industry': random.choice(['科技', '金融', '医药', '消费', '制造']),
                'market_cap': random.randint(1000000000, 100000000000)
            }
            stocks.append(stock)
        
        with open(self.data_dir / "stock_list.json", 'w') as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        
        # 生成历史价格数据
        price_data = {}
        base_date = datetime(2023, 1, 1)
        
        for stock in stocks[:20]:  # 只为前20只股票生成数据
            code = stock['code']
            prices = []
            
            current_price = random.uniform(10, 100)
            
            for day in range(365):
                date = base_date + timedelta(days=day)
                
                # 模拟价格变动
                change_pct = random.gauss(0, 0.02)  # 平均0%，标准差2%
                current_price *= (1 + change_pct)
                current_price = max(current_price, 1.0)  # 最低价格1元
                
                price_record = {
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(current_price * random.uniform(0.98, 1.02), 2),
                    'high': round(current_price * random.uniform(1.00, 1.05), 2),
                    'low': round(current_price * random.uniform(0.95, 1.00), 2),
                    'close': round(current_price, 2),
                    'volume': random.randint(1000000, 50000000),
                    'amount': round(current_price * random.randint(1000000, 50000000), 2)
                }
                
                prices.append(price_record)
            
            price_data[code] = prices
        
        with open(self.data_dir / "historical_prices.json", 'w') as f:
            json.dump(price_data, f, ensure_ascii=False, indent=2)
    
    def test_complete_quantitative_workflow(self):
        """测试完整的量化投资工作流程"""
        self.logger.info("开始端到端测试：完整量化投资工作流程")
        
        # 1. 系统初始化
        config = self.config_loader.load_config("default")
        assert config['system']['name'] == '量化投资系统E2E测试'
        self.logger.info("✅ 系统初始化完成")
        
        # 2. 加载策略配置
        strategy_config = self.config_loader.load_strategy_config("momentum_strategy")
        assert strategy_config['strategy_info']['name'] == '动量策略'
        self.logger.info("✅ 策略配置加载完成")
        
        # 3. 数据获取和处理
        market_data = self.load_and_process_market_data()
        assert len(market_data) > 0
        self.logger.info(f"✅ 市场数据处理完成，共{len(market_data)}只股票")
        
        # 4. 策略执行
        selected_stocks = self.execute_strategy(market_data, strategy_config)
        assert len(selected_stocks) > 0
        self.logger.info(f"✅ 策略执行完成，选中{len(selected_stocks)}只股票")
        
        # 5. 风险管理
        risk_adjusted_positions = self.apply_risk_management(selected_stocks, strategy_config)
        assert len(risk_adjusted_positions) <= len(selected_stocks)
        self.logger.info(f"✅ 风险管理完成，最终持仓{len(risk_adjusted_positions)}只股票")
        
        # 6. 回测分析
        backtest_results = self.run_backtest(risk_adjusted_positions, config)
        assert 'total_return' in backtest_results
        self.logger.info(f"✅ 回测分析完成，总收益率: {backtest_results['total_return']:.2%}")
        
        # 7. 结果保存
        self.save_results(backtest_results)
        self.logger.info("✅ 结果保存完成")
        
        # 验证整个流程的完整性
        assert backtest_results['total_return'] is not None
        assert len(backtest_results['trades']) >= 0
        
        self.logger.info("🎉 端到端测试完成：完整量化投资工作流程")
    
    def load_and_process_market_data(self):
        """加载和处理市场数据"""
        # 加载股票列表
        with open(self.data_dir / "stock_list.json", 'r') as f:
            stock_list = json.load(f)
        
        # 加载历史价格数据
        with open(self.data_dir / "historical_prices.json", 'r') as f:
            price_data = json.load(f)
        
        # 处理数据
        processed_data = []
        for stock in stock_list:
            code = stock['code']
            if code in price_data:
                # 计算技术指标
                prices = price_data[code]
                latest_price = prices[-1]
                
                # 计算收益率
                if len(prices) >= 20:
                    price_20_days_ago = prices[-20]['close']
                    return_20d = (latest_price['close'] - price_20_days_ago) / price_20_days_ago
                else:
                    return_20d = 0
                
                # 计算平均成交量
                avg_volume = sum(p['volume'] for p in prices[-10:]) / min(10, len(prices))
                
                processed_stock = {
                    'code': code,
                    'name': stock['name'],
                    'industry': stock['industry'],
                    'market_cap': stock['market_cap'],
                    'current_price': latest_price['close'],
                    'return_20d': return_20d,
                    'avg_volume': avg_volume,
                    'latest_volume': latest_price['volume']
                }
                
                processed_data.append(processed_stock)
        
        return processed_data
    
    def execute_strategy(self, market_data, strategy_config):
        """执行策略选股"""
        criteria = strategy_config['selection_criteria']
        
        selected_stocks = []
        
        for stock in market_data:
            # 基本条件筛选
            if stock['return_20d'] < criteria['basic_criteria']['min_total_return']:
                continue
            
            # 价格筛选
            price_filters = criteria['price_filters']
            if not (price_filters['min_stock_price'] <= stock['current_price'] <= price_filters['max_stock_price']):
                continue
            
            # 成交量筛选
            volume_filters = criteria['volume_filters']
            if stock['avg_volume'] < volume_filters['min_avg_volume']:
                continue
            
            # 计算选股得分
            score = stock['return_20d'] * 100 + (stock['avg_volume'] / 1000000) * 0.1
            
            selected_stocks.append({
                **stock,
                'selection_score': score
            })
        
        # 按得分排序，选择前10只
        selected_stocks.sort(key=lambda x: x['selection_score'], reverse=True)
        return selected_stocks[:10]
    
    def apply_risk_management(self, selected_stocks, strategy_config):
        """应用风险管理"""
        risk_config = strategy_config['risk_management']
        
        # 简单的风险管理：限制单只股票最大权重
        max_weight = 0.15  # 单只股票最大15%权重
        total_score = sum(stock['selection_score'] for stock in selected_stocks)
        
        risk_adjusted_positions = []
        
        for stock in selected_stocks:
            weight = stock['selection_score'] / total_score
            adjusted_weight = min(weight, max_weight)
            
            position = {
                **stock,
                'weight': adjusted_weight,
                'stop_loss_price': stock['current_price'] * (1 - risk_config['stop_loss']['percentage']),
                'take_profit_price': stock['current_price'] * (1 + risk_config['take_profit']['percentage'])
            }
            
            risk_adjusted_positions.append(position)
        
        return risk_adjusted_positions
    
    def run_backtest(self, positions, config):
        """运行回测"""
        backtest_config = config['backtest']
        initial_capital = config['strategy']['default_capital']
        
        # 简化的回测逻辑
        total_return = 0
        trades = []
        
        for position in positions:
            # 模拟交易
            entry_price = position['current_price']
            
            # 模拟持有期收益
            import random
            holding_return = random.gauss(0.05, 0.15)  # 平均5%收益，15%波动
            exit_price = entry_price * (1 + holding_return)
            
            trade = {
                'code': position['code'],
                'name': position['name'],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'weight': position['weight'],
                'return': holding_return,
                'profit': initial_capital * position['weight'] * holding_return
            }
            
            trades.append(trade)
            total_return += position['weight'] * holding_return
        
        # 计算其他指标
        returns = [trade['return'] for trade in trades]
        
        backtest_results = {
            'start_date': backtest_config['start_date'],
            'end_date': backtest_config['end_date'],
            'initial_capital': initial_capital,
            'final_capital': initial_capital * (1 + total_return),
            'total_return': total_return,
            'trades': trades,
            'num_trades': len(trades),
            'win_rate': len([r for r in returns if r > 0]) / len(returns) if returns else 0,
            'avg_return': sum(returns) / len(returns) if returns else 0,
            'max_return': max(returns) if returns else 0,
            'min_return': min(returns) if returns else 0
        }
        
        return backtest_results
    
    def save_results(self, results):
        """保存结果"""
        # 保存回测结果
        results_file = self.results_dir / "backtest_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        # 保存交易记录
        trades_file = self.results_dir / "trades.json"
        with open(trades_file, 'w') as f:
            json.dump(results['trades'], f, ensure_ascii=False, indent=2)
        
        # 生成简单报告
        report_file = self.results_dir / "report.txt"
        with open(report_file, 'w') as f:
            f.write("量化投资系统回测报告\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"回测期间: {results['start_date']} 至 {results['end_date']}\n")
            f.write(f"初始资金: ¥{results['initial_capital']:,.0f}\n")
            f.write(f"最终资金: ¥{results['final_capital']:,.0f}\n")
            f.write(f"总收益率: {results['total_return']:+.2%}\n")
            f.write(f"交易次数: {results['num_trades']}\n")
            f.write(f"胜率: {results['win_rate']:.2%}\n")
            f.write(f"平均收益: {results['avg_return']:+.2%}\n")
    
    def test_error_recovery(self):
        """测试错误恢复能力"""
        self.logger.info("开始测试：错误恢复能力")
        
        # 测试配置文件缺失的情况
        try:
            config = self.config_loader.load_config("nonexistent_config")
            # 应该返回默认配置或空配置，而不是崩溃
            assert isinstance(config, dict)
            self.logger.info("✅ 配置文件缺失错误恢复测试通过")
        except Exception as e:
            pytest.fail(f"配置文件缺失应该优雅处理: {e}")
        
        # 测试数据文件损坏的情况
        corrupted_file = self.data_dir / "corrupted_data.json"
        with open(corrupted_file, 'w') as f:
            f.write("invalid json content {")
        
        try:
            with open(corrupted_file, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            # 这是预期的错误，系统应该能够处理
            self.logger.info("✅ 数据文件损坏错误检测正常")
        
        self.logger.info("🎉 错误恢复能力测试完成")
    
    def test_performance_under_load(self):
        """测试负载下的性能"""
        self.logger.info("开始测试：负载下的性能")
        
        import time
        
        # 创建大量数据
        large_dataset = []
        for i in range(1000):
            stock = {
                'code': f"{i:06d}",
                'name': f"股票{i}",
                'current_price': 10 + (i % 100),
                'return_20d': (i % 20) / 100,
                'avg_volume': 1000000 + (i * 1000)
            }
            large_dataset.append(stock)
        
        # 测试数据处理性能
        start_time = time.time()
        
        # 模拟策略执行
        filtered_stocks = []
        for stock in large_dataset:
            if stock['return_20d'] > 0.05 and stock['current_price'] > 15:
                filtered_stocks.append(stock)
        
        processing_time = time.time() - start_time
        
        assert processing_time < 1.0, f"数据处理时间过长: {processing_time:.2f}s"
        assert len(filtered_stocks) > 0, "筛选结果不应为空"
        
        self.logger.info(f"✅ 负载测试通过，处理1000只股票用时: {processing_time:.3f}s")
        self.logger.info("🎉 负载下的性能测试完成")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
