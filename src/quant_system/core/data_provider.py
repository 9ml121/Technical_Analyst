"""
历史行情数据获取模块
基于现有的production_ready.py扩展，支持获取A股和港股通H股最近3年历史数据
"""
import os
import time
import json
import sqlite3
import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# 可选依赖处理
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas not available, some features may be limited")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not available, some features may be limited")

# 导入数据模型
try:
    from ..models.stock_data import StockData, StockDataValidator
    from ..utils.logger import get_logger
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    try:
        from quant_system.models.stock_data import StockData, StockDataValidator
        from quant_system.utils.logger import get_logger
    except ImportError:
        # 如果都失败，使用基础日志
        StockData = None
        StockDataValidator = None
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
    else:
        logger = get_logger()
else:
    logger = get_logger()


class HistoricalDataProvider:
    """历史数据提供者实现"""

    def __init__(self, db_path: str = './data/stock_data.db', cache_days: int = 1):
        """
        初始化历史数据提供者

        Args:
            db_path: 数据库路径
            cache_days: 缓存天数
        """
        self.db_path = db_path
        self.cache_days = cache_days

        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # 初始化数据库
        self._init_database()

        # 配置HTTP会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'http://quote.eastmoney.com/'
        })

        logger.info(f"历史数据提供者初始化完成，数据库: {db_path}")

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

    def get_stock_list(self, market: str = 'A') -> List[Tuple[str, str]]:
        """
        获取股票列表

        Args:
            market: 市场类型 ('A' for A股, 'HK' for 港股)

        Returns:
            [(股票代码, 股票名称), ...]
        """
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
                    logger.info(f"从缓存获取{market}股票列表: {len(cached_stocks)}只")
                    return cached_stocks

        # 从网络获取最新数据
        logger.info(f"从网络获取{market}股票列表...")

        if market == 'A':
            stocks = self._fetch_a_stock_list()
        elif market == 'HK':
            stocks = self._fetch_hk_stock_list()
        else:
            raise ValueError(f"不支持的市场类型: {market}")

        # 更新数据库
        if stocks:
            self._update_stock_list(stocks, market)

        return stocks

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

            logger.error(f"获取A股列表失败: HTTP {response.status_code}")
            return []

        except Exception as e:
            logger.error(f"获取A股列表异常: {e}")
            return []

    def _fetch_hk_stock_list(self) -> List[Tuple[str, str]]:
        """获取港股通股票列表"""
        try:
            # 获取港股通成份股
            url = "http://82.push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': '1',
                'pz': '1000',
                'po': '1',
                'np': '1',
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': '2',
                'invt': '2',
                'fid': 'f3',
                'fs': 'b:MK0144',  # 港股通
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

                    logger.info(f"获取港股通列表成功: {len(stocks)}只")
                    return stocks

            logger.error(f"获取港股通列表失败: HTTP {response.status_code}")
            return []

        except Exception as e:
            logger.error(f"获取港股通列表异常: {e}")
            return []

    def _update_stock_list(self, stocks: List[Tuple[str, str]], market: str):
        """更新股票列表到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            # 清除旧数据
            conn.execute('DELETE FROM stock_info WHERE market = ?', (market,))

            # 插入新数据
            for code, name in stocks:
                conn.execute(
                    'INSERT INTO stock_info (code, name, market) VALUES (?, ?, ?)',
                    (code, name, market)
                )

            conn.commit()
            logger.info(f"更新{market}股票列表到数据库: {len(stocks)}只")

    def get_historical_data(self, code: str, start_date: date, end_date: date) -> List[StockData]:
        """
        获取历史数据

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            历史数据列表
        """
        # 先从数据库获取
        cached_data = self._get_cached_data(code, start_date, end_date)

        # 检查是否需要补充数据
        missing_dates = self._find_missing_dates(
            cached_data, start_date, end_date)

        if missing_dates:
            logger.info(f"需要补充{code}的数据: {len(missing_dates)}个日期段")

            for start, end in missing_dates:
                new_data = self._fetch_historical_data(code, start, end)
                if new_data:
                    self._save_historical_data(new_data)
                    cached_data.extend(new_data)
                time.sleep(0.1)  # 避免请求过于频繁

        # 按日期排序并转换为StockData对象
        cached_data.sort(key=lambda x: x.date)
        return cached_data

    def _get_cached_data(self, code: str, start_date: date, end_date: date) -> List[StockData]:
        """从数据库获取缓存数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT code, date, open_price, high_price, low_price, close_price,
                       volume, amount, change_pct
                FROM daily_data
                WHERE code = ? AND date >= ? AND date <= ?
                ORDER BY date
            ''', (code, start_date.isoformat(), end_date.isoformat()))

            data = []
            for row in cursor.fetchall():
                # 获取股票名称
                name_cursor = conn.execute(
                    'SELECT name FROM stock_info WHERE code = ?', (code,))
                name_result = name_cursor.fetchone()
                name = name_result[0] if name_result else code

                data.append(StockData(
                    code=row[0],
                    name=name,
                    date=datetime.fromisoformat(row[1]).date(),
                    open_price=row[2] or 0,
                    high_price=row[3] or 0,
                    low_price=row[4] or 0,
                    close_price=row[5] or 0,
                    volume=row[6] or 0,
                    amount=row[7] or 0,
                    change_pct=row[8] or 0
                ))

            return data

    def _find_missing_dates(self, cached_data: List[StockData], start_date: date, end_date: date) -> List[Tuple[date, date]]:
        """找出缺失的日期段"""
        if not cached_data:
            return [(start_date, end_date)]

        cached_dates = set(item.date for item in cached_data)
        missing_ranges = []

        current_date = start_date
        range_start = None

        while current_date <= end_date:
            if current_date not in cached_dates:
                if range_start is None:
                    range_start = current_date
            else:
                if range_start is not None:
                    missing_ranges.append(
                        (range_start, current_date - timedelta(days=1)))
                    range_start = None

            current_date += timedelta(days=1)

        # 处理最后一个缺失段
        if range_start is not None:
            missing_ranges.append((range_start, end_date))

        return missing_ranges

    def _fetch_historical_data(self, code: str, start_date: date, end_date: date) -> List[StockData]:
        """从网络获取历史数据"""
        try:
            # 判断是A股还是港股
            if code.startswith('6'):
                secid = f"1.{code}"  # 上海
            elif len(code) == 6 and code.isdigit():
                secid = f"0.{code}"  # 深圳
            else:
                secid = f"116.{code}"  # 港股

            url = "http://82.push2his.eastmoney.com/api/qt/stock/kline/get"
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

                    historical_data = []
                    for kline in klines:
                        fields = kline.split(',')
                        if len(fields) >= 11:
                            trade_date = datetime.strptime(
                                fields[0], '%Y-%m-%d').date()

                            historical_data.append(StockData(
                                code=code,
                                name=stock_name,
                                date=trade_date,
                                open_price=float(fields[1]),
                                close_price=float(fields[2]),
                                high_price=float(fields[3]),
                                low_price=float(fields[4]),
                                volume=int(fields[5]),
                                amount=float(fields[6]),
                                pct_change=float(fields[8])
                            ))

                    logger.info(f"获取{code}历史数据成功: {len(historical_data)}条")
                    return historical_data

            logger.warning(f"获取{code}历史数据失败: HTTP {response.status_code}")
            return []

        except Exception as e:
            logger.error(f"获取{code}历史数据异常: {e}")
            return []

    def _save_historical_data(self, data: List[StockData]):
        """保存历史数据到数据库"""
        if not data:
            return

        with sqlite3.connect(self.db_path) as conn:
            for item in data:
                conn.execute('''
                    INSERT OR REPLACE INTO daily_data
                    (code, date, open_price, high_price, low_price, close_price,
                     volume, amount, change_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.code, item.date.isoformat(), item.open_price,
                    item.high_price, item.low_price, item.close_price,
                    item.volume, item.amount, item.change_pct
                ))

            conn.commit()

    def get_index_data(self, index_code: str, start_date: date, end_date: date) -> List[StockData]:
        """获取指数数据"""
        # 指数代码映射
        index_mapping = {
            '000300': '1.000300',  # 沪深300
            '000001': '1.000001',  # 上证指数
            '399001': '0.399001',  # 深证成指
            '399006': '0.399006',  # 创业板指
        }

        secid = index_mapping.get(index_code, f"1.{index_code}")
        return self._fetch_historical_data(index_code, start_date, end_date)

    def get_data_summary(self) -> Dict:
        """获取数据概览"""
        with sqlite3.connect(self.db_path) as conn:
            # 统计股票数量
            cursor = conn.execute(
                'SELECT market, COUNT(*) FROM stock_info GROUP BY market')
            stock_counts = dict(cursor.fetchall())

            # 统计数据日期范围
            cursor = conn.execute(
                'SELECT MIN(date), MAX(date), COUNT(*) FROM daily_data')
            date_info = cursor.fetchone()

            return {
                'stock_counts': stock_counts,
                'date_range': {
                    'start': date_info[0],
                    'end': date_info[1],
                    'total_records': date_info[2]
                }
            }


if __name__ == "__main__":
    # 测试历史数据提供者
    provider = HistoricalDataProvider()

    print("测试历史数据提供者...")

    # 测试获取股票列表
    a_stocks = provider.get_stock_list('A')
    print(f"A股数量: {len(a_stocks)}")

    if a_stocks:
        # 测试获取历史数据
        test_code = a_stocks[0][0]
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        print(f"测试获取{test_code}最近30天数据...")
        historical_data = provider.get_historical_data(
            test_code, start_date, end_date)
        print(f"获取数据条数: {len(historical_data)}")

        if historical_data:
            print("样例数据:")
            for i, data in enumerate(historical_data[:3]):
                print(f"  {data.date}: {data.close_price}")

    # 显示数据概览
    summary = provider.get_data_summary()
    print(f"数据概览: {summary}")
