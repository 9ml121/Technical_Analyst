"""
量化投资系统主程序入口

提供命令行接口和系统集成功能
"""
import sys
import argparse
from pathlib import Path
from datetime import date, timedelta

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from quant_system.utils.logger import get_logger, setup_logging
from quant_system.utils.config_loader import load_config
from quant_system.utils.helpers import ensure_dir

def test_imports():
    """测试模块导入"""
    logger = get_logger()
    logger.info("开始测试模块导入...")
    
    try:
        # 测试核心模块导入
        from quant_system.core import data_provider
        logger.info("✅ data_provider 模块导入成功")
        
        from quant_system.core import strategy_engine
        logger.info("✅ strategy_engine 模块导入成功")
        
        from quant_system.core import backtest_engine
        logger.info("✅ backtest_engine 模块导入成功")
        
        from quant_system.core import trading_strategy
        logger.info("✅ trading_strategy 模块导入成功")
        
        from quant_system.core import feature_extraction
        logger.info("✅ feature_extraction 模块导入成功")
        
        from quant_system.core import analysis_module
        logger.info("✅ analysis_module 模块导入成功")
        
        # 测试数据模型导入
        from quant_system.models import stock_data
        logger.info("✅ stock_data 模型导入成功")
        
        from quant_system.models import strategy_models
        logger.info("✅ strategy_models 模型导入成功")
        
        from quant_system.models import backtest_models
        logger.info("✅ backtest_models 模型导入成功")
        
        # 测试工具模块导入
        from quant_system.utils import config_loader
        logger.info("✅ config_loader 工具导入成功")
        
        from quant_system.utils import validators
        logger.info("✅ validators 工具导入成功")
        
        from quant_system.utils import helpers
        logger.info("✅ helpers 工具导入成功")
        
        logger.info("🎉 所有模块导入测试通过！")
        return True
        
    except ImportError as e:
        logger.error(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 测试过程中出现错误: {e}")
        return False

def test_data_models():
    """测试数据模型"""
    logger = get_logger()
    logger.info("开始测试数据模型...")
    
    try:
        from quant_system.models.stock_data import StockData, StockDataValidator
        from quant_system.models.strategy_models import SelectionCriteria, TradingStrategy, StrategyType
        from quant_system.models.backtest_models import BacktestConfig, TradeRecord, TradeAction
        
        # 测试StockData模型
        stock_data = StockData(
            code="000001",
            name="平安银行",
            date=date.today(),
            open_price=12.50,
            close_price=12.80,
            high_price=13.00,
            low_price=12.30,
            volume=1000000,
            amount=12800000,
            pre_close=12.50
        )
        logger.info(f"✅ StockData模型创建成功: {stock_data.code} {stock_data.name}")
        
        # 测试股票代码验证
        is_valid = StockDataValidator.validate_stock_code("000001", "A")
        logger.info(f"✅ 股票代码验证: 000001 -> {is_valid}")
        
        # 测试选股条件模型
        criteria = SelectionCriteria(
            consecutive_days=3,
            min_total_return=0.15,
            max_drawdown=0.05
        )
        logger.info(f"✅ SelectionCriteria模型创建成功")
        
        # 测试回测配置模型
        backtest_config = BacktestConfig(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            initial_capital=1000000
        )
        logger.info(f"✅ BacktestConfig模型创建成功")
        
        logger.info("🎉 数据模型测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据模型测试失败: {e}")
        return False

def test_config_system():
    """测试配置系统"""
    logger = get_logger()
    logger.info("开始测试配置系统...")
    
    try:
        from quant_system.utils.config_loader import ConfigLoader
        
        # 创建配置加载器
        config_loader = ConfigLoader()
        
        # 测试加载默认配置（即使文件不存在也应该返回空字典）
        config = config_loader.load_config("test_config", use_cache=False)
        logger.info(f"✅ 配置加载测试通过，返回类型: {type(config)}")
        
        # 测试配置验证
        test_config = {
            "basic_criteria": {
                "consecutive_days": 3,
                "min_total_return": 0.15
            }
        }
        
        schema = {
            "basic_criteria": dict
        }
        
        is_valid = config_loader.validate_config(test_config, schema)
        logger.info(f"✅ 配置验证测试: {is_valid}")
        
        logger.info("🎉 配置系统测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 配置系统测试失败: {e}")
        return False

def test_validation_system():
    """测试验证系统"""
    logger = get_logger()
    logger.info("开始测试验证系统...")
    
    try:
        from quant_system.utils.validators import StockCodeValidator, DataValidator, validate_stock_data
        
        # 测试股票代码验证
        test_codes = ["000001", "600000", "300001", "68001", "invalid"]
        for code in test_codes:
            is_valid = StockCodeValidator.is_valid_a_share(code)
            logger.info(f"股票代码验证 {code}: {is_valid}")
        
        # 测试价格验证
        test_prices = [12.50, -1.0, 0, 10000, "invalid"]
        for price in test_prices:
            is_valid = DataValidator.validate_price(price)
            logger.info(f"价格验证 {price}: {is_valid}")
        
        # 测试股票数据验证
        test_stock_data = {
            "code": "000001",
            "open_price": 12.50,
            "close_price": 12.80,
            "high_price": 13.00,
            "low_price": 12.30,
            "volume": 1000000
        }
        
        errors = validate_stock_data(test_stock_data)
        logger.info(f"✅ 股票数据验证完成，错误数量: {len(errors)}")
        
        logger.info("🎉 验证系统测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 验证系统测试失败: {e}")
        return False

def test_helper_functions():
    """测试辅助函数"""
    logger = get_logger()
    logger.info("开始测试辅助函数...")
    
    try:
        from quant_system.utils.helpers import (
            safe_divide, calculate_percentage_change, format_currency,
            format_percentage, get_quarter, flatten_dict
        )
        
        # 测试安全除法
        result = safe_divide(10, 2)
        logger.info(f"安全除法 10/2 = {result}")
        
        result = safe_divide(10, 0, default=999)
        logger.info(f"安全除法 10/0 = {result} (默认值)")
        
        # 测试百分比计算
        pct_change = calculate_percentage_change(100, 120)
        logger.info(f"百分比变化 100->120 = {pct_change:.2%}")
        
        # 测试货币格式化
        formatted = format_currency(1234567.89)
        logger.info(f"货币格式化 1234567.89 = {formatted}")
        
        # 测试百分比格式化
        formatted = format_percentage(0.1234)
        logger.info(f"百分比格式化 0.1234 = {formatted}")
        
        # 测试季度获取
        quarter = get_quarter(date.today())
        logger.info(f"当前季度: {quarter}")
        
        # 测试字典扁平化
        nested_dict = {"a": {"b": {"c": 1}}, "d": 2}
        flattened = flatten_dict(nested_dict)
        logger.info(f"字典扁平化: {flattened}")
        
        logger.info("🎉 辅助函数测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 辅助函数测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    logger = get_logger()
    logger.info("=" * 60)
    logger.info("开始运行重构成果测试套件")
    logger.info("=" * 60)
    
    tests = [
        ("模块导入测试", test_imports),
        ("数据模型测试", test_data_models),
        ("配置系统测试", test_config_system),
        ("验证系统测试", test_validation_system),
        ("辅助函数测试", test_helper_functions),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 {test_name} 执行异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！重构成果验证成功！")
        return True
    else:
        logger.warning(f"⚠️ 有 {total - passed} 个测试失败，需要进一步检查")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="量化投资系统")
    parser.add_argument("--test", action="store_true", help="运行测试套件")
    parser.add_argument("--version", action="store_true", help="显示版本信息")
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    ensure_dir("logs")
    
    # 设置日志
    logger = get_logger()
    
    if args.version:
        print("量化投资系统 V0.1.0")
        print("重构版本 - 测试阶段")
        return
    
    if args.test:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    
    # 默认显示帮助
    parser.print_help()

if __name__ == "__main__":
    main()
