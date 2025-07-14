"""
工具模块单元测试

测试验证器、辅助函数、日志等工具功能
"""
import pytest
import tempfile
import logging
from datetime import date, datetime
from pathlib import Path

# 添加src目录到Python路径
import sys
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from quant_system.utils.validators import (
    StockCodeValidator, DataValidator, StrategyValidator,
    validate_stock_data, sanitize_input
)
from quant_system.utils.helpers import (
    ensure_dir, safe_divide, calculate_percentage_change,
    format_currency, format_percentage, get_trading_dates,
    is_trading_day, flatten_dict, unflatten_dict,
    timing_context
)
from quant_system.utils.logger import get_logger, QuantLogger

class TestStockCodeValidator:
    """股票代码验证器测试"""
    
    def test_is_valid_a_share(self):
        """测试A股代码验证"""
        # 有效的A股代码
        assert StockCodeValidator.is_valid_a_share("000001") is True  # 深市主板
        assert StockCodeValidator.is_valid_a_share("300001") is True  # 创业板
        assert StockCodeValidator.is_valid_a_share("600000") is True  # 沪市主板
        assert StockCodeValidator.is_valid_a_share("688001") is True  # 科创板
        
        # 无效的A股代码
        assert StockCodeValidator.is_valid_a_share("123456") is False  # 不符合规则
        assert StockCodeValidator.is_valid_a_share("00001") is False   # 长度不对
        assert StockCodeValidator.is_valid_a_share("0000001") is False # 长度不对
        assert StockCodeValidator.is_valid_a_share("") is False        # 空字符串
        assert StockCodeValidator.is_valid_a_share(None) is False      # None值
    
    def test_is_valid_hk_share(self):
        """测试港股代码验证"""
        # 有效的港股代码
        assert StockCodeValidator.is_valid_hk_share("00700") is True  # 腾讯
        assert StockCodeValidator.is_valid_hk_share("09988") is True  # 阿里巴巴
        assert StockCodeValidator.is_valid_hk_share("01299") is True  # 友邦保险
        
        # 无效的港股代码
        assert StockCodeValidator.is_valid_hk_share("700") is False    # 长度不对
        assert StockCodeValidator.is_valid_hk_share("000700") is False # 长度不对
        assert StockCodeValidator.is_valid_hk_share("") is False       # 空字符串
        assert StockCodeValidator.is_valid_hk_share("ABCDE") is False  # 非数字
    
    def test_validate_code(self):
        """测试通用代码验证"""
        # A股验证
        assert StockCodeValidator.validate_code("000001", "A") is True
        assert StockCodeValidator.validate_code("123456", "A") is False
        
        # 港股验证
        assert StockCodeValidator.validate_code("00700", "HK") is True
        assert StockCodeValidator.validate_code("700", "HK") is False
        
        # 不支持的市场
        assert StockCodeValidator.validate_code("000001", "US") is False

class TestDataValidator:
    """数据验证器测试"""
    
    def test_validate_price(self):
        """测试价格验证"""
        # 有效价格
        assert DataValidator.validate_price(12.50) is True
        assert DataValidator.validate_price(0.01) is True
        assert DataValidator.validate_price(1000.0) is True
        assert DataValidator.validate_price("12.50") is True  # 字符串数字
        
        # 无效价格
        assert DataValidator.validate_price(-1.0) is False
        assert DataValidator.validate_price(0) is False
        assert DataValidator.validate_price(10001.0) is False
        assert DataValidator.validate_price("invalid") is False
        assert DataValidator.validate_price(None) is False
    
    def test_validate_volume(self):
        """测试成交量验证"""
        # 有效成交量
        assert DataValidator.validate_volume(1000000) is True
        assert DataValidator.validate_volume(0) is True
        assert DataValidator.validate_volume("1000000") is True
        
        # 无效成交量
        assert DataValidator.validate_volume(-1000) is False
        assert DataValidator.validate_volume("invalid") is False
        assert DataValidator.validate_volume(None) is False
    
    def test_validate_percentage(self):
        """测试百分比验证"""
        # 有效百分比
        assert DataValidator.validate_percentage(0.5) is True
        assert DataValidator.validate_percentage(-0.5) is True
        assert DataValidator.validate_percentage(0.0) is True
        
        # 无效百分比
        assert DataValidator.validate_percentage(1.5) is False
        assert DataValidator.validate_percentage(-1.5) is False
        assert DataValidator.validate_percentage("invalid") is False
    
    def test_validate_date_range(self):
        """测试日期范围验证"""
        start_date = date(2023, 1, 1)
        end_date = date(2024, 1, 1)
        
        # 有效日期范围
        assert DataValidator.validate_date_range(start_date, end_date) is True
        assert DataValidator.validate_date_range(start_date, start_date) is True
        
        # 无效日期范围
        assert DataValidator.validate_date_range(end_date, start_date) is False
    
    def test_validate_config_dict(self):
        """测试配置字典验证"""
        config = {
            "key1": "value1",
            "key2": "value2"
        }
        
        required_keys = ["key1", "key2"]
        errors = DataValidator.validate_config_dict(config, required_keys)
        assert len(errors) == 0
        
        required_keys = ["key1", "key2", "key3"]
        errors = DataValidator.validate_config_dict(config, required_keys)
        assert len(errors) == 1
        assert "key3" in errors[0]

class TestStrategyValidator:
    """策略验证器测试"""
    
    def test_validate_selection_criteria(self):
        """测试选股条件验证"""
        # 有效的选股条件
        valid_criteria = {
            "basic_criteria": {
                "consecutive_days": 3,
                "min_total_return": 0.15,
                "max_drawdown": 0.05
            },
            "price_filters": {
                "min_stock_price": 5.0,
                "max_stock_price": 200.0
            }
        }
        
        errors = StrategyValidator.validate_selection_criteria(valid_criteria)
        assert len(errors) == 0
        
        # 无效的选股条件
        invalid_criteria = {
            "basic_criteria": {
                "consecutive_days": -1,  # 无效值
                "min_total_return": -0.1  # 无效值
            },
            "price_filters": {
                "min_stock_price": 200.0,
                "max_stock_price": 5.0  # 最小价格大于最大价格
            }
        }
        
        errors = StrategyValidator.validate_selection_criteria(invalid_criteria)
        assert len(errors) > 0
    
    def test_validate_backtest_config(self):
        """测试回测配置验证"""
        # 有效的回测配置
        valid_config = {
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "initial_capital": 1000000.0
        }
        
        errors = StrategyValidator.validate_backtest_config(valid_config)
        assert len(errors) == 0
        
        # 无效的回测配置
        invalid_config = {
            "start_date": "2024-01-01",
            "end_date": "2023-01-01",  # 结束日期早于开始日期
            "initial_capital": -1000000.0  # 负数资金
        }
        
        errors = StrategyValidator.validate_backtest_config(invalid_config)
        assert len(errors) > 0

class TestValidateStockData:
    """股票数据验证函数测试"""
    
    def test_validate_valid_stock_data(self):
        """测试有效股票数据验证"""
        valid_data = {
            "code": "000001",
            "open_price": 12.50,
            "close_price": 12.80,
            "high_price": 13.00,
            "low_price": 12.30,
            "volume": 1000000
        }
        
        errors = validate_stock_data(valid_data)
        assert len(errors) == 0
    
    def test_validate_invalid_stock_data(self):
        """测试无效股票数据验证"""
        invalid_data = {
            "code": "",  # 空代码
            "open_price": -1.0,  # 负价格
            "close_price": 12.80,
            "high_price": 10.00,  # 最高价小于收盘价
            "low_price": 15.00,   # 最低价大于收盘价
            "volume": -1000       # 负成交量
        }
        
        errors = validate_stock_data(invalid_data)
        assert len(errors) > 0

class TestSanitizeInput:
    """输入清理函数测试"""
    
    def test_sanitize_string(self):
        """测试字符串清理"""
        assert sanitize_input("  test  ", str) == "test"
        assert sanitize_input(123, str) == "123"
        assert sanitize_input(None, str, "default") == "default"
    
    def test_sanitize_int(self):
        """测试整数清理"""
        assert sanitize_input("123", int) == 123
        assert sanitize_input("123.5", int) == 123
        assert sanitize_input("invalid", int, 0) == 0
        assert sanitize_input(None, int, -1) == -1
    
    def test_sanitize_float(self):
        """测试浮点数清理"""
        assert sanitize_input("12.5", float) == 12.5
        assert sanitize_input("invalid", float, 0.0) == 0.0
        assert sanitize_input(None, float, -1.0) == -1.0
    
    def test_sanitize_bool(self):
        """测试布尔值清理"""
        assert sanitize_input("true", bool) is True
        assert sanitize_input("1", bool) is True
        assert sanitize_input("yes", bool) is True
        assert sanitize_input("false", bool) is False
        assert sanitize_input("0", bool) is False
        assert sanitize_input(1, bool) is True
        assert sanitize_input(0, bool) is False

class TestHelpers:
    """辅助函数测试"""
    
    def test_ensure_dir(self):
        """测试目录创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test" / "nested"
            result_dir = ensure_dir(test_dir)
            
            assert result_dir.exists()
            assert result_dir.is_dir()
            assert result_dir == test_dir
    
    def test_safe_divide(self):
        """测试安全除法"""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=999) == 999
        assert safe_divide("invalid", 2, default=-1) == -1
    
    def test_calculate_percentage_change(self):
        """测试百分比变化计算"""
        assert calculate_percentage_change(100, 120) == 0.2
        assert calculate_percentage_change(100, 80) == -0.2
        assert calculate_percentage_change(0, 100) == 0.0
        assert calculate_percentage_change(100, 100) == 0.0
    
    def test_format_currency(self):
        """测试货币格式化"""
        assert format_currency(1234567.89) == "¥123.46万"
        assert format_currency(123456789.0) == "¥1.23亿"
        assert format_currency(1234.56) == "¥1234.56"
        assert format_currency(1234567.89, "$") == "$123.46万"
    
    def test_format_percentage(self):
        """测试百分比格式化"""
        assert format_percentage(0.1234) == "12.34%"
        assert format_percentage(0.1234, 1) == "12.3%"
        assert format_percentage(-0.05) == "-5.00%"
    
    def test_get_trading_dates(self):
        """测试交易日期获取"""
        start_date = date(2024, 1, 1)  # 周一
        end_date = date(2024, 1, 7)    # 周日
        
        # 包含周末
        all_dates = get_trading_dates(start_date, end_date, exclude_weekends=False)
        assert len(all_dates) == 7
        
        # 排除周末
        trading_dates = get_trading_dates(start_date, end_date, exclude_weekends=True)
        assert len(trading_dates) == 5  # 周一到周五
    
    def test_is_trading_day(self):
        """测试交易日判断"""
        monday = date(2024, 1, 1)    # 周一
        saturday = date(2024, 1, 6)  # 周六
        sunday = date(2024, 1, 7)    # 周日
        
        assert is_trading_day(monday) is True
        assert is_trading_day(saturday) is False
        assert is_trading_day(sunday) is False
    
    def test_flatten_dict(self):
        """测试字典扁平化"""
        nested_dict = {
            "a": {
                "b": {
                    "c": 1
                },
                "d": 2
            },
            "e": 3
        }
        
        flattened = flatten_dict(nested_dict)
        expected = {
            "a.b.c": 1,
            "a.d": 2,
            "e": 3
        }
        
        assert flattened == expected
    
    def test_unflatten_dict(self):
        """测试字典反扁平化"""
        flattened_dict = {
            "a.b.c": 1,
            "a.d": 2,
            "e": 3
        }
        
        unflattened = unflatten_dict(flattened_dict)
        expected = {
            "a": {
                "b": {
                    "c": 1
                },
                "d": 2
            },
            "e": 3
        }
        
        assert unflattened == expected
    
    def test_timing_context(self):
        """测试计时上下文管理器"""
        import time
        
        with timing_context("test_operation"):
            time.sleep(0.1)  # 模拟操作
        
        # 测试异常情况
        try:
            with timing_context("test_error"):
                raise ValueError("Test error")
        except ValueError:
            pass  # 预期的异常

class TestQuantLogger:
    """量化日志器测试"""
    
    def test_logger_creation(self):
        """测试日志器创建"""
        logger = QuantLogger("test_logger")
        assert logger.name == "test_logger"
        assert logger._configured is False
    
    def test_logger_configuration(self):
        """测试日志器配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = QuantLogger("test_logger")
            
            configured_logger = logger.configure(
                level="DEBUG",
                log_dir=temp_dir,
                log_file="test.log",
                console_output=False
            )
            
            assert logger._configured is True
            assert configured_logger.level == logging.DEBUG
    
    def test_get_logger_function(self):
        """测试获取日志器函数"""
        logger = get_logger("test_function_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "quant_system"  # 默认名称

# 测试夹具
@pytest.fixture
def sample_stock_data_dict():
    """示例股票数据字典夹具"""
    return {
        "code": "000001",
        "name": "平安银行",
        "open_price": 12.50,
        "close_price": 12.80,
        "high_price": 13.00,
        "low_price": 12.30,
        "volume": 1000000,
        "amount": 12800000
    }

@pytest.fixture
def sample_selection_criteria():
    """示例选股条件夹具"""
    return {
        "basic_criteria": {
            "consecutive_days": 3,
            "min_total_return": 0.15,
            "max_drawdown": 0.05
        },
        "price_filters": {
            "min_stock_price": 5.0,
            "max_stock_price": 200.0
        }
    }

def test_utils_integration(sample_stock_data_dict, sample_selection_criteria):
    """工具模块集成测试"""
    # 验证股票数据
    errors = validate_stock_data(sample_stock_data_dict)
    assert len(errors) == 0
    
    # 验证选股条件
    errors = StrategyValidator.validate_selection_criteria(sample_selection_criteria)
    assert len(errors) == 0
    
    # 测试数据清理
    cleaned_price = sanitize_input(sample_stock_data_dict["close_price"], float)
    assert cleaned_price == 12.80
    
    # 测试格式化
    formatted_price = format_currency(sample_stock_data_dict["amount"])
    assert "万" in formatted_price or "亿" in formatted_price
