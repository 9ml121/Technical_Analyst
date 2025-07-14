#!/usr/bin/env python3
"""
测试运行脚本

提供便捷的测试运行和管理功能
"""

import sys
import argparse
import subprocess
from pathlib import Path

def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/",
        "-m", "not integration",
        "--tb=short",
        "-v"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0

def run_integration_tests():
    """运行集成测试"""
    print("🔗 运行集成测试...")
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/",
        "-m", "integration",
        "--tb=short",
        "-v"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0

def run_all_tests():
    """运行所有测试"""
    print("🚀 运行所有测试...")
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--tb=short",
        "-v"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0

def run_coverage_tests():
    """运行测试并生成覆盖率报告"""
    print("📊 运行测试并生成覆盖率报告...")
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:output/coverage",
        "--tb=short",
        "-v"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    
    if result.returncode == 0:
        print("\n📈 覆盖率报告已生成:")
        print("   - 终端报告: 已显示")
        print("   - HTML报告: output/coverage/index.html")
    
    return result.returncode == 0

def run_fast_tests():
    """运行快速测试（排除慢速和集成测试）"""
    print("⚡ 运行快速测试...")
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", "not slow and not integration",
        "--tb=line",
        "-q"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0

def run_specific_test(test_path):
    """运行特定测试"""
    print(f"🎯 运行特定测试: {test_path}")
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "--tb=short",
        "-v"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0

def run_tests_by_marker(marker):
    """按标记运行测试"""
    print(f"🏷️ 运行标记为 '{marker}' 的测试...")
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", marker,
        "--tb=short",
        "-v"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0

def check_test_environment():
    """检查测试环境"""
    print("🔍 检查测试环境...")
    
    # 检查pytest是否安装
    try:
        import pytest
        print(f"✅ pytest 版本: {pytest.__version__}")
    except ImportError:
        print("❌ pytest 未安装")
        return False
    
    # 检查测试目录
    test_dir = Path("tests")
    if not test_dir.exists():
        print("❌ tests 目录不存在")
        return False
    
    unit_dir = test_dir / "unit"
    integration_dir = test_dir / "integration"
    
    if unit_dir.exists():
        unit_tests = list(unit_dir.glob("test_*.py"))
        print(f"✅ 单元测试文件: {len(unit_tests)} 个")
    else:
        print("⚠️ tests/unit 目录不存在")
    
    if integration_dir.exists():
        integration_tests = list(integration_dir.glob("test_*.py"))
        print(f"✅ 集成测试文件: {len(integration_tests)} 个")
    else:
        print("⚠️ tests/integration 目录不存在")
    
    # 检查src目录
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ src 目录不存在")
        return False
    
    print("✅ src 目录存在")
    
    # 检查配置文件
    pytest_ini = Path("pytest.ini")
    if pytest_ini.exists():
        print("✅ pytest.ini 配置文件存在")
    else:
        print("⚠️ pytest.ini 配置文件不存在")
    
    return True

def clean_test_artifacts():
    """清理测试产生的文件"""
    print("🧹 清理测试产生的文件...")
    
    artifacts = [
        ".pytest_cache",
        "__pycache__",
        "*.pyc",
        ".coverage",
        "output/coverage",
        "output/test-results.xml"
    ]
    
    import shutil
    import glob
    
    for pattern in artifacts:
        if pattern.startswith(".") and not pattern.startswith("*."):
            # 目录
            if Path(pattern).exists():
                if Path(pattern).is_dir():
                    shutil.rmtree(pattern)
                    print(f"   删除目录: {pattern}")
                else:
                    Path(pattern).unlink()
                    print(f"   删除文件: {pattern}")
        else:
            # 文件模式
            for file_path in glob.glob(pattern, recursive=True):
                if Path(file_path).is_file():
                    Path(file_path).unlink()
                    print(f"   删除文件: {file_path}")
                elif Path(file_path).is_dir():
                    shutil.rmtree(file_path)
                    print(f"   删除目录: {file_path}")
    
    print("✅ 清理完成")

def generate_test_report():
    """生成测试报告"""
    print("📋 生成测试报告...")
    
    # 确保输出目录存在
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--tb=short",
        "--junit-xml=output/test-results.xml",
        "--html=output/test-report.html",
        "--self-contained-html",
        "-v"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    
    if result.returncode == 0:
        print("\n📊 测试报告已生成:")
        print("   - JUnit XML: output/test-results.xml")
        print("   - HTML报告: output/test-report.html")
    
    return result.returncode == 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="量化投资系统测试运行器")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 单元测试命令
    subparsers.add_parser('unit', help='运行单元测试')
    
    # 集成测试命令
    subparsers.add_parser('integration', help='运行集成测试')
    
    # 所有测试命令
    subparsers.add_parser('all', help='运行所有测试')
    
    # 覆盖率测试命令
    subparsers.add_parser('coverage', help='运行测试并生成覆盖率报告')
    
    # 快速测试命令
    subparsers.add_parser('fast', help='运行快速测试')
    
    # 特定测试命令
    specific_parser = subparsers.add_parser('specific', help='运行特定测试')
    specific_parser.add_argument('path', help='测试文件或目录路径')
    
    # 按标记运行命令
    marker_parser = subparsers.add_parser('marker', help='按标记运行测试')
    marker_parser.add_argument('marker', help='测试标记')
    
    # 环境检查命令
    subparsers.add_parser('check', help='检查测试环境')
    
    # 清理命令
    subparsers.add_parser('clean', help='清理测试产生的文件')
    
    # 报告生成命令
    subparsers.add_parser('report', help='生成测试报告')
    
    args = parser.parse_args()
    
    if args.command == 'unit':
        success = run_unit_tests()
    elif args.command == 'integration':
        success = run_integration_tests()
    elif args.command == 'all':
        success = run_all_tests()
    elif args.command == 'coverage':
        success = run_coverage_tests()
    elif args.command == 'fast':
        success = run_fast_tests()
    elif args.command == 'specific':
        success = run_specific_test(args.path)
    elif args.command == 'marker':
        success = run_tests_by_marker(args.marker)
    elif args.command == 'check':
        success = check_test_environment()
    elif args.command == 'clean':
        clean_test_artifacts()
        success = True
    elif args.command == 'report':
        success = generate_test_report()
    else:
        parser.print_help()
        success = True
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
