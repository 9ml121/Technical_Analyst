"""
辅助函数测试
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from datetime import date, datetime, timedelta
from unittest.mock import patch, mock_open

from quant_system.utils.helpers import (
    ensure_dir, safe_divide, calculate_percentage_change, round_to_tick,
    format_currency, format_percentage, format_number, validate_stock_code,
    normalize_stock_code, is_trading_day, get_next_trading_day,
    get_previous_trading_day, get_trading_dates, clean_string,
    generate_hash, format_timestamp, load_yaml_file, save_yaml_file,
    validate_config_value, save_to_json, load_from_json
)


class TestBasicHelpers:
    """基础辅助函数测试"""

    def test_ensure_dir(self):
        """测试确保目录存在"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test" / "subdir"
            result = ensure_dir(test_path)

            assert result == test_path
            assert test_path.exists()
            assert test_path.is_dir()

    def test_safe_divide(self):
        """测试安全除法"""
        # 正常除法
        assert safe_divide(10, 2) == 5.0

        # 除零
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=999) == 999

        # 类型错误
        assert safe_divide("10", 2) == 0.0
        assert safe_divide(10, "2") == 0.0

    def test_calculate_percentage_change(self):
        """测试百分比变化计算"""
        # 正常计算
        assert calculate_percentage_change(100, 110) == 0.1
        assert calculate_percentage_change(100, 90) == -0.1

        # 旧值为零
        assert calculate_percentage_change(0, 100) == 0.0

        # 相同值
        assert calculate_percentage_change(100, 100) == 0.0

    def test_round_to_tick(self):
        """测试价格取整"""
        # 默认tick_size=0.01
        assert round_to_tick(12.345) == 12.34  # Python的round函数使用银行家舍入
        assert round_to_tick(12.344) == 12.34
        assert round_to_tick(12.346) == 12.35

        # 自定义tick_size
        assert round_to_tick(12.345, 0.1) == 12.3
        # 银行家舍入：12.35/0.1=123.5，round(123.5)=124，但实际是123
        assert round_to_tick(12.35, 0.1) == 12.3
        assert round_to_tick(12.36, 0.1) == 12.4


class TestFormatHelpers:
    """格式化辅助函数测试"""

    def test_format_currency(self):
        """测试货币格式化"""
        # 亿级
        assert format_currency(150000000) == "¥1.50亿"

        # 万级
        assert format_currency(50000) == "¥5.00万"

        # 普通
        assert format_currency(1234.56) == "¥1234.56"

        # 自定义货币符号
        assert format_currency(1000, "$") == "$1000.00"

    def test_format_percentage(self):
        """测试百分比格式化"""
        assert format_percentage(0.1234) == "12.34%"
        assert format_percentage(0.1234, 1) == "12.3%"
        assert format_percentage(-0.05) == "-5.00%"

    def test_format_number(self):
        """测试数字格式化"""
        assert format_number(1234.567) == "1,234.57"
        assert format_number(1234.567, 1) == "1,234.6"
        assert format_number(1000000) == "1,000,000.00"

    def test_format_timestamp(self):
        """测试时间戳格式化"""
        # 指定时间
        dt = datetime(2023, 12, 25, 15, 30, 45)
        assert format_timestamp(dt) == "2023-12-25 15:30:45"

        # 默认当前时间
        result = format_timestamp()
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS
        assert result[4] == '-'
        assert result[7] == '-'
        assert result[10] == ' '


class TestStockCodeHelpers:
    """股票代码辅助函数测试"""

    def test_validate_stock_code(self):
        """测试股票代码验证"""
        # A股代码
        assert validate_stock_code("000001", "A") is True
        assert validate_stock_code("600000", "A") is True
        assert validate_stock_code("12345", "A") is False  # 长度不够
        assert validate_stock_code("1234567", "A") is False  # 长度过长
        assert validate_stock_code("00000A", "A") is False  # 包含字母

        # 港股代码
        assert validate_stock_code("00700", "HK") is True
        assert validate_stock_code("1234", "HK") is False  # 长度不够
        assert validate_stock_code("123456", "HK") is False  # 长度过长

        # 未知市场
        assert validate_stock_code("000001", "UNKNOWN") is False

    def test_normalize_stock_code(self):
        """测试股票代码标准化"""
        # A股代码
        assert normalize_stock_code("1", "A") == "000001"
        assert normalize_stock_code("  123  ", "A") == "000123"
        assert normalize_stock_code("600000", "A") == "600000"

        # 港股代码
        assert normalize_stock_code("700", "HK") == "00700"
        assert normalize_stock_code("  123  ", "HK") == "00123"

        # 未知市场
        assert normalize_stock_code("123", "UNKNOWN") == "123"


class TestDateHelpers:
    """日期辅助函数测试"""

    def test_is_trading_day(self):
        """测试交易日判断"""
        # 周一到周五是交易日
        monday = date(2023, 12, 25)  # 2023-12-25是周一
        assert is_trading_day(monday) is True

        friday = date(2023, 12, 29)  # 2023-12-29是周五
        assert is_trading_day(friday) is True

        # 周六周日不是交易日
        saturday = date(2023, 12, 30)  # 2023-12-30是周六
        assert is_trading_day(saturday) is False

        sunday = date(2023, 12, 31)  # 2023-12-31是周日
        assert is_trading_day(sunday) is False

    def test_get_next_trading_day(self):
        """测试获取下一个交易日"""
        # 周四的下一个交易日是周五
        thursday = date(2023, 12, 28)
        friday = date(2023, 12, 29)
        assert get_next_trading_day(thursday) == friday

        # 周五的下一个交易日是下周一
        friday = date(2023, 12, 29)
        next_monday = date(2024, 1, 1)
        assert get_next_trading_day(friday) == next_monday

    def test_get_previous_trading_day(self):
        """测试获取上一个交易日"""
        # 周二的上一个交易日是周一
        tuesday = date(2023, 12, 26)
        monday = date(2023, 12, 25)
        assert get_previous_trading_day(tuesday) == monday

        # 周一的上一个交易日是上周五
        monday = date(2024, 1, 1)
        prev_friday = date(2023, 12, 29)
        assert get_previous_trading_day(monday) == prev_friday

    def test_get_trading_dates(self):
        """测试获取交易日期列表"""
        start_date = date(2023, 12, 25)  # 周一
        end_date = date(2023, 12, 31)    # 周日

        trading_dates = get_trading_dates(start_date, end_date)

        # 应该包含周一到周五，共5天
        assert len(trading_dates) == 5
        assert start_date in trading_dates
        assert date(2023, 12, 29) in trading_dates  # 周五
        assert date(2023, 12, 30) not in trading_dates  # 周六
        assert date(2023, 12, 31) not in trading_dates  # 周日


class TestStringHelpers:
    """字符串辅助函数测试"""

    def test_clean_string(self):
        """测试字符串清理"""
        # 去除首尾空格
        assert clean_string("  hello  ") == "hello"

        # 替换多个空格
        assert clean_string("hello    world") == "hello world"

        # 空字符串
        assert clean_string("") == ""
        assert clean_string(None) == ""

        # 复杂情况
        assert clean_string("  hello   world  ") == "hello world"

    def test_generate_hash(self):
        """测试哈希生成"""
        # 相同输入产生相同哈希
        hash1 = generate_hash("test")
        hash2 = generate_hash("test")
        assert hash1 == hash2

        # 不同输入产生不同哈希
        hash3 = generate_hash("different")
        assert hash1 != hash3

        # 哈希长度固定
        assert len(hash1) == 32  # MD5哈希长度


class TestFileHelpers:
    """文件操作辅助函数测试"""

    def test_save_and_load_json(self):
        """测试JSON文件保存和加载"""
        test_data = {"key": "value", "number": 123}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            # 保存
            result = save_to_json(test_data, temp_path)
            assert result is True
            assert Path(temp_path).exists()

            # 加载
            loaded_data = load_from_json(temp_path)
            assert loaded_data == test_data
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_json_nonexistent(self):
        """测试加载不存在的JSON文件"""
        result = load_from_json("nonexistent.json")
        assert result is None

    def test_save_and_load_yaml(self):
        """测试YAML文件保存和加载"""
        test_data = {"key": "value", "list": [1, 2, 3]}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            # 保存
            save_yaml_file(test_data, temp_path)
            assert Path(temp_path).exists()

            # 加载
            loaded_data = load_yaml_file(temp_path)
            assert loaded_data == test_data
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_yaml_nonexistent(self):
        """测试加载不存在的YAML文件"""
        result = load_yaml_file("nonexistent.yaml")
        assert result == {}

    @patch('builtins.open', mock_open(read_data='invalid: yaml: ['))
    def test_load_yaml_invalid(self):
        """测试加载无效YAML文件"""
        result = load_yaml_file("invalid.yaml")
        assert result == {}


class TestValidationHelpers:
    """验证辅助函数测试"""

    def test_validate_config_value(self):
        """测试配置值验证"""
        # 类型验证
        assert validate_config_value(10, int) is True
        assert validate_config_value("10", int) is False
        assert validate_config_value(10.5, float) is True
        assert validate_config_value("hello", str) is True

        # 范围验证
        assert validate_config_value(5, int, min_value=1, max_value=10) is True
        assert validate_config_value(
            0, int, min_value=1, max_value=10) is False
        assert validate_config_value(
            15, int, min_value=1, max_value=10) is False

        # 只有最小值
        assert validate_config_value(5, int, min_value=1) is True
        assert validate_config_value(0, int, min_value=1) is False

        # 只有最大值
        assert validate_config_value(5, int, max_value=10) is True
        assert validate_config_value(15, int, max_value=10) is False


class TestErrorHandling:
    """错误处理测试"""

    @patch('builtins.open', side_effect=IOError("File error"))
    def test_save_json_error(self, mock_open):
        """测试JSON保存错误处理"""
        result = save_to_json({"test": "data"}, "test.json")
        assert result is False

    @patch('builtins.open', side_effect=IOError("File error"))
    def test_load_json_error(self, mock_open):
        """测试JSON加载错误处理"""
        result = load_from_json("test.json")
        assert result is None

    @patch('builtins.open', side_effect=IOError("File error"))
    def test_save_yaml_error(self, mock_open):
        """测试YAML保存错误处理"""
        # 应该不抛出异常，只记录日志
        save_yaml_file({"test": "data"}, "test.yaml")

    @patch('builtins.open', side_effect=IOError("File error"))
    def test_load_yaml_error(self, mock_open):
        """测试YAML加载错误处理"""
        result = load_yaml_file("test.yaml")
        assert result == {}


if __name__ == '__main__':
    pytest.main([__file__])
