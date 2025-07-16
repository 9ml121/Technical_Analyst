#!/usr/bin/env python3
"""
NumPy 2.0兼容性修复脚本

解决akshare、pandas等包与NumPy 2.0的兼容性问题
"""

import subprocess
import sys
import os


def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_package_version(package):
    """检查包版本"""
    success, stdout, stderr = run_command(f"pip show {package}")
    if success:
        for line in stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':')[1].strip()
    return None


def fix_numpy_compatibility():
    """修复NumPy兼容性问题"""
    print("🔧 开始修复NumPy 2.0兼容性问题...")

    # 检查当前NumPy版本
    numpy_version = check_package_version("numpy")
    print(f"当前NumPy版本: {numpy_version}")

    if numpy_version and numpy_version.startswith('2'):
        print("⚠️  检测到NumPy 2.0，可能存在兼容性问题")

        # 方案1: 降级到NumPy 1.x
        print("\n📦 方案1: 降级NumPy到1.x版本")
        success, stdout, stderr = run_command(
            "pip install 'numpy<2' --force-reinstall")
        if success:
            print("✅ NumPy降级成功")
        else:
            print(f"❌ NumPy降级失败: {stderr}")

        # 方案2: 更新相关包
        print("\n📦 方案2: 更新相关包到最新版本")
        packages_to_update = [
            "pandas",
            "pyarrow",
            "numexpr",
            "bottleneck",
            "akshare"
        ]

        for package in packages_to_update:
            print(f"更新 {package}...")
            success, stdout, stderr = run_command(
                f"pip install --upgrade {package}")
            if success:
                print(f"✅ {package} 更新成功")
            else:
                print(f"❌ {package} 更新失败: {stderr}")

    else:
        print("✅ NumPy版本正常，无需修复")

    # 验证修复结果
    print("\n🔍 验证修复结果...")
    success, stdout, stderr = run_command(
        "python -c 'import numpy; import pandas; import akshare; print(\"✅ 所有包导入成功\")'")
    if success:
        print("✅ 兼容性问题已修复")
    else:
        print(f"❌ 仍有兼容性问题: {stderr}")


def create_requirements_fixed():
    """创建修复后的requirements文件"""
    print("\n📝 创建修复后的requirements.txt...")

    requirements_content = """# 修复NumPy 2.0兼容性问题的依赖
numpy<2
pandas>=2.0.0
pyarrow>=14.0.0
numexpr>=2.8.0
bottleneck>=1.3.0
akshare>=1.12.0
yfinance>=0.2.0
requests>=2.31.0
"""

    with open("requirements_fixed.txt", "w") as f:
        f.write(requirements_content)

    print("✅ 已创建 requirements_fixed.txt")


if __name__ == "__main__":
    fix_numpy_compatibility()
    create_requirements_fixed()

    print("\n🎯 修复完成！建议执行以下命令安装修复后的依赖:")
    print("pip install -r requirements_fixed.txt")
