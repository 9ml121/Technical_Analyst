"""
股票数据获取器
支持A股和港股通H股实盘交易行情
"""
import akshare as ak
import tushare as ts
import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime
from typing import Dict, List, Optional, Union
import logging
from config import TUSHARE_TOKEN, SAMPLE_STOCKS

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        """初始化数据获取器"""
        self.setup_tushare()
        
    def setup_tushare(self):
        """设置Tushare"""
        if TUSHARE_TOKEN:
            ts.set_token(TUSHARE_TOKEN)
            self.ts_pro = ts.pro_api()
            logger.info("Tushare已配置")
        else:
            self.ts_pro = None
            logger.warning("未配置Tushare Token，部分功能可能不可用")
    
    def get_a_stock_realtime(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        获取A股实时行情
        
        Args:
            symbols: 股票代码列表，如['000001', '600000']
            
        Returns:
            包含实时行情的DataFrame
        """
        try:
            if symbols is None:
                # 获取所有A股实时行情（数据量大，谨慎使用）
                df = ak.stock_zh_a_spot_em()
            else:
                # 获取指定股票的实时行情
                data_list = []
                for symbol in symbols:
                    try:
                        # 使用akshare获取个股实时数据
                        stock_data = ak.stock_zh_a_spot_em()
                        stock_info = stock_data[stock_data['代码'] == symbol]
                        if not stock_info.empty:
                            data_list.append(stock_info.iloc[0])
                    except Exception as e:
                        logger.error(f"获取股票 {symbol} 数据失败: {e}")
                        continue
                
                if data_list:
                    df = pd.DataFrame(data_list)
                else:
                    df = pd.DataFrame()
            
            if not df.empty:
                df['更新时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"成功获取A股实时行情，共{len(df)}只股票")
            
            return df
            
        except Exception as e:
            logger.error(f"获取A股实时行情失败: {e}")
            return pd.DataFrame()
    
    def get_hk_stock_realtime(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        获取港股实时行情
        
        Args:
            symbols: 港股代码列表，如['00700', '00941']
            
        Returns:
            包含实时行情的DataFrame
        """
        try:
            if symbols is None:
                # 获取港股通成份股实时行情
                df = ak.stock_hk_ggt_components_em()
            else:
                # 获取指定港股的实时行情
                data_list = []
                for symbol in symbols:
                    try:
                        # 使用yfinance获取港股数据
                        ticker = f"{symbol}.HK"
                        stock = yf.Ticker(ticker)
                        info = stock.info
                        hist = stock.history(period="1d", interval="1m")
                        
                        if not hist.empty:
                            latest = hist.iloc[-1]
                            stock_data = {
                                '代码': symbol,
                                '名称': info.get('longName', ''),
                                '最新价': latest['Close'],
                                '开盘价': latest['Open'],
                                '最高价': latest['High'],
                                '最低价': latest['Low'],
                                '成交量': latest['Volume'],
                                '涨跌幅': ((latest['Close'] - info.get('previousClose', latest['Close'])) / 
                                         info.get('previousClose', latest['Close']) * 100) if info.get('previousClose') else 0
                            }
                            data_list.append(stock_data)
                    except Exception as e:
                        logger.error(f"获取港股 {symbol} 数据失败: {e}")
                        continue
                
                if data_list:
                    df = pd.DataFrame(data_list)
                else:
                    df = pd.DataFrame()
            
            if not df.empty:
                df['更新时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"成功获取港股实时行情，共{len(df)}只股票")
            
            return df
            
        except Exception as e:
            logger.error(f"获取港股实时行情失败: {e}")
            return pd.DataFrame()
    
    def get_hk_connect_realtime(self) -> pd.DataFrame:
        """
        获取港股通实时行情
        
        Returns:
            包含港股通实时行情的DataFrame
        """
        try:
            # 获取港股通成份股
            df = ak.stock_hk_ggt_components_em()
            
            if not df.empty:
                df['更新时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"成功获取港股通实时行情，共{len(df)}只股票")
            
            return df
            
        except Exception as e:
            logger.error(f"获取港股通实时行情失败: {e}")
            return pd.DataFrame()
    
    def get_market_overview(self) -> Dict:
        """
        获取市场概览
        
        Returns:
            包含市场概览信息的字典
        """
        overview = {}
        
        try:
            # A股市场概览
            a_stock_count = len(ak.stock_zh_a_spot_em())
            overview['A股'] = {
                '股票数量': a_stock_count,
                '更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"获取A股市场概览失败: {e}")
            overview['A股'] = {'错误': str(e)}
        
        try:
            # 港股通概览
            hk_connect = ak.stock_hk_ggt_components_em()
            overview['港股通'] = {
                '股票数量': len(hk_connect),
                '更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"获取港股通概览失败: {e}")
            overview['港股通'] = {'错误': str(e)}
        
        return overview
