"""
数据提供者服务
将历史数据获取功能迁移到微服务架构
"""
from shared.utils.validators import validate_stock_code
from shared.utils.helpers import ensure_dir, safe_divide
from shared.utils.exceptions import DataSourceError, NetworkError
from shared.models.market_data import StockData, StockInfo
import os
import time
import json
import sqlite3
import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import asdict

# 导入共享模型和工具
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))


logger = logging.getLogger(__name__)


class DataProviderService:
    """数据提供者服务"""

    def __init__(self, db_path: str = './data/stock_data.db', cache_days: int = 1):
        """
        初始化数据提供者服务

        Args:
            db_path: 数据库路径
            cache_days: 缓存天数
        """
        self.db_path = db_path
        self.cache_days = cache_days

        # 确保数据目录存在
        ensure_dir(os.path.dirname(db_path))

        # 初始化数据库
        self._init_database()

        # 配置HTTP会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'http://quote.eastmoney.com/'
        })

        logger.info(f"数据提供者服务初始化完成，数据库: {db_path}")

    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            # 创建股票基本信息表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stock_info (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    market TEXT NOT NULL,
                    list_date TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 创建历史行情数据表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS daily_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    volume INTEGER,
                    amount REAL,
                    change_pct REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(code, date)
                )
            ''')

            # 创建索引
            conn.execute(
                'CREATE INDEX IF NOT EXISTS idx_daily_data_code_date ON daily_data(code, date)')
            conn.execute(
                'CREATE INDEX IF NOT EXISTS idx_daily_data_date ON daily_data(date)')

            conn.commit()

    def get_stock_list(self, market: str = 'A') -> List[Dict[str, str]]:
        """
        获取股票列表

        Args:
            market: 市场类型 ('A' for A股, 'HK' for 港股)

        Returns:
            [{"code": "000001", "name": "平安银行"}, ...]
        """
        try:
            # 先从数据库获取
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT code, name FROM stock_info WHERE market = ? ORDER BY code',
                    (market,)
                )
                cached_stocks = cursor.fetchall()

                # 检查缓存是否过期
                cursor = conn.execute(
                    'SELECT MAX(updated_at) FROM stock_info WHERE market = ?',
                    (market,)
                )
                last_update = cursor.fetchone()[0]

                if last_update:
                    last_update_time = datetime.fromisoformat(last_update)
                    if datetime.now() - last_update_time < timedelta(days=self.cache_days):
                        logger.info(
                            f"从缓存获取{market}股票列表: {len(cached_stocks)}只")
                        return [{"code": code, "name": name} for code, name in cached_stocks]

            # 从网络获取最新数据
            logger.info(f"从网络获取{market}股票列表...")

            if market == 'A':
                stocks = self._fetch_a_stock_list()
            elif market == 'HK':
                stocks = self._fetch_hk_stock_list()
            else:
                raise DataSourceError(f"不支持的市场类型: {market}")

            # 更新数据库
            if stocks:
                self._update_stock_list(stocks, market)

            return [{"code": code, "name": name} for code, name in stocks]

        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            raise DataSourceError(f"获取股票列表失败: {str(e)}")

    def _fetch_a_stock_list(self) -> List[Tuple[str, str]]:
        """获取A股股票列表"""
        try:
            url = "http://82.push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': '1',
                'pz': '5000',  # 获取更多股票
                'po': '1',
                'np': '1',
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': '2',
                'invt': '2',
                'fid': 'f3',
                'fs': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23',  # A股主板、中小板、创业板
                'fields': 'f12,f14'  # 代码和名称
            }

            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'diff' in data['data']:
                    stocks = []
                    for item in data['data']['diff']:
                        code = item.get('f12')
                        name = item.get('f14')
                        if code and name:
                            stocks.append((code, name))

                    logger.info(f"获取A股列表成功: {len(stocks)}只")
                    return stocks
                else:
                    raise NetworkError("A股数据格式异常")
            else:
                raise NetworkError(f"获取A股列表失败，状态码: {response.status_code}")

        except requests.RequestException as e:
            raise NetworkError(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise DataSourceError(f"获取A股列表异常: {str(e)}")

    def _fetch_hk_stock_list(self) -> List[Tuple[str, str]]:
        """获取港股股票列表"""
        try:
            url = "http://82.push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': '1',
                'pz': '2000',
                'po': '1',
                'np': '1',
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': '2',
                'invt': '2',
                'fid': 'f3',
                'fs': 'm:128 t:3,m:128 t:4,m:128 t:1,m:128 t:2',  # 港股
                'fields': 'f12,f14'
            }

            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'diff' in data['data']:
                    stocks = []
                    for item in data['data']['diff']:
                        code = item.get('f12')
                        name = item.get('f14')
                        if code and name:
                            stocks.append((code, name))

                    logger.info(f"获取港股列表成功: {len(stocks)}只")
                    return stocks
                else:
                    raise NetworkError("港股数据格式异常")
            else:
                raise NetworkError(f"获取港股列表失败，状态码: {response.status_code}")

        except requests.RequestException as e:
            raise NetworkError(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise DataSourceError(f"获取港股列表异常: {str(e)}")

    def _update_stock_list(self, stocks: List[Tuple[str, str]], market: str):
        """更新股票列表到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 删除旧数据
                conn.execute(
                    'DELETE FROM stock_info WHERE market = ?', (market,))

                # 插入新数据
                conn.executemany(
                    'INSERT INTO stock_info (code, name, market, updated_at) VALUES (?, ?, ?, ?)',
                    [(code, name, market, datetime.now().isoformat())
                     for code, name in stocks]
                )

                conn.commit()
                logger.info(f"更新{market}股票列表到数据库: {len(stocks)}只")

        except Exception as e:
            logger.error(f"更新股票列表到数据库失败: {e}")

    def get_historical_data(self, code: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        获取历史数据

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            历史数据列表
        """
        try:
            # 验证股票代码
            if not validate_stock_code(code):
                raise DataSourceError(f"无效的股票代码: {code}")

            # 验证日期范围
            if start_date >= end_date:
                raise DataSourceError("开始日期必须早于结束日期")

            # 先从缓存获取
            cached_data = self._get_cached_data(code, start_date, end_date)

            # 检查是否有缺失数据
            missing_ranges = self._find_missing_dates(
                cached_data, start_date, end_date)

            # 获取缺失数据
            for missing_start, missing_end in missing_ranges:
                logger.info(f"获取{code}缺失数据: {missing_start} 到 {missing_end}")
                new_data = self._fetch_historical_data(
                    code, missing_start, missing_end)
                if new_data:
                    self._save_historical_data(new_data)
                    cached_data.extend(new_data)

            # 按日期排序
            cached_data.sort(key=lambda x: x.date)

            # 转换为字典格式
            result = []
            for data in cached_data:
                result.append({
                    "code": data.code,
                    "name": data.name,
                    "date": data.date.isoformat(),
                    "open_price": data.open_price,
                    "high_price": data.high_price,
                    "low_price": data.low_price,
                    "close_price": data.close_price,
                    "volume": data.volume,
                    "amount": data.amount,
                    "change_pct": data.change_pct
                })

            logger.info(f"获取{code}历史数据成功: {len(result)}条")
            return result

        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            raise DataSourceError(f"获取历史数据失败: {str(e)}")

    def _get_cached_data(self, code: str, start_date: date, end_date: date) -> List[StockData]:
        """从缓存获取数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT code, date, open_price, high_price, low_price, close_price, 
                           volume, amount, change_pct
                    FROM daily_data 
                    WHERE code = ? AND date BETWEEN ? AND ?
                    ORDER BY date
                ''', (code, start_date.isoformat(), end_date.isoformat()))

                data = []
                for row in cursor.fetchall():
                    stock_data = StockData(
                        code=row[0],
                        name="",  # 从数据库获取时不包含名称
                        date=datetime.strptime(row[1], '%Y-%m-%d').date(),
                        open_price=row[2],
                        close_price=row[5],
                        high_price=row[3],
                        low_price=row[4],
                        volume=row[6],
                        amount=row[7],
                        change_pct=row[8]
                    )
                    data.append(stock_data)

                return data

        except Exception as e:
            logger.error(f"从缓存获取数据失败: {e}")
            return []

    def _find_missing_dates(self, cached_data: List[StockData], start_date: date, end_date: date) -> List[Tuple[date, date]]:
        """查找缺失的日期范围"""
        if not cached_data:
            return [(start_date, end_date)]

        cached_dates = {data.date for data in cached_data}
        missing_ranges = []

        current_date = start_date
        while current_date <= end_date:
            if current_date not in cached_dates:
                # 找到缺失范围的开始
                range_start = current_date
                while current_date <= end_date and current_date not in cached_dates:
                    current_date += timedelta(days=1)
                range_end = current_date - timedelta(days=1)
                missing_ranges.append((range_start, range_end))
            else:
                current_date += timedelta(days=1)

        return missing_ranges

    def _fetch_historical_data(self, code: str, start_date: date, end_date: date) -> List[StockData]:
        """从网络获取历史数据"""
        try:
            # 判断市场
            if code.startswith('6'):
                secid = f"1.{code}"  # 上海
            else:
                secid = f"0.{code}"  # 深圳

            url = "http://82.push2.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': secid,
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': '101',  # 日K线
                'fqt': '1',    # 前复权
                'beg': start_date.strftime('%Y%m%d'),
                'end': end_date.strftime('%Y%m%d')
            }

            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data'] and 'klines' in data['data']:
                    klines = data['data']['klines']
                    stock_name = data['data'].get('name', code)

                    result = []
                    for kline in klines:
                        fields = kline.split(',')
                        if len(fields) >= 11:
                            trade_date = datetime.strptime(
                                fields[0], '%Y-%m-%d').date()

                            stock_data = StockData(
                                code=code,
                                name=stock_name,
                                date=trade_date,
                                open_price=float(fields[1]),
                                close_price=float(fields[2]),
                                high_price=float(fields[3]),
                                low_price=float(fields[4]),
                                volume=int(fields[5]),
                                amount=float(fields[6]),
                                change_pct=float(fields[8])
                            )
                            result.append(stock_data)

                    logger.info(f"获取{code}历史数据成功: {len(result)}条")
                    return result
                else:
                    raise NetworkError(f"未找到股票{code}的历史数据")
            else:
                raise NetworkError(f"获取历史数据失败，状态码: {response.status_code}")

        except requests.RequestException as e:
            raise NetworkError(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise DataSourceError(f"获取历史数据异常: {str(e)}")

    def _save_historical_data(self, data: List[StockData]):
        """保存历史数据到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for stock_data in data:
                    conn.execute('''
                        INSERT OR REPLACE INTO daily_data 
                        (code, date, open_price, high_price, low_price, close_price, volume, amount, change_pct)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stock_data.code,
                        stock_data.date.isoformat(),
                        stock_data.open_price,
                        stock_data.high_price,
                        stock_data.low_price,
                        stock_data.close_price,
                        stock_data.volume,
                        stock_data.amount,
                        stock_data.change_pct
                    ))

                conn.commit()
                logger.info(f"保存历史数据到数据库: {len(data)}条")

        except Exception as e:
            logger.error(f"保存历史数据到数据库失败: {e}")

    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据摘要"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 统计股票数量
                cursor = conn.execute(
                    'SELECT market, COUNT(*) FROM stock_info GROUP BY market')
                stock_counts = dict(cursor.fetchall())

                # 统计历史数据量
                cursor = conn.execute('SELECT COUNT(*) FROM daily_data')
                total_records = cursor.fetchone()[0]

                # 统计最新数据日期
                cursor = conn.execute('SELECT MAX(date) FROM daily_data')
                latest_date = cursor.fetchone()[0]

                return {
                    "stock_counts": stock_counts,
                    "total_records": total_records,
                    "latest_date": latest_date,
                    "cache_days": self.cache_days,
                    "database_path": self.db_path
                }

        except Exception as e:
            logger.error(f"获取数据摘要失败: {e}")
            return {"error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查数据库连接
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM stock_info')
                stock_count = cursor.fetchone()[0]

            # 检查网络连接
            test_response = self.session.get(
                "http://quote.eastmoney.com/", timeout=5)
            network_ok = test_response.status_code == 200

            return {
                "status": "healthy",
                "database_ok": True,
                "network_ok": network_ok,
                "stock_count": stock_count,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
