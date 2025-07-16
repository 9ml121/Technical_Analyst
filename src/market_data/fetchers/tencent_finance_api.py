#!/usr/bin/env python3
"""
腾讯财经API

免费港股数据源，数据稳定，实现简单
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import time

logger = logging.getLogger(__name__)


class TencentFinanceAPI:
    """腾讯财经API"""

    def __init__(self):
        """初始化腾讯财经API"""
        self.base_url = "http://qt.gtimg.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_stock_detail(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票实时详情

        Args:
            stock_code: 股票代码

        Returns:
            股票详情数据
        """
        try:
            # 腾讯财经的港股代码格式：hk00700
            if stock_code.startswith(('00', '01', '02', '03', '04', '05')):
                tencent_code = f"hk{stock_code}"
            else:
                tencent_code = stock_code

            url = f"{self.base_url}/q={tencent_code}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # 解析返回的数据
            data = self._parse_tencent_response(response.text, tencent_code)
            if data:
                data['source'] = 'tencent_finance'

            return data

        except Exception as e:
            logger.error(f"腾讯财经获取股票详情失败 {stock_code}: {e}")
            return None

    def get_historical_data(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """
        获取历史数据（腾讯财经主要提供实时数据，历史数据有限）

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            历史数据列表
        """
        try:
            # 腾讯财经的历史数据API
            if stock_code.startswith(('00', '01', '02', '03', '04', '05')):
                tencent_code = f"hk{stock_code}"
            else:
                tencent_code = stock_code

            # 获取最近几天的数据
            url = f"http://ifzq.gtimg.cn/appstock/app/kline/mkline"
            params = {
                'param': f"{tencent_code}.day",
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': '101',  # 日线
                'fqt': '0',    # 不复权
                'beg': start_date.strftime('%Y%m%d'),
                'end': end_date.strftime('%Y%m%d'),
                'smplmt': '1000',
                'lmt': '1000'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return self._parse_historical_data(data, tencent_code)

        except Exception as e:
            logger.error(f"腾讯财经获取历史数据失败 {stock_code}: {e}")
            return None

    def _parse_tencent_response(self, response_text: str, stock_code: str) -> Optional[Dict[str, Any]]:
        """解析腾讯财经响应数据"""
        try:
            # 腾讯财经返回格式：v_hk00700="51~腾讯控股~00700~500.00~..."
            if '~' not in response_text:
                return None

            # 提取数据部分
            data_part = response_text.split('=')[1].strip('"')
            fields = data_part.split('~')

            if len(fields) < 40:
                return None

            # 解析字段，添加安全的数值转换
            def safe_float(value, default=0.0):
                try:
                    return float(value) if value else default
                except (ValueError, TypeError):
                    return default

            def safe_int(value, default=0):
                try:
                    return int(float(value)) if value else default
                except (ValueError, TypeError):
                    return default

            return {
                'code': fields[2],
                'name': fields[1],
                'current_price': safe_float(fields[3]),
                'open': safe_float(fields[5]),
                'high': safe_float(fields[33]),
                'low': safe_float(fields[34]),
                'volume': safe_int(fields[6]),
                'amount': safe_float(fields[37]),
                'pct_change': safe_float(fields[32]),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"解析腾讯财经响应失败: {e}")
            return None

    def _parse_historical_data(self, data: Dict, stock_code: str) -> List[Dict[str, Any]]:
        """解析历史数据"""
        result = []

        try:
            if 'data' not in data or stock_code not in data['data']:
                return result

            stock_data = data['data'][stock_code]
            if 'day' not in stock_data:
                return result

            day_data = stock_data['day']
            for item in day_data:
                # 腾讯财经历史数据格式：['2025-01-15', '500.00', '501.00', '502.00', '499.00', '1000000', '500000000']
                if len(item) >= 7:
                    data_item = {
                        'date': item[0],
                        'open': float(item[1]),
                        'close': float(item[2]),
                        'high': float(item[3]),
                        'low': float(item[4]),
                        'volume': int(item[5]),
                        'amount': float(item[6]),
                        'pct_change': 0.0,  # 需要自己计算
                        'source': 'tencent_finance'
                    }
                    result.append(data_item)

        except Exception as e:
            logger.error(f"解析腾讯财经历史数据失败: {e}")

        return result

    def get_market_status(self) -> Dict[str, Any]:
        """获取市场状态"""
        try:
            # 获取港股市场状态
            url = f"{self.base_url}/q=hkHSI"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = self._parse_tencent_response(response.text, "hkHSI")

            return {
                'market': '港股',
                'status': '正常' if data else '未知',
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_available': data is not None
            }

        except Exception as e:
            logger.error(f"获取市场状态失败: {e}")
            return {
                'market': '港股',
                'status': '未知',
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_available': False
            }

    def test_connection(self) -> bool:
        """测试连接"""
        try:
            # 测试获取腾讯控股的数据
            data = self.get_stock_detail("00700")
            return data is not None
        except Exception as e:
            logger.error(f"腾讯财经连接测试失败: {e}")
            return False
