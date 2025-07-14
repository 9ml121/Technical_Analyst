"""
市场数据处理器

提供数据清洗、转换、聚合等处理功能，包含性能优化
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Union
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from functools import partial
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from quant_system.utils.performance import performance_timer, performance_context
    from quant_system.utils.cache import cache_result, cache_manager
    HAS_PERFORMANCE_TOOLS = True
except ImportError:
    HAS_PERFORMANCE_TOOLS = False
    # 提供空的装饰器

    def performance_timer(func):
        return func

    def cache_result(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)

# 可选依赖处理
try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logger.warning("pandas未安装，部分功能受限")


class MarketDataProcessor:
    """市场数据处理器"""

    def __init__(self, enable_parallel: bool = True, max_workers: Optional[int] = None):
        """
        初始化数据处理器

        Args:
            enable_parallel: 是否启用并行处理
            max_workers: 最大工作线程数
        """
        self.logger = logger
        self.enable_parallel = enable_parallel
        self.max_workers = max_workers or min(32, (mp.cpu_count() or 1) + 4)

        # 获取缓存实例
        if HAS_PERFORMANCE_TOOLS:
            self.cache = cache_manager.get_cache('stock_data')
        else:
            self.cache = None

    @performance_timer
    def clean_stock_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        清洗股票数据

        Args:
            raw_data: 原始股票数据

        Returns:
            清洗后的数据
        """
        if not raw_data:
            return []

        # 如果数据量大且启用并行处理，使用多线程
        if len(raw_data) > 1000 and self.enable_parallel:
            return self._clean_stock_data_parallel(raw_data)
        else:
            return self._clean_stock_data_sequential(raw_data)

    def _clean_stock_data_sequential(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """顺序清洗股票数据"""
        cleaned_data = []

        for item in raw_data:
            cleaned_item = self._clean_single_stock_item(item)
            if cleaned_item:
                cleaned_data.append(cleaned_item)

        return cleaned_data

    def _clean_stock_data_parallel(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """并行清洗股票数据"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 使用线程池并行处理
            results = list(executor.map(
                self._clean_single_stock_item, raw_data))

        # 过滤掉None结果
        return [item for item in results if item is not None]

    def _clean_single_stock_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """清洗单个股票数据项"""
        try:
            # 数据验证和清洗
            cleaned_item = {}

            # 股票代码处理
            code = str(item.get('code', '')).strip()
            if not code or len(code) != 6:
                return None
            cleaned_item['code'] = code

            # 股票名称处理
            name = str(item.get('name', '')).strip()
            if not name:
                return None
            cleaned_item['name'] = name

            # 价格数据处理
            price_fields = ['price', 'open',
                            'high', 'low', 'close', 'pre_close']
            for field in price_fields:
                value = item.get(field, 0)
                try:
                    cleaned_value = float(value) if value is not None else 0.0
                    if cleaned_value < 0:
                        cleaned_value = 0.0
                    cleaned_item[field] = round(cleaned_value, 2)
                except (ValueError, TypeError):
                    cleaned_item[field] = 0.0

            # 成交量和成交额处理
            volume = item.get('volume', 0)
            try:
                cleaned_item['volume'] = int(
                    volume) if volume is not None else 0
                if cleaned_item['volume'] < 0:
                    cleaned_item['volume'] = 0
            except (ValueError, TypeError):
                cleaned_item['volume'] = 0

            amount = item.get('amount', 0)
            try:
                cleaned_item['amount'] = float(
                    amount) if amount is not None else 0.0
                if cleaned_item['amount'] < 0:
                    cleaned_item['amount'] = 0.0
            except (ValueError, TypeError):
                cleaned_item['amount'] = 0.0

            # 涨跌幅处理
            change = item.get('change', 0)
            pct_change = item.get('pct_change', 0)

            try:
                cleaned_item['change'] = float(
                    change) if change is not None else 0.0
                cleaned_item['pct_change'] = float(
                    pct_change) if pct_change is not None else 0.0
            except (ValueError, TypeError):
                cleaned_item['change'] = 0.0
                cleaned_item['pct_change'] = 0.0

            # 时间戳处理
            update_time = item.get(
                'update_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            cleaned_item['update_time'] = update_time

            # 其他字段
            for field in ['turnover_rate', 'pe_ratio', 'pb_ratio', 'market_cap']:
                value = item.get(field, 0)
                try:
                    cleaned_item[field] = float(
                        value) if value is not None else 0.0
                except (ValueError, TypeError):
                    cleaned_item[field] = 0.0

            return cleaned_item

        except Exception as e:
            self.logger.warning(f"清洗数据项失败: {e}, 数据: {item}")
            return None

    @performance_timer
    @cache_result(ttl=300)  # 缓存5分钟
    def filter_stocks(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据条件筛选股票

        Args:
            data: 股票数据
            filters: 筛选条件

        Returns:
            筛选后的数据
        """
        if not data or not filters:
            return data

        # 如果数据量大且启用并行处理，使用多线程
        if len(data) > 500 and self.enable_parallel:
            return self._filter_stocks_parallel(data, filters)
        else:
            return self._filter_stocks_sequential(data, filters)

    def _filter_stocks_sequential(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """顺序筛选股票"""
        filtered_data = []

        for stock in data:
            if self._stock_meets_filters(stock, filters):
                filtered_data.append(stock)

        return filtered_data

    def _filter_stocks_parallel(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """并行筛选股票"""
        filter_func = partial(self._stock_meets_filters, filters=filters)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 并行检查每只股票是否满足条件
            results = list(executor.map(filter_func, data))

        # 返回满足条件的股票
        return [stock for stock, meets_filter in zip(data, results) if meets_filter]

    def _stock_meets_filters(self, stock: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """检查股票是否满足筛选条件"""
        try:
            # 价格筛选
            if 'min_price' in filters:
                if stock.get('price', 0) < filters['min_price']:
                    return False

            if 'max_price' in filters:
                if stock.get('price', 0) > filters['max_price']:
                    return False

            # 涨跌幅筛选
            if 'min_pct_change' in filters:
                if stock.get('pct_change', 0) < filters['min_pct_change']:
                    return False

            if 'max_pct_change' in filters:
                if stock.get('pct_change', 0) > filters['max_pct_change']:
                    return False

            # 成交量筛选
            if 'min_volume' in filters:
                if stock.get('volume', 0) < filters['min_volume']:
                    return False

            # 市值筛选
            if 'min_market_cap' in filters:
                if stock.get('market_cap', 0) < filters['min_market_cap']:
                    return False

            if 'max_market_cap' in filters:
                if stock.get('market_cap', 0) > filters['max_market_cap']:
                    return False

            # 排除特定股票
            if 'exclude_codes' in filters:
                if stock.get('code') in filters['exclude_codes']:
                    return False

            # 包含特定股票
            if 'include_codes' in filters:
                if stock.get('code') not in filters['include_codes']:
                    return False

            return True

        except Exception as e:
            self.logger.warning(
                f"筛选股票失败: {e}, 股票: {stock.get('code', 'unknown')}")
            return False

    @performance_timer
    def sort_stocks(self, data: List[Dict[str, Any]], sort_by: str = 'pct_change',
                    ascending: bool = False) -> List[Dict[str, Any]]:
        """
        对股票数据排序

        Args:
            data: 股票数据
            sort_by: 排序字段
            ascending: 是否升序

        Returns:
            排序后的数据
        """
        if not data:
            return data

        try:
            # 对于大数据集，使用numpy排序可能更快
            if HAS_PANDAS and len(data) > 1000:
                return self._sort_stocks_with_pandas(data, sort_by, ascending)
            else:
                return self._sort_stocks_native(data, sort_by, ascending)

        except Exception as e:
            self.logger.error(f"股票排序失败: {e}")
            return data

    def _sort_stocks_native(self, data: List[Dict[str, Any]], sort_by: str, ascending: bool) -> List[Dict[str, Any]]:
        """使用原生Python排序"""
        sorted_data = sorted(
            data,
            key=lambda x: x.get(sort_by, 0),
            reverse=not ascending
        )

        self.logger.info(f"股票排序完成，按{sort_by}{'升序' if ascending else '降序'}排列")
        return sorted_data

    def _sort_stocks_with_pandas(self, data: List[Dict[str, Any]], sort_by: str, ascending: bool) -> List[Dict[str, Any]]:
        """使用pandas排序（适用于大数据集）"""
        df = pd.DataFrame(data)
        sorted_df = df.sort_values(by=sort_by, ascending=ascending)

        self.logger.info(
            f"股票排序完成（pandas），按{sort_by}{'升序' if ascending else '降序'}排列")
        return sorted_df.to_dict('records')

    def calculate_technical_indicators(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        计算技术指标

        Args:
            data: 历史数据

        Returns:
            包含技术指标的数据
        """
        if not data:
            return data

        try:
            # 按日期排序
            sorted_data = sorted(data, key=lambda x: x.get('date', ''))

            # 计算移动平均线
            for i, item in enumerate(sorted_data):
                # MA5
                if i >= 4:
                    ma5_sum = sum(sorted_data[j].get('close', 0)
                                  for j in range(i-4, i+1))
                    item['ma5'] = round(ma5_sum / 5, 2)
                else:
                    item['ma5'] = item.get('close', 0)

                # MA10
                if i >= 9:
                    ma10_sum = sum(sorted_data[j].get(
                        'close', 0) for j in range(i-9, i+1))
                    item['ma10'] = round(ma10_sum / 10, 2)
                else:
                    item['ma10'] = item.get('close', 0)

                # MA20
                if i >= 19:
                    ma20_sum = sum(sorted_data[j].get('close', 0)
                                   for j in range(i-19, i+1))
                    item['ma20'] = round(ma20_sum / 20, 2)
                else:
                    item['ma20'] = item.get('close', 0)

                # 成交量移动平均
                if i >= 4:
                    vol_ma5_sum = sum(sorted_data[j].get(
                        'volume', 0) for j in range(i-4, i+1))
                    item['vol_ma5'] = int(vol_ma5_sum / 5)
                else:
                    item['vol_ma5'] = item.get('volume', 0)

            self.logger.info(f"技术指标计算完成，共{len(sorted_data)}条数据")
            return sorted_data

        except Exception as e:
            self.logger.error(f"技术指标计算失败: {e}")
            return data

    def aggregate_market_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        聚合市场数据统计

        Args:
            data: 股票数据

        Returns:
            市场统计数据
        """
        if not data:
            return {}

        try:
            total_stocks = len(data)

            # 涨跌统计
            rising_stocks = len(
                [s for s in data if s.get('pct_change', 0) > 0])
            falling_stocks = len(
                [s for s in data if s.get('pct_change', 0) < 0])
            flat_stocks = total_stocks - rising_stocks - falling_stocks

            # 价格统计
            prices = [s.get('price', 0) for s in data if s.get('price', 0) > 0]
            avg_price = sum(prices) / len(prices) if prices else 0

            # 涨跌幅统计
            pct_changes = [s.get('pct_change', 0) for s in data]
            avg_pct_change = sum(pct_changes) / \
                len(pct_changes) if pct_changes else 0

            # 成交量统计
            volumes = [s.get('volume', 0) for s in data]
            total_volume = sum(volumes)

            # 成交额统计
            amounts = [s.get('amount', 0) for s in data]
            total_amount = sum(amounts)

            market_stats = {
                'total_stocks': total_stocks,
                'rising_stocks': rising_stocks,
                'falling_stocks': falling_stocks,
                'flat_stocks': flat_stocks,
                'rising_ratio': round(rising_stocks / total_stocks, 4) if total_stocks > 0 else 0,
                'avg_price': round(avg_price, 2),
                'avg_pct_change': round(avg_pct_change, 4),
                'total_volume': total_volume,
                'total_amount': round(total_amount, 2),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            self.logger.info(f"市场数据聚合完成: {total_stocks}只股票")
            return market_stats

        except Exception as e:
            self.logger.error(f"市场数据聚合失败: {e}")
            return {}

    def convert_to_standard_format(self, data: List[Dict[str, Any]],
                                   source: str = 'unknown') -> List[Dict[str, Any]]:
        """
        转换为标准格式

        Args:
            data: 原始数据
            source: 数据源

        Returns:
            标准格式数据
        """
        if not data:
            return []

        standard_data = []

        for item in data:
            try:
                standard_item = {
                    'code': str(item.get('code', item.get('symbol', ''))).strip(),
                    'name': str(item.get('name', '')).strip(),
                    'price': float(item.get('price', item.get('close', 0))),
                    'open': float(item.get('open', 0)),
                    'high': float(item.get('high', 0)),
                    'low': float(item.get('low', 0)),
                    'close': float(item.get('close', item.get('price', 0))),
                    'pre_close': float(item.get('pre_close', 0)),
                    'change': float(item.get('change', 0)),
                    'pct_change': float(item.get('pct_change', item.get('pct_chg', 0))),
                    'volume': int(item.get('volume', item.get('vol', 0))),
                    'amount': float(item.get('amount', 0)),
                    'turnover_rate': float(item.get('turnover_rate', 0)),
                    'pe_ratio': float(item.get('pe_ratio', 0)),
                    'pb_ratio': float(item.get('pb_ratio', 0)),
                    'market_cap': float(item.get('market_cap', 0)),
                    'source': source,
                    'update_time': item.get('update_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                }

                # 数据验证
                if standard_item['code'] and standard_item['name']:
                    standard_data.append(standard_item)

            except Exception as e:
                self.logger.warning(f"格式转换失败: {e}, 数据: {item}")
                continue

        self.logger.info(f"格式转换完成: {len(data)} -> {len(standard_data)}")
        return standard_data
