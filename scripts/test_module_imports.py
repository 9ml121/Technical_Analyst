#!/usr/bin/env python3
"""
模块导入测试脚本

验证重构后的模块依赖和导入是否正常工作
"""
import sys
import os
from pathlib import Path
import importlib
import traceback
from typing import Dict, List, Tuple

# 添加src目录到Python路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def test_module_import(module_name: str, description: str = "") -> Tuple[bool, str]:
    """
    测试单个模块的导入

    Args:
        module_name: 模块名称
        description: 模块描述

    Returns:
        (是否成功, 错误信息)
    """
    try:
        module = importlib.import_module(module_name)
        return True, f"✅ {description or module_name} 导入成功"
    except ImportError as e:
        return False, f"❌ {description or module_name} 导入失败: {e}"
    except Exception as e:
        return False, f"❌ {description or module_name} 导入异常: {e}"


def test_quant_system_modules() -> List[Tuple[bool, str]]:
    """测试量化系统核心模块"""
    print("=" * 60)
    print("测试量化系统核心模块导入")
    print("=" * 60)

    modules_to_test = [
        ("quant_system", "量化系统主模块"),
        ("quant_system.core", "核心功能模块"),
        ("quant_system.models", "数据模型模块"),
        ("quant_system.utils", "工具模块"),
        ("quant_system.core.data_provider", "数据提供器"),
        ("quant_system.core.strategy_engine", "策略引擎"),
        ("quant_system.core.backtest_engine", "回测引擎"),
        ("quant_system.core.trading_strategy", "交易策略"),
        ("quant_system.core.feature_extraction", "特征提取"),
        ("quant_system.core.analysis_module", "分析模块"),
        ("quant_system.core.ml_enhanced_strategy", "机器学习策略"),
        ("quant_system.models.stock_data", "股票数据模型"),
        ("quant_system.models.strategy_models", "策略模型"),
        ("quant_system.models.backtest_models", "回测模型"),
        ("quant_system.utils.config_loader", "配置加载器"),
        ("quant_system.utils.logger", "日志工具"),
        ("quant_system.utils.validators", "验证工具"),
        ("quant_system.utils.helpers", "辅助函数"),
        ("quant_system.utils.performance", "性能工具"),
        ("quant_system.utils.cache", "缓存工具"),
        ("quant_system.utils.concurrent", "并发工具"),
        ("quant_system.utils.config_validator", "配置验证器"),
    ]

    results = []
    for module_name, description in modules_to_test:
        success, message = test_module_import(module_name, description)
        results.append((success, message))
        print(message)

    return results


def test_market_data_modules() -> List[Tuple[bool, str]]:
    """测试市场数据模块"""
    print("\n" + "=" * 60)
    print("测试市场数据模块导入")
    print("=" * 60)

    modules_to_test = [
        ("market_data", "市场数据主模块"),
        ("market_data.fetchers", "数据获取器模块"),
        ("market_data.processors", "数据处理器模块"),
        ("market_data.fetchers.eastmoney_api", "东方财富API"),
        ("market_data.fetchers.tushare_api", "Tushare API"),
        ("market_data.fetchers.free_data_sources", "免费数据源"),
        ("market_data.fetchers.multi_source_fetcher", "多源数据获取器"),
        ("market_data.processors.data_processor", "数据处理器"),
    ]

    results = []
    for module_name, description in modules_to_test:
        success, message = test_module_import(module_name, description)
        results.append((success, message))
        print(message)

    return results


def test_module_factory() -> List[Tuple[bool, str]]:
    """测试模块工厂功能"""
    print("\n" + "=" * 60)
    print("测试模块工厂功能")
    print("=" * 60)

    try:
        from quant_system import ModuleFactory, get_module

        # 测试模块工厂
        factory = ModuleFactory()

        # 测试获取核心模块
        core_modules = [
            "data_provider",
            "strategy_engine",
            "backtest_engine",
            "trading_strategy",
            "feature_extraction",
            "analysis_module",
            "ml_enhanced_strategy"
        ]

        results = []
        for module_name in core_modules:
            try:
                module = factory.get_module(module_name)
                if module is not None:
                    results.append((True, f"✅ 模块工厂获取 {module_name} 成功"))
                else:
                    results.append((False, f"❌ 模块工厂获取 {module_name} 失败"))
            except Exception as e:
                results.append((False, f"❌ 模块工厂获取 {module_name} 异常: {e}"))

        # 测试便捷函数
        try:
            module = get_module("config_loader")
            if module is not None:
                results.append((True, "✅ get_module 便捷函数工作正常"))
            else:
                results.append((False, "❌ get_module 便捷函数失败"))
        except Exception as e:
            results.append((False, f"❌ get_module 便捷函数异常: {e}"))

        return results

    except ImportError as e:
        return [(False, f"❌ 模块工厂导入失败: {e}")]
    except Exception as e:
        return [(False, f"❌ 模块工厂测试异常: {e}")]


def test_web_modules() -> List[Tuple[bool, str]]:
    """测试Web模块"""
    print("\n" + "=" * 60)
    print("测试Web模块导入")
    print("=" * 60)

    # 添加web目录到路径
    web_path = Path(__file__).parent.parent / "web"
    if web_path.exists():
        sys.path.insert(0, str(web_path))

    modules_to_test = [
        ("backend.app", "Web后端应用"),
        ("backend.app.api", "Web API模块"),
        ("backend.app.models", "Web数据模型"),
        ("backend.app.services", "Web服务模块"),
    ]

    results = []
    for module_name, description in modules_to_test:
        success, message = test_module_import(module_name, description)
        results.append((success, message))
        print(message)

    return results


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始模块导入测试")
    print("=" * 80)
    print(f"Python路径: {sys.path[:3]}")  # 显示前3个路径

    all_results = []

    # 测试量化系统模块
    quant_results = test_quant_system_modules()
    all_results.extend(quant_results)

    # 测试市场数据模块
    market_results = test_market_data_modules()
    all_results.extend(market_results)

    # 测试模块工厂
    factory_results = test_module_factory()
    all_results.extend(factory_results)

    # 测试Web模块
    web_results = test_web_modules()
    all_results.extend(web_results)

    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)

    passed = 0
    failed = 0

    for success, message in all_results:
        if success:
            passed += 1
        else:
            failed += 1

    print(f"✅ 通过: {passed} 个")
    print(f"❌ 失败: {failed} 个")
    print(f"📊 总计: {len(all_results)} 个")

    if failed == 0:
        print("\n🎉 所有模块导入测试通过！重构成功！")
        return True
    else:
        print(f"\n⚠️ 有 {failed} 个模块导入失败，需要进一步检查")

        # 显示失败的模块
        print("\n失败的模块:")
        for success, message in all_results:
            if not success:
                print(f"  {message}")

        return False


def main():
    """主函数"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行异常: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
