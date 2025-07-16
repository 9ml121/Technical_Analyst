#!/usr/bin/env python3
"""
纯免费数据源整合器

实现方案一：akshare + Yahoo Finance + 东方财富API
完全免费，适合个人开发、学习研究、小规模应用
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FreeDataSourceType(Enum):
    """免费数据源类型"""
    AKSHARE = "akshare"
    YAHOO_FINANCE = "yahoo_finance"
    EASTMONEY = "eastmoney"
    SINA_FINANCE = "sina_finance"
    TENCENT_FINANCE = "tencent_finance"


@dataclass
class FreeDataSourceConfig:
    """免费数据源配置"""
    name: str
    type: FreeDataSourceType
    priority: int  # 优先级，数字越小优先级越高
    supports_a_stock: bool = True
    supports_h_stock: bool = False
    supports_us_stock: bool = False
    rate_limit: Optional[int] = None  # 每分钟请求限制
    description: str = ""


class FreeDataSourcesFetcher:
    """纯免费数据源整合器"""

    def __init__(self):
        """初始化免费数据源整合器"""
        self.data_sources = self._initialize_free_data_sources()
        self.source_instances = {}
        self.last_request_time = {}  # 用于限流

        # 初始化各个数据源
        self._init_data_sources()

    def _initialize_free_data_sources(self) -> Dict[str, FreeDataSourceConfig]:
        """初始化免费数据源配置"""
        return {
            "akshare": FreeDataSourceConfig(
                name="akshare",
                type=FreeDataSourceType.AKSHARE,
                priority=1,
                supports_a_stock=True,
                supports_h_stock=True,
                supports_us_stock=False,
                rate_limit=100,
                description="开源免费，A股数据优秀，港股数据不稳定"
            ),
            "yahoo_finance": FreeDataSourceConfig(
                name="yahoo_finance",
                type=FreeDataSourceType.YAHOO_FINANCE,
                priority=2,
                supports_a_stock=False,
                supports_h_stock=True,
                supports_us_stock=True,
                rate_limit=2000,
                description="免费，港股和美股数据优秀"
            ),
            "tencent_finance": FreeDataSourceConfig(
                name="tencent_finance",
                type=FreeDataSourceType.TENCENT_FINANCE,
                priority=3,
                supports_a_stock=False,
                supports_h_stock=True,
                supports_us_stock=False,
                rate_limit=200,
                description="免费，港股数据稳定，实现简单"
            ),
            "eastmoney": FreeDataSourceConfig(
                name="eastmoney",
                type=FreeDataSourceType.EASTMONEY,
                priority=4,
                supports_a_stock=True,
                supports_h_stock=False,
                supports_us_stock=False,
                rate_limit=60,
                description="免费，A股实时数据优秀"
            ),
            "sina_finance": FreeDataSourceConfig(
                name="sina_finance",
                type=FreeDataSourceType.SINA_FINANCE,
                priority=5,
                supports_a_stock=True,
                supports_h_stock=True,
                supports_us_stock=False,
                rate_limit=100,
                description="免费，数据质量一般但稳定"
            )
        }

    def _init_data_sources(self):
        """初始化各个数据源实例"""
        # 初始化akshare
        try:
            import akshare as ak
            self.source_instances["akshare"] = ak
            logger.info("akshare数据源初始化成功")
        except ImportError:
            logger.warning("akshare未安装，跳过初始化")

        # 初始化Yahoo Finance
        try:
            import yfinance as yf
            self.source_instances["yahoo_finance"] = yf
            logger.info("Yahoo Finance数据源初始化成功")
        except ImportError:
            logger.warning("yfinance未安装，跳过初始化")

        # 初始化东方财富API
        try:
            from .eastmoney_api import EastMoneyAPI
            self.source_instances["eastmoney"] = EastMoneyAPI()
            logger.info("东方财富API初始化成功")
        except Exception as e:
            logger.warning(f"东方财富API初始化失败: {e}")

        # 初始化新浪财经API
        try:
            from .sina_finance_api import SinaFinanceAPI
            self.source_instances["sina_finance"] = SinaFinanceAPI()
            logger.info("新浪财经API初始化成功")
        except Exception as e:
            logger.warning(f"新浪财经API初始化失败: {e}")

        # 初始化腾讯财经API
        try:
            from .tencent_finance_api import TencentFinanceAPI
            self.source_instances["tencent_finance"] = TencentFinanceAPI()
            logger.info("腾讯财经API初始化成功")
        except Exception as e:
            logger.warning(f"腾讯财经API初始化失败: {e}")

    def _check_rate_limit(self, source_name: str) -> bool:
        """检查请求频率限制"""
        if source_name not in self.data_sources:
            return True

        config = self.data_sources[source_name]
        if not config.rate_limit:
            return True

        current_time = time.time()
        last_time = self.last_request_time.get(source_name, 0)

        # 检查是否超过频率限制
        if current_time - last_time < 60.0 / config.rate_limit:
            return False

        self.last_request_time[source_name] = current_time
        return True

    def get_available_sources(self, market_type: str = "a_stock") -> List[str]:
        """获取可用的数据源列表"""
        available = []

        for name, config in self.data_sources.items():
            if name not in self.source_instances:
                continue

            if market_type == "a_stock" and config.supports_a_stock:
                available.append(name)
            elif market_type == "h_stock" and config.supports_h_stock:
                available.append(name)
            elif market_type == "us_stock" and config.supports_us_stock:
                available.append(name)

        # 按优先级排序
        available.sort(key=lambda x: self.data_sources[x].priority)
        return available

    def get_historical_data_with_fallback(self,
                                          stock_code: str,
                                          start_date: date,
                                          end_date: date,
                                          market_type: str = "auto") -> Optional[List[Dict[str, Any]]]:
        """
        获取历史数据，支持故障转移

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            market_type: 市场类型 (auto/a_stock/h_stock/us_stock)

        Returns:
            历史数据列表
        """
        # 自动判断市场类型
        if market_type == "auto":
            if stock_code.startswith(('6', '0', '3')) and not stock_code.startswith(('00', '01', '02', '03', '04', '05')):
                market_type = "a_stock"
            elif stock_code.startswith(('00', '01', '02', '03', '04', '05')):
                market_type = "h_stock"
            else:
                market_type = "a_stock"  # 默认A股

        available_sources = self.get_available_sources(market_type)

        if not available_sources:
            logger.error(f"没有可用的数据源支持 {market_type} 市场")
            return None

        for source_name in available_sources:
            try:
                # 检查频率限制
                if not self._check_rate_limit(source_name):
                    logger.warning(f"数据源 {source_name} 请求频率过高，跳过")
                    continue

                logger.info(f"尝试使用 {source_name} 获取 {stock_code} 的历史数据")

                data = self._fetch_from_source(
                    source_name, stock_code, start_date, end_date)

                if data and len(data) > 0:
                    logger.info(f"成功从 {source_name} 获取到 {len(data)} 条数据")
                    return data
                else:
                    logger.warning(f"从 {source_name} 获取的数据为空")

            except Exception as e:
                logger.error(f"从 {source_name} 获取数据失败: {e}")
                continue

        logger.error(f"所有免费数据源都无法获取 {stock_code} 的历史数据")
        return None

    def _fetch_from_source(self, source_name: str, stock_code: str,
                           start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从指定数据源获取数据"""

        if source_name == "akshare":
            return self._fetch_from_akshare(stock_code, start_date, end_date)
        elif source_name == "yahoo_finance":
            return self._fetch_from_yahoo(stock_code, start_date, end_date)
        elif source_name == "tencent_finance":
            return self._fetch_from_tencent(stock_code, start_date, end_date)
        elif source_name == "eastmoney":
            return self._fetch_from_eastmoney(stock_code, start_date, end_date)
        elif source_name == "sina_finance":
            return self._fetch_from_sina(stock_code, start_date, end_date)

        return None

    def _fetch_from_akshare(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从akshare获取数据"""
        try:
            import akshare as ak
            import pandas as pd

            start_date_str = start_date.strftime('%Y%m%d')
            end_date_str = end_date.strftime('%Y%m%d')

            if stock_code.startswith(('6', '0', '3')):
                # A股数据
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date=start_date_str,
                    end_date=end_date_str,
                    adjust=""
                )
            else:
                # 港股数据 - 改进代码格式
                try:
                    # 尝试不同的港股代码格式
                    hk_codes = []
                    if len(stock_code) == 5:
                        hk_codes.append(stock_code)
                    if len(stock_code) == 4:
                        hk_codes.append(stock_code)
                    if len(stock_code) == 3:
                        hk_codes.append(f"0{stock_code}")

                    df = None
                    for hk_code in hk_codes:
                        try:
                            logger.info(f"尝试akshare港股代码: {hk_code}")
                            df = ak.stock_hk_hist(
                                symbol=hk_code,
                                period="daily",
                                start_date=start_date_str,
                                end_date=end_date_str,
                                adjust=""
                            )
                            if not df.empty:
                                break
                        except Exception as e:
                            logger.debug(f"akshare港股代码 {hk_code} 失败: {e}")
                            continue

                    if df is None or df.empty:
                        logger.warning(f"akshare所有港股代码格式都失败: {stock_code}")
                        return None

                except Exception as e:
                    logger.error(f"akshare港股数据获取失败: {e}")
                    return None

            if df.empty:
                return None

            # 转换为统一格式
            result = []
            for _, row in df.iterrows():
                if '日期' in df.columns:
                    # A股数据格式
                    data = {
                        'date': row['日期'],
                        'open': float(row['开盘']),
                        'close': float(row['收盘']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'volume': int(row['成交量']),
                        'amount': float(row.get('成交额', 0)),
                        'pct_change': float(row.get('涨跌幅', 0)),
                        'source': 'akshare'
                    }
                else:
                    # 港股数据格式
                    data = {
                        'date': row['日期'],
                        'open': float(row['开盘']),
                        'close': float(row['收盘']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'volume': int(row['成交量']),
                        'amount': float(row.get('成交额', 0)),
                        'pct_change': 0.0,
                        'source': 'akshare'
                    }
                result.append(data)

            return result

        except Exception as e:
            logger.error(f"akshare获取数据失败: {e}")
            return None

    def _fetch_from_yahoo(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从Yahoo Finance获取数据"""
        try:
            import yfinance as yf

            # 改进Yahoo格式的代码转换
            if stock_code.startswith('6'):
                yahoo_code = f"{stock_code}.SS"  # 上海证券交易所
            elif stock_code.startswith(('0', '3')) and not stock_code.startswith(('00', '01', '02', '03', '04', '05')):
                yahoo_code = f"{stock_code}.SZ"  # 深圳证券交易所
            elif stock_code.startswith(('00', '01', '02', '03', '04', '05')):
                # 港股代码，需要去掉前导零
                if len(stock_code) == 5:
                    # 去掉前导零，如00700 -> 700
                    clean_code = stock_code.lstrip('0')
                    yahoo_code = f"{clean_code}.HK"
                else:
                    yahoo_code = f"{stock_code}.HK"
            else:
                # 其他情况，尝试多种港股格式
                clean_code = stock_code.lstrip('0')  # 去掉前导零
                yahoo_codes = [
                    f"{clean_code}.HK",
                    f"{stock_code}.HK",
                    f"{stock_code.zfill(4)}.HK",
                    f"{stock_code.zfill(5)}.HK"
                ]

                # 尝试不同的代码格式
                for code in yahoo_codes:
                    try:
                        logger.info(f"尝试Yahoo Finance代码: {code}")
                        ticker = yf.Ticker(code)
                        df = ticker.history(start=start_date, end=end_date)

                        if not df.empty:
                            logger.info(f"成功使用Yahoo Finance代码: {code}")
                            break
                        else:
                            logger.debug(f"Yahoo Finance代码 {code} 返回空数据")
                    except Exception as e:
                        logger.debug(f"Yahoo Finance代码 {code} 失败: {e}")
                        continue
                else:
                    logger.warning(f"所有Yahoo Finance代码格式都失败: {stock_code}")
                    return None

                return self._convert_yahoo_data(df)

            logger.info(f"尝试Yahoo Finance代码: {yahoo_code}")
            ticker = yf.Ticker(yahoo_code)
            df = ticker.history(start=start_date, end=end_date)

            if df.empty:
                logger.warning(f"Yahoo Finance返回空数据: {yahoo_code}")
                return None

            return self._convert_yahoo_data(df)

        except Exception as e:
            logger.error(f"Yahoo Finance获取数据失败: {e}")
            return None

    def _convert_yahoo_data(self, df) -> List[Dict[str, Any]]:
        """转换Yahoo Finance数据格式"""
        result = []
        for date_str, row in df.iterrows():
            data = {
                'date': date_str.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'close': float(row['Close']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'volume': int(row['Volume']),
                'amount': 0.0,  # Yahoo没有成交额
                'pct_change': 0.0,  # 需要自己计算
                'source': 'yahoo_finance'
            }
            result.append(data)
        return result

    def _fetch_from_tencent(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从腾讯财经API获取数据"""
        try:
            api = self.source_instances["tencent_finance"]
            data = api.get_historical_data(stock_code, start_date, end_date)

            if data:
                # 添加数据源标识
                for item in data:
                    item['source'] = 'tencent_finance'

            return data

        except Exception as e:
            logger.error(f"腾讯财经API获取数据失败: {e}")
            return None

    def _fetch_from_eastmoney(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从东方财富API获取数据"""
        try:
            api = self.source_instances["eastmoney"]
            data = api.get_historical_data(stock_code, start_date, end_date)

            if data:
                # 添加数据源标识
                for item in data:
                    item['source'] = 'eastmoney'

            return data

        except Exception as e:
            logger.error(f"东方财富API获取数据失败: {e}")
            return None

    def _fetch_from_sina(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从新浪财经API获取数据"""
        try:
            api = self.source_instances["sina_finance"]
            data = api.get_historical_data(stock_code, start_date, end_date)

            if data:
                # 添加数据源标识
                for item in data:
                    item['source'] = 'sina_finance'

            return data

        except Exception as e:
            logger.error(f"新浪财经API获取数据失败: {e}")
            return None

    def get_realtime_data(self, stock_codes: List[str]) -> List[Dict[str, Any]]:
        """获取实时数据"""
        result = []

        for stock_code in stock_codes:
            try:
                # 优先使用东方财富API获取实时数据
                if "eastmoney" in self.source_instances:
                    api = self.source_instances["eastmoney"]
                    data = api.get_stock_detail(stock_code)
                    if data:
                        data['source'] = 'eastmoney'
                        result.append(data)
                        continue

                # 备用：使用akshare获取实时数据
                if "akshare" in self.source_instances:
                    # akshare的实时数据获取逻辑
                    pass

            except Exception as e:
                logger.error(f"获取 {stock_code} 实时数据失败: {e}")

        return result

    def get_market_status(self) -> Dict[str, Any]:
        """获取市场状态"""
        try:
            # 尝试从东方财富API获取市场状态
            if "eastmoney" in self.source_instances:
                api = self.source_instances["eastmoney"]
                return api.get_market_status()
        except Exception as e:
            logger.error(f"获取市场状态失败: {e}")

        # 默认返回
        return {
            'market': '未知',
            'status': '未知',
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_available': False
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        available_sources = []
        unavailable_sources = []

        for name, config in self.data_sources.items():
            if name in self.source_instances:
                available_sources.append({
                    'name': name,
                    'description': config.description,
                    'supports_a_stock': config.supports_a_stock,
                    'supports_h_stock': config.supports_h_stock,
                    'supports_us_stock': config.supports_us_stock
                })
            else:
                unavailable_sources.append(name)

        return {
            'total_sources': len(self.data_sources),
            'available_sources': len(available_sources),
            'unavailable_sources': unavailable_sources,
            'available_sources_detail': available_sources,
            'cost': '¥0/月 (完全免费)',
            'recommendations': [
                'akshare作为A股主要数据源',
                'Yahoo Finance作为港股主要数据源',
                '东方财富API作为实时数据源',
                '新浪财经API作为备用数据源'
            ]
        }
