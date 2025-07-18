#!/usr/bin/env python3
"""
路由检测脚本
检测所有微服务的路由注册情况
"""
import asyncio
import httpx
import json
from typing import Dict, List

# 服务配置
SERVICES = {
    "gateway": "http://localhost:8000",
    "data-service": "http://localhost:8002",
    "core-service": "http://localhost:8001",
    "strategy-service": "http://localhost:8003",
    "notification-service": "http://localhost:8004"
}


async def get_openapi_spec(service_name: str, base_url: str) -> Dict:
    """获取服务的OpenAPI规范"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/openapi.json")
            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f"❌ {service_name}: 无法获取OpenAPI规范 (状态码: {response.status_code})")
                print(f"   响应内容: {response.text[:200]}")
                return {}
    except Exception as e:
        print(f"❌ {service_name}: 连接失败 - {str(e)}")
        return {}


async def get_health_status(service_name: str, base_url: str) -> bool:
    """检查服务健康状态"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/health")
            return response.status_code == 200
    except:
        return False


def extract_routes(openapi_spec: Dict) -> List[str]:
    """从OpenAPI规范中提取路由"""
    routes = []
    if "paths" in openapi_spec:
        for path, methods in openapi_spec["paths"].items():
            for method in methods.keys():
                routes.append(f"{method.upper()} {path}")
    return sorted(routes)


async def test_specific_routes():
    """测试特定的路由"""
    test_routes = [
        # 数据服务路由
        ("data-service", "GET", "/api/v1/stocks/AAPL"),
        ("data-service", "GET", "/api/v1/stocks?market=CN"),
        ("data-service", "GET", "/api/v1/search?keyword=AAPL"),

        # 核心服务路由
        ("core-service", "GET", "/api/v1/analysis/AAPL"),
        ("core-service", "GET", "/api/v1/backtest/strategy1"),

        # 策略服务路由
        ("strategy-service", "GET", "/api/v1/strategies"),
        ("strategy-service", "POST", "/api/v1/strategies"),

        # 通知服务路由
        ("notification-service", "GET", "/api/v1/notifications"),
        ("notification-service", "POST", "/api/v1/notifications"),

        # 网关路由
        ("gateway", "GET", "/api/v1/data/stocks/AAPL"),
        ("gateway", "GET", "/api/v1/core/analysis/AAPL"),
        ("gateway", "GET", "/api/v1/strategy/strategies"),
    ]

    print("\n" + "="*60)
    print("🔍 测试特定路由")
    print("="*60)

    for service_name, method, route in test_routes:
        base_url = SERVICES.get(service_name)
        if not base_url:
            continue

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if method == "GET":
                    response = await client.get(f"{base_url}{route}")
                elif method == "POST":
                    response = await client.post(f"{base_url}{route}")
                else:
                    continue

                status = "✅" if response.status_code < 400 else "❌"
                print(
                    f"{status} {service_name} {method} {route} -> {response.status_code}")

                if response.status_code >= 400:
                    try:
                        error_detail = response.json()
                        print(f"   错误详情: {error_detail}")
                    except:
                        print(f"   错误详情: {response.text[:100]}")

        except Exception as e:
            print(f"❌ {service_name} {method} {route} -> 连接失败: {str(e)}")


async def main():
    """主函数"""
    print("🚀 微服务路由检测")
    print("="*60)

    # 检查服务健康状态
    print("\n📊 服务健康状态:")
    for service_name, base_url in SERVICES.items():
        is_healthy = await get_health_status(service_name, base_url)
        status = "✅ 健康" if is_healthy else "❌ 不健康"
        print(f"  {service_name}: {status}")

    # 获取各服务的路由
    print("\n📋 各服务路由列表:")
    for service_name, base_url in SERVICES.items():
        print(f"\n🔧 {service_name} ({base_url}):")

        openapi_spec = await get_openapi_spec(service_name, base_url)
        if openapi_spec:
            routes = extract_routes(openapi_spec)
            if routes:
                for route in routes:
                    print(f"  {route}")
            else:
                print("  没有找到路由")
        else:
            print("  无法获取路由信息")

    # 测试特定路由
    await test_specific_routes()

    print("\n" + "="*60)
    print("✅ 路由检测完成")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
