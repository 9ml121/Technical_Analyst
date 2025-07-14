"""
东方财富API数据获取器

提供A股实时行情数据获取功能
"""
import requests
import json
import time
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class EastMoneyAPI:
    """东方财富API数据获取器"""
    
    def __init__(self):
        """初始化API客户端"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "http://82.push2.eastmoney.com/api/qt"
    
    def get_a_stock_realtime(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取A股实时行情
        
        Args:
            limit: 返回股票数量限制
            
        Returns:
            股票行情数据列表
        """
        try:
            url = f"{self.base_url}/clist/get"
            params = {
                'pn': '1',
                'pz': str(limit),
                'po': '1',
                'np': '1',
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': '2',
                'invt': '2',
                'fid': 'f3',
                'fs': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23',
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and 'diff' in data['data']:
                    stocks = data['data']['diff']
                    
                    result = []
                    for stock in stocks:
                        stock_data = {
                            'code': stock.get('f12', ''),
                            'name': stock.get('f14', ''),
                            'price': stock.get('f2', 0) / 100 if stock.get('f2') else 0,
                            'change': stock.get('f4', 0) / 100 if stock.get('f4') else 0,
                            'pct_change': stock.get('f3', 0) / 100 if stock.get('f3') else 0,
                            'volume': stock.get('f5', 0),
                            'amount': stock.get('f6', 0),
                            'open': stock.get('f17', 0) / 100 if stock.get('f17') else 0,
                            'high': stock.get('f15', 0) / 100 if stock.get('f15') else 0,
                            'low': stock.get('f16', 0) / 100 if stock.get('f16') else 0,
                            'pre_close': stock.get('f18', 0) / 100 if stock.get('f18') else 0,
                            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        result.append(stock_data)
                    
                    logger.info(f"成功获取A股实时行情，共{len(result)}只股票")
                    return result
                else:
                    logger.error("数据格式异常")
                    return []
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"获取A股实时行情失败: {e}")
            return []
    
    def get_stock_detail(self, code: str) -> Optional[Dict[str, Any]]:
        """
        获取单只股票详细信息
        
        Args:
            code: 股票代码
            
        Returns:
            股票详细信息
        """
        try:
            # 判断市场
            if code.startswith('6'):
                secid = f"1.{code}"  # 上海
            else:
                secid = f"0.{code}"  # 深圳
            
            url = f"{self.base_url}/stock/get"
            params = {
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'invt': '2',
                'fltt': '2',
                'secid': secid,
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23,f24,f25'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and data['data']:
                    stock = data['data']
                    
                    result = {
                        'code': stock.get('f12', ''),
                        'name': stock.get('f14', ''),
                        'price': stock.get('f2', 0) / 100 if stock.get('f2') else 0,
                        'change': stock.get('f4', 0) / 100 if stock.get('f4') else 0,
                        'pct_change': stock.get('f3', 0) / 100 if stock.get('f3') else 0,
                        'volume': stock.get('f5', 0),
                        'amount': stock.get('f6', 0),
                        'open': stock.get('f17', 0) / 100 if stock.get('f17') else 0,
                        'high': stock.get('f15', 0) / 100 if stock.get('f15') else 0,
                        'low': stock.get('f16', 0) / 100 if stock.get('f16') else 0,
                        'pre_close': stock.get('f18', 0) / 100 if stock.get('f18') else 0,
                        'turnover_rate': stock.get('f8', 0) / 100 if stock.get('f8') else 0,
                        'pe_ratio': stock.get('f9', 0) / 100 if stock.get('f9') else 0,
                        'pb_ratio': stock.get('f23', 0) / 100 if stock.get('f23') else 0,
                        'market_cap': stock.get('f20', 0),
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    logger.info(f"成功获取股票{code}详细信息")
                    return result
                else:
                    logger.error(f"未找到股票{code}的数据")
                    return None
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取股票{code}详细信息失败: {e}")
            return None
    
    def get_historical_data(self, code: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        获取历史K线数据
        
        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            历史数据列表
        """
        try:
            # 判断市场
            if code.startswith('6'):
                secid = f"1.{code}"  # 上海
            else:
                secid = f"0.{code}"  # 深圳
            
            url = f"{self.base_url}/stock/kline/get"
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
                            trade_date = datetime.strptime(fields[0], '%Y-%m-%d').date()
                            
                            kline_data = {
                                'code': code,
                                'name': stock_name,
                                'date': trade_date.strftime('%Y-%m-%d'),
                                'open': float(fields[1]),
                                'close': float(fields[2]),
                                'high': float(fields[3]),
                                'low': float(fields[4]),
                                'volume': int(fields[5]),
                                'amount': float(fields[6]),
                                'pct_change': float(fields[8])
                            }
                            result.append(kline_data)
                    
                    logger.info(f"获取{code}历史数据成功: {len(result)}条")
                    return result
                else:
                    logger.error(f"未找到股票{code}的历史数据")
                    return []
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"获取股票{code}历史数据失败: {e}")
            return []
    
    def get_market_status(self) -> Dict[str, Any]:
        """
        获取市场状态信息
        
        Returns:
            市场状态信息
        """
        try:
            # 获取市场概览数据
            stocks = self.get_a_stock_realtime(limit=1)
            
            if stocks:
                current_time = datetime.now()
                
                # 简单判断交易时间
                is_trading_time = (
                    current_time.weekday() < 5 and  # 周一到周五
                    ((9 <= current_time.hour < 11) or (13 <= current_time.hour < 15))  # 交易时间段
                )
                
                return {
                    'market': 'A股',
                    'status': '交易中' if is_trading_time else '休市',
                    'update_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'data_available': True
                }
            else:
                return {
                    'market': 'A股',
                    'status': '数据获取失败',
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'data_available': False
                }
                
        except Exception as e:
            logger.error(f"获取市场状态失败: {e}")
            return {
                'market': 'A股',
                'status': '未知',
                'error': str(e),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_available': False
            }
