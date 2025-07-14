"""
pytest配置文件

定义测试的全局配置、fixtures和工具函数
"""
import pytest
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session") 
def temp_dir(tmp_path_factory):
    """临时目录"""
    return tmp_path_factory.mktemp("quant_test")

@pytest.fixture
def sample_config():
    """示例配置"""
    return {
        "basic_criteria": {
            "consecutive_days": 3,
            "min_total_return": 0.15,
            "max_drawdown": 0.05,
            "exclude_limit_up_first_day": True
        },
        "price_filters": {
            "min_stock_price": 5.0,
            "max_stock_price": 200.0,
            "min_market_cap": 10.0,
            "max_market_cap": 5000.0
        }
    }

@pytest.fixture
def sample_stock_data():
    """示例股票数据"""
    return [
        {
            "code": "000001",
            "name": "平安银行",
            "price": 12.50,
            "change": 0.25,
            "pct_change": 0.02,
            "volume": 1000000,
            "amount": 12500000
        },
        {
            "code": "600000", 
            "name": "浦发银行",
            "price": 8.80,
            "change": -0.10,
            "pct_change": -0.011,
            "volume": 800000,
            "amount": 7040000
        }
    ]

@pytest.fixture(autouse=True)
def setup_test_environment():
    """自动设置测试环境"""
    # 设置测试环境变量
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["TEST_MODE"] = "true"
    
    yield
    
    # 清理测试环境
    test_vars = ["ENVIRONMENT", "LOG_LEVEL", "TEST_MODE"]
    for var in test_vars:
        if var in os.environ:
            del os.environ[var]
