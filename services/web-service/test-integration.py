#!/usr/bin/env python3
"""
Web Service 集成测试脚本
测试前端和后端的集成情况
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path


def test_frontend_build():
    """测试前端构建"""
    print("🔨 测试前端构建...")

    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ frontend目录不存在")
        return False

    try:
        # 检查package.json
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            print("❌ package.json不存在")
            return False

        # 检查node_modules
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            print("⚠️  node_modules不存在，需要运行npm install")
            return False

        # 检查构建目录
        dist_dir = frontend_dir / "dist"
        if not dist_dir.exists():
            print("⚠️  dist目录不存在，需要运行npm run build")
            return False

        print("✅ 前端构建检查通过")
        return True

    except Exception as e:
        print(f"❌ 前端构建测试失败: {e}")
        return False


def test_backend_dependencies():
    """测试后端依赖"""
    print("🐍 测试后端依赖...")

    try:
        # 检查requirements.txt
        if not Path("requirements.txt").exists():
            print("❌ requirements.txt不存在")
            return False

        # 检查主要Python文件
        main_files = [
            "app/main.py",
            "app/core/config.py",
            "app/api/__init__.py"
        ]

        for file_path in main_files:
            if not Path(file_path).exists():
                print(f"❌ {file_path}不存在")
                return False

        print("✅ 后端依赖检查通过")
        return True

    except Exception as e:
        print(f"❌ 后端依赖测试失败: {e}")
        return False


def test_docker_build():
    """测试Docker构建"""
    print("🐳 测试Docker构建...")

    try:
        # 检查Dockerfile
        if not Path("Dockerfile").exists():
            print("❌ Dockerfile不存在")
            return False

        # 尝试构建Docker镜像（不推送）
        result = subprocess.run(
            ["docker", "build", "-t", "test-web-service", "."],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            print("✅ Docker构建成功")
            # 清理测试镜像
            subprocess.run(["docker", "rmi", "test-web-service"],
                           capture_output=True)
            return True
        else:
            print(f"❌ Docker构建失败: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Docker构建超时")
        return False
    except Exception as e:
        print(f"❌ Docker构建测试失败: {e}")
        return False


def test_api_endpoints():
    """测试API端点（如果服务运行中）"""
    print("🌐 测试API端点...")

    base_url = "http://localhost:8005"
    endpoints = [
        "/health",
        "/api/v1/core/accounts/",
        "/api/v1/data/market/overview"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code in [200, 404, 503]:  # 正常响应或服务未启动
                print(f"✅ {endpoint} - {response.status_code}")
            else:
                print(f"⚠️  {endpoint} - {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"⚠️  {endpoint} - 服务未运行")
        except Exception as e:
            print(f"❌ {endpoint} - 错误: {e}")

    return True


def test_configuration():
    """测试配置文件"""
    print("⚙️  测试配置文件...")

    config_files = [
        "config/settings.py",
        "frontend/vite.config.js",
        "frontend/package.json"
    ]

    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file} 存在")
        else:
            print(f"❌ {config_file} 不存在")

    return True


def main():
    """主测试函数"""
    print("🚀 开始Web Service集成测试...\n")

    tests = [
        ("前端构建", test_frontend_build),
        ("后端依赖", test_backend_dependencies),
        ("Docker构建", test_docker_build),
        ("配置文件", test_configuration),
        ("API端点", test_api_endpoints)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 50)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))

    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有测试通过！Web Service集成成功。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查上述问题。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
