"""
测试数据服务迁移
验证从单体架构到微服务架构的数据提供者功能迁移
"""
from shared.utils.helpers import ensure_dir
from shared.models.market_data import StockData
import sys
import os
import requests
import json
from datetime import date, datetime, timedelta
from typing import Dict, List, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DataServiceMigrationTester:
    """数据服务迁移测试器"""

    def __init__(self, base_url: str = "http://localhost:8002"):
        """
        初始化测试器

        Args:
            base_url: 数据服务的基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)

        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}: {message}")

        if data and not success:
            print(f"   错误详情: {data}")

    def test_health_check(self) -> bool:
        """测试健康检查"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/health", timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data", {}).get("status") == "healthy":
                    self.log_test("健康检查", True, "服务运行正常")
                    return True
                else:
                    self.log_test("健康检查", False, "服务状态异常", data)
                    return False
            else:
                self.log_test(
                    "健康检查", False, f"HTTP状态码: {response.status_code}", response.text)
                return False

        except Exception as e:
            self.log_test("健康检查", False, f"请求失败: {str(e)}")
            return False

    def test_get_stock_list(self) -> bool:
        """测试获取股票列表"""
        try:
            # 测试A股列表
            response = self.session.get(
                f"{self.base_url}/api/v1/stocks/list",
                params={"market": "A", "limit": 10},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    stocks = data["data"]
                    if len(stocks) > 0 and all("code" in stock and "name" in stock for stock in stocks):
                        self.log_test("获取股票列表", True, f"成功获取{len(stocks)}只A股")
                        return True
                    else:
                        self.log_test("获取股票列表", False, "返回数据格式错误", data)
                        return False
                else:
                    self.log_test("获取股票列表", False, "API返回失败", data)
                    return False
            else:
                self.log_test(
                    "获取股票列表", False, f"HTTP状态码: {response.status_code}", response.text)
                return False

        except Exception as e:
            self.log_test("获取股票列表", False, f"请求失败: {str(e)}")
            return False

    def test_get_historical_data(self) -> bool:
        """测试获取历史数据"""
        try:
            # 测试获取平安银行最近30天的数据
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            response = self.session.get(
                f"{self.base_url}/api/v1/stocks/000001/history",
                params={
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    history_data = data["data"]
                    if len(history_data) > 0:
                        # 验证数据格式
                        first_record = history_data[0]
                        required_fields = [
                            "code", "date", "open_price", "close_price", "high_price", "low_price", "volume"]

                        if all(field in first_record for field in required_fields):
                            self.log_test("获取历史数据", True,
                                          f"成功获取{len(history_data)}条历史数据")
                            return True
                        else:
                            self.log_test("获取历史数据", False,
                                          "数据字段不完整", first_record)
                            return False
                    else:
                        self.log_test("获取历史数据", False, "未获取到历史数据", data)
                        return False
                else:
                    self.log_test("获取历史数据", False, "API返回失败", data)
                    return False
            else:
                self.log_test(
                    "获取历史数据", False, f"HTTP状态码: {response.status_code}", response.text)
                return False

        except Exception as e:
            self.log_test("获取历史数据", False, f"请求失败: {str(e)}")
            return False

    def test_batch_historical_data(self) -> bool:
        """测试批量获取历史数据"""
        try:
            # 测试批量获取多只股票的数据
            end_date = date.today()
            start_date = end_date - timedelta(days=7)

            request_data = {
                "codes": ["000001", "600000", "300001"],
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/stocks/batch-history",
                json=request_data,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    batch_result = data["data"]
                    successful_codes = data.get("successful_codes", 0)

                    if successful_codes > 0:
                        self.log_test("批量获取历史数据", True,
                                      f"成功获取{successful_codes}只股票数据")
                        return True
                    else:
                        self.log_test("批量获取历史数据", False,
                                      "批量获取失败", batch_result)
                        return False
                else:
                    self.log_test("批量获取历史数据", False, "API返回失败", data)
                    return False
            else:
                self.log_test("批量获取历史数据", False,
                              f"HTTP状态码: {response.status_code}", response.text)
                return False

        except Exception as e:
            self.log_test("批量获取历史数据", False, f"请求失败: {str(e)}")
            return False

    def test_data_summary(self) -> bool:
        """测试获取数据摘要"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/data/summary", timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    summary = data["data"]
                    if "stock_counts" in summary and "total_records" in summary:
                        self.log_test(
                            "获取数据摘要", True, f"数据库记录数: {summary.get('total_records', 0)}")
                        return True
                    else:
                        self.log_test("获取数据摘要", False, "摘要数据不完整", summary)
                        return False
                else:
                    self.log_test("获取数据摘要", False, "API返回失败", data)
                    return False
            else:
                self.log_test(
                    "获取数据摘要", False, f"HTTP状态码: {response.status_code}", response.text)
                return False

        except Exception as e:
            self.log_test("获取数据摘要", False, f"请求失败: {str(e)}")
            return False

    def test_error_handling(self) -> bool:
        """测试错误处理"""
        try:
            # 测试无效股票代码
            response = self.session.get(
                f"{self.base_url}/api/v1/stocks/invalid/history",
                params={
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-15"
                },
                timeout=10
            )

            if response.status_code == 400:
                data = response.json()
                if "无效的股票代码" in data.get("detail", ""):
                    self.log_test("错误处理", True, "正确处理无效股票代码")
                    return True
                else:
                    self.log_test("错误处理", False, "错误信息不正确", data)
                    return False
            else:
                self.log_test(
                    "错误处理", False, f"期望400状态码，实际: {response.status_code}", response.text)
                return False

        except Exception as e:
            self.log_test("错误处理", False, f"请求失败: {str(e)}")
            return False

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("=" * 60)
        print("开始数据服务迁移测试")
        print("=" * 60)

        tests = [
            ("健康检查", self.test_health_check),
            ("获取股票列表", self.test_get_stock_list),
            ("获取历史数据", self.test_get_historical_data),
            ("批量获取历史数据", self.test_batch_historical_data),
            ("获取数据摘要", self.test_data_summary),
            ("错误处理", self.test_error_handling),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"测试执行异常: {str(e)}")

        # 汇总结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)

        for result in self.test_results:
            status = "✅ 通过" if result["success"] else "❌ 失败"
            print(f"{status} {result['test_name']}: {result['message']}")

        print(f"\n总计: {passed}/{total} 个测试通过")

        if passed == total:
            print("🎉 所有测试通过！数据服务迁移成功！")
            return True
        else:
            print(f"⚠️ 有 {total - passed} 个测试失败，需要进一步检查")
            return False

    def save_test_report(self, filename: str = "data_service_migration_test_report.json"):
        """保存测试报告"""
        report = {
            "test_name": "数据服务迁移测试",
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": len([r for r in self.test_results if r["success"]]),
                "failed_tests": len([r for r in self.test_results if not r["success"]])
            }
        }

        ensure_dir("examples")
        with open(f"examples/{filename}", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n测试报告已保存到: examples/{filename}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="数据服务迁移测试")
    parser.add_argument(
        "--url", default="http://localhost:8002", help="数据服务URL")
    parser.add_argument("--report", help="测试报告文件名")

    args = parser.parse_args()

    # 创建测试器
    tester = DataServiceMigrationTester(args.url)

    # 运行测试
    success = tester.run_all_tests()

    # 保存报告
    report_filename = args.report or "data_service_migration_test_report.json"
    tester.save_test_report(report_filename)

    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
