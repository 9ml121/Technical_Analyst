"""
行情数据系统集成测试

测试行情数据获取、处理、存储的完整流程
"""
import pytest
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

# 添加src目录到Python路径
import sys
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from market_data.fetchers.eastmoney_api import EastMoneyAPI
from market_data.processors.data_processor import MarketDataProcessor
from market_data import get_eastmoney_api, get_data_processor

class TestEastMoneyAPIIntegration:
    """东方财富API集成测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.api = EastMoneyAPI()
        self.processor = MarketDataProcessor()
    
    @pytest.mark.integration
    def test_get_realtime_data_and_process(self):
        """测试获取实时数据并处理"""
        # 获取实时数据
        stocks = self.api.get_a_stock_realtime(limit=5)
        
        if not stocks:
            pytest.skip("无法获取实时数据，可能是网络问题")
        
        # 验证数据结构
        assert isinstance(stocks, list)
        assert len(stocks) > 0
        
        for stock in stocks:
            assert 'code' in stock
            assert 'name' in stock
            assert 'price' in stock
            assert isinstance(stock['code'], str)
            assert len(stock['code']) == 6
        
        # 数据处理
        cleaned_stocks = self.processor.clean_stock_data(stocks)
        
        # 验证处理结果
        assert isinstance(cleaned_stocks, list)
        assert len(cleaned_stocks) <= len(stocks)  # 可能过滤掉一些无效数据
        
        for stock in cleaned_stocks:
            assert stock['code'] != ''
            assert stock['name'] != ''
            assert stock['price'] >= 0
            assert stock['volume'] >= 0
    
    @pytest.mark.integration
    def test_get_stock_detail_and_validate(self):
        """测试获取股票详情并验证"""
        # 测试知名股票
        test_codes = ["000001", "600000", "300001"]
        
        for code in test_codes:
            stock_detail = self.api.get_stock_detail(code)
            
            if stock_detail:
                # 验证数据完整性
                assert stock_detail['code'] == code
                assert stock_detail['name'] != ''
                assert stock_detail['price'] > 0
                assert 'update_time' in stock_detail
                
                # 验证价格关系
                if all(key in stock_detail for key in ['open', 'high', 'low', 'price']):
                    assert stock_detail['low'] <= stock_detail['price'] <= stock_detail['high']
                    assert stock_detail['low'] <= stock_detail['open'] <= stock_detail['high']
    
    @pytest.mark.integration
    def test_market_status_check(self):
        """测试市场状态检查"""
        market_status = self.api.get_market_status()
        
        assert isinstance(market_status, dict)
        assert 'market' in market_status
        assert 'status' in market_status
        assert 'update_time' in market_status
        assert 'data_available' in market_status
        
        assert market_status['market'] == 'A股'
        assert isinstance(market_status['data_available'], bool)

class TestDataProcessorIntegration:
    """数据处理器集成测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.processor = MarketDataProcessor()
        
        # 创建测试数据
        self.test_data = [
            {
                'code': '000001',
                'name': '平安银行',
                'price': 12.50,
                'pct_change': 0.02,
                'volume': 1000000,
                'market_cap': 50000000000
            },
            {
                'code': '000002',
                'name': '万科A',
                'price': 18.80,
                'pct_change': -0.015,
                'volume': 800000,
                'market_cap': 80000000000
            },
            {
                'code': '600000',
                'name': '浦发银行',
                'price': 8.90,
                'pct_change': 0.01,
                'volume': 1200000,
                'market_cap': 30000000000
            }
        ]
    
    def test_complete_data_processing_pipeline(self):
        """测试完整的数据处理流程"""
        # 1. 数据清洗
        cleaned_data = self.processor.clean_stock_data(self.test_data)
        assert len(cleaned_data) == 3
        
        # 2. 数据筛选
        filters = {
            'min_price': 10.0,
            'min_pct_change': 0.0
        }
        filtered_data = self.processor.filter_stocks(cleaned_data, filters)
        
        # 验证筛选结果
        for stock in filtered_data:
            assert stock['price'] >= 10.0
            assert stock['pct_change'] >= 0.0
        
        # 3. 数据排序
        sorted_data = self.processor.sort_stocks(filtered_data, sort_by='pct_change', ascending=False)
        
        # 验证排序结果
        if len(sorted_data) > 1:
            for i in range(len(sorted_data) - 1):
                assert sorted_data[i]['pct_change'] >= sorted_data[i + 1]['pct_change']
        
        # 4. 市场统计
        market_stats = self.processor.aggregate_market_data(cleaned_data)
        
        # 验证统计结果
        assert market_stats['total_stocks'] == 3
        assert market_stats['rising_stocks'] == 2  # 2只上涨
        assert market_stats['falling_stocks'] == 1  # 1只下跌
        assert 0 <= market_stats['rising_ratio'] <= 1
    
    def test_technical_indicators_calculation(self):
        """测试技术指标计算"""
        # 创建历史数据
        historical_data = []
        base_price = 100.0
        
        for i in range(30):  # 30天数据
            price = base_price + (i % 5 - 2) * 2  # 模拟价格波动
            historical_data.append({
                'date': (date.today() - timedelta(days=30-i)).strftime('%Y-%m-%d'),
                'open': price - 0.5,
                'close': price,
                'high': price + 1.0,
                'low': price - 1.0,
                'volume': 1000000 + i * 10000
            })
        
        # 计算技术指标
        processed_data = self.processor.calculate_technical_indicators(historical_data)
        
        # 验证技术指标
        assert len(processed_data) == 30
        
        # 检查MA5计算
        for i, item in enumerate(processed_data):
            if i >= 4:  # MA5需要至少5个数据点
                assert 'ma5' in item
                assert item['ma5'] > 0
            
            if i >= 9:  # MA10需要至少10个数据点
                assert 'ma10' in item
                assert item['ma10'] > 0
            
            if i >= 19:  # MA20需要至少20个数据点
                assert 'ma20' in item
                assert item['ma20'] > 0
    
    def test_data_format_conversion(self):
        """测试数据格式转换"""
        # 测试不同格式的数据转换
        tushare_format_data = [
            {
                'ts_code': '000001.SZ',
                'symbol': '000001',
                'name': '平安银行',
                'close': 12.50,
                'pct_chg': 2.0,
                'vol': 1000000
            }
        ]
        
        # 转换为标准格式
        standard_data = self.processor.convert_to_standard_format(
            tushare_format_data, 
            source='tushare'
        )
        
        assert len(standard_data) == 1
        stock = standard_data[0]
        
        assert stock['code'] == '000001'
        assert stock['name'] == '平安银行'
        assert stock['price'] == 12.50
        assert stock['pct_change'] == 2.0
        assert stock['volume'] == 1000000
        assert stock['source'] == 'tushare'

class TestMarketDataSystemIntegration:
    """行情数据系统整体集成测试"""
    
    def test_system_initialization(self):
        """测试系统初始化"""
        # 测试便捷函数
        api = get_eastmoney_api()
        processor = get_data_processor()
        
        assert isinstance(api, EastMoneyAPI)
        assert isinstance(processor, MarketDataProcessor)
    
    @pytest.mark.integration
    def test_end_to_end_data_flow(self):
        """测试端到端数据流"""
        # 1. 初始化组件
        api = get_eastmoney_api()
        processor = get_data_processor()
        
        # 2. 获取实时数据
        stocks = api.get_a_stock_realtime(limit=10)
        
        if not stocks:
            pytest.skip("无法获取实时数据")
        
        # 3. 数据处理流程
        # 清洗数据
        cleaned_stocks = processor.clean_stock_data(stocks)
        
        # 筛选数据（价格大于5元，成交量大于100万）
        filters = {
            'min_price': 5.0,
            'min_volume': 1000000
        }
        filtered_stocks = processor.filter_stocks(cleaned_stocks, filters)
        
        # 排序数据（按涨跌幅降序）
        sorted_stocks = processor.sort_stocks(
            filtered_stocks, 
            sort_by='pct_change', 
            ascending=False
        )
        
        # 生成市场统计
        market_stats = processor.aggregate_market_data(sorted_stocks)
        
        # 4. 验证完整流程
        assert isinstance(cleaned_stocks, list)
        assert isinstance(filtered_stocks, list)
        assert isinstance(sorted_stocks, list)
        assert isinstance(market_stats, dict)
        
        # 验证数据质量
        for stock in sorted_stocks:
            assert stock['price'] >= 5.0
            assert stock['volume'] >= 1000000
            assert stock['code'] != ''
            assert stock['name'] != ''
        
        # 验证统计数据
        assert 'total_stocks' in market_stats
        assert 'rising_stocks' in market_stats
        assert 'falling_stocks' in market_stats
        assert 'avg_pct_change' in market_stats
    
    @pytest.mark.integration
    def test_error_handling_and_recovery(self):
        """测试错误处理和恢复"""
        api = EastMoneyAPI()
        processor = MarketDataProcessor()
        
        # 测试无效股票代码
        invalid_stock = api.get_stock_detail("INVALID")
        assert invalid_stock is None
        
        # 测试空数据处理
        empty_result = processor.clean_stock_data([])
        assert empty_result == []
        
        # 测试无效数据处理
        invalid_data = [
            {'code': '', 'name': '', 'price': -1},  # 无效数据
            {'code': '000001', 'name': '平安银行', 'price': 12.50}  # 有效数据
        ]
        
        cleaned_result = processor.clean_stock_data(invalid_data)
        assert len(cleaned_result) == 1  # 只保留有效数据
        assert cleaned_result[0]['code'] == '000001'
    
    def test_performance_benchmarks(self):
        """测试性能基准"""
        import time
        
        api = EastMoneyAPI()
        processor = MarketDataProcessor()
        
        # 测试数据获取性能
        start_time = time.time()
        stocks = api.get_a_stock_realtime(limit=20)
        fetch_time = time.time() - start_time
        
        if stocks:
            # 数据获取应该在合理时间内完成
            assert fetch_time < 10.0  # 10秒内
            
            # 测试数据处理性能
            start_time = time.time()
            cleaned_stocks = processor.clean_stock_data(stocks)
            filtered_stocks = processor.filter_stocks(cleaned_stocks, {'min_price': 1.0})
            sorted_stocks = processor.sort_stocks(filtered_stocks, 'pct_change')
            market_stats = processor.aggregate_market_data(sorted_stocks)
            process_time = time.time() - start_time
            
            # 数据处理应该很快
            assert process_time < 1.0  # 1秒内

# 测试夹具
@pytest.fixture
def mock_market_data():
    """模拟市场数据夹具"""
    return [
        {
            'code': '000001',
            'name': '平安银行',
            'price': 12.50,
            'open': 12.30,
            'high': 12.80,
            'low': 12.20,
            'pct_change': 0.024,
            'volume': 15000000,
            'amount': 187500000,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'code': '600000',
            'name': '浦发银行',
            'price': 8.90,
            'open': 8.85,
            'high': 9.00,
            'low': 8.80,
            'pct_change': -0.011,
            'volume': 12000000,
            'amount': 106800000,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

@pytest.fixture
def data_processor():
    """数据处理器夹具"""
    return MarketDataProcessor()

def test_integration_with_fixtures(mock_market_data, data_processor):
    """使用夹具的集成测试"""
    # 测试数据处理
    cleaned_data = data_processor.clean_stock_data(mock_market_data)
    assert len(cleaned_data) == 2
    
    # 测试筛选
    rising_stocks = data_processor.filter_stocks(
        cleaned_data, 
        {'min_pct_change': 0.0}
    )
    assert len(rising_stocks) == 1
    assert rising_stocks[0]['code'] == '000001'
    
    # 测试统计
    stats = data_processor.aggregate_market_data(cleaned_data)
    assert stats['total_stocks'] == 2
    assert stats['rising_stocks'] == 1
    assert stats['falling_stocks'] == 1
