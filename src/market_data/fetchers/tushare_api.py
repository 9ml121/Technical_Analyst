"""
Tushare API数据获取器

提供专业的股票数据获取功能
"""
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# 可选依赖处理
try:
    import tushare as ts
    HAS_TUSHARE = True
except ImportError:
    HAS_TUSHARE = False
    logger.warning("Tushare未安装，相关功能不可用")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logger.warning("pandas未安装，部分功能受限")

class TushareAPI:
    """Tushare API数据获取器"""
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化Tushare API
        
        Args:
            token: Tushare API token
        """
        self.token = token or os.getenv('TUSHARE_TOKEN')
        self.pro = None
        
        if not HAS_TUSHARE:
            logger.error("Tushare未安装，无法使用该数据源")
            return
        
        if self.token:
            try:
                ts.set_token(self.token)
                self.pro = ts.pro_api()
                logger.info("Tushare API初始化成功")
            except Exception as e:
                logger.error(f"Tushare API初始化失败: {e}")
        else:
            logger.warning("未提供Tushare token，部分功能不可用")
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        return HAS_TUSHARE and self.pro is not None
    
    def get_stock_basic(self) -> List[Dict[str, Any]]:
        """
        获取股票基本信息
        
        Returns:
            股票基本信息列表
        """
        if not self.is_available():
            logger.error("Tushare API不可用")
            return []
        
        try:
            df = self.pro.stock_basic(exchange='', list_status='L')
            
            if HAS_PANDAS and not df.empty:
                result = []
                for _, row in df.iterrows():
                    stock_info = {
                        'ts_code': row['ts_code'],
                        'symbol': row['symbol'],
                        'name': row['name'],
                        'area': row['area'],
                        'industry': row['industry'],
                        'market': row['market'],
                        'list_date': row['list_date']
                    }
                    result.append(stock_info)
                
                logger.info(f"获取股票基本信息成功，共{len(result)}只股票")
                return result
            else:
                logger.error("获取股票基本信息失败")
                return []
                
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            return []
    
    def get_daily_data(self, ts_code: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取日线数据
        
        Args:
            ts_code: 股票代码 (如: 000001.SZ)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            日线数据列表
        """
        if not self.is_available():
            logger.error("Tushare API不可用")
            return []
        
        try:
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            if HAS_PANDAS and not df.empty:
                result = []
                for _, row in df.iterrows():
                    daily_data = {
                        'ts_code': row['ts_code'],
                        'trade_date': row['trade_date'],
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'pre_close': row['pre_close'],
                        'change': row['change'],
                        'pct_chg': row['pct_chg'],
                        'vol': row['vol'],
                        'amount': row['amount']
                    }
                    result.append(daily_data)
                
                logger.info(f"获取{ts_code}日线数据成功，共{len(result)}条")
                return result
            else:
                logger.error(f"获取{ts_code}日线数据失败")
                return []
                
        except Exception as e:
            logger.error(f"获取{ts_code}日线数据失败: {e}")
            return []
    
    def get_realtime_quotes(self, ts_codes: List[str]) -> List[Dict[str, Any]]:
        """
        获取实时行情数据
        
        Args:
            ts_codes: 股票代码列表
            
        Returns:
            实时行情数据列表
        """
        if not self.is_available():
            logger.error("Tushare API不可用")
            return []
        
        try:
            # Tushare的实时数据需要高级权限，这里提供基础实现
            result = []
            
            for ts_code in ts_codes:
                # 获取最新的日线数据作为近似实时数据
                today = datetime.now().strftime('%Y%m%d')
                df = self.pro.daily(ts_code=ts_code, start_date=today, end_date=today)
                
                if HAS_PANDAS and not df.empty:
                    row = df.iloc[0]
                    quote_data = {
                        'ts_code': row['ts_code'],
                        'trade_date': row['trade_date'],
                        'price': row['close'],
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'pre_close': row['pre_close'],
                        'change': row['change'],
                        'pct_change': row['pct_chg'],
                        'volume': row['vol'],
                        'amount': row['amount'],
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    result.append(quote_data)
            
            logger.info(f"获取实时行情成功，共{len(result)}只股票")
            return result
            
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return []
    
    def get_trade_cal(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取交易日历
        
        Args:
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            交易日历列表
        """
        if not self.is_available():
            logger.error("Tushare API不可用")
            return []
        
        try:
            df = self.pro.trade_cal(start_date=start_date, end_date=end_date)
            
            if HAS_PANDAS and not df.empty:
                result = []
                for _, row in df.iterrows():
                    cal_data = {
                        'cal_date': row['cal_date'],
                        'is_open': row['is_open'],
                        'pretrade_date': row.get('pretrade_date', '')
                    }
                    result.append(cal_data)
                
                logger.info(f"获取交易日历成功，共{len(result)}条记录")
                return result
            else:
                logger.error("获取交易日历失败")
                return []
                
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            return []
    
    def get_stock_company(self, ts_code: str) -> Optional[Dict[str, Any]]:
        """
        获取上市公司基本信息
        
        Args:
            ts_code: 股票代码
            
        Returns:
            公司基本信息
        """
        if not self.is_available():
            logger.error("Tushare API不可用")
            return None
        
        try:
            df = self.pro.stock_company(ts_code=ts_code)
            
            if HAS_PANDAS and not df.empty:
                row = df.iloc[0]
                company_info = {
                    'ts_code': row['ts_code'],
                    'chairman': row.get('chairman', ''),
                    'manager': row.get('manager', ''),
                    'secretary': row.get('secretary', ''),
                    'reg_capital': row.get('reg_capital', 0),
                    'setup_date': row.get('setup_date', ''),
                    'province': row.get('province', ''),
                    'city': row.get('city', ''),
                    'introduction': row.get('introduction', ''),
                    'website': row.get('website', ''),
                    'email': row.get('email', ''),
                    'office': row.get('office', ''),
                    'employees': row.get('employees', 0),
                    'main_business': row.get('main_business', ''),
                    'business_scope': row.get('business_scope', '')
                }
                
                logger.info(f"获取{ts_code}公司信息成功")
                return company_info
            else:
                logger.error(f"获取{ts_code}公司信息失败")
                return None
                
        except Exception as e:
            logger.error(f"获取{ts_code}公司信息失败: {e}")
            return None
