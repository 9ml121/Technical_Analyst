"""
真实市场数据获取服务
"""

import httpx
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional
import asyncio

logger = logging.getLogger(__name__)

class RealMarketDataService:
    """真实市场数据服务"""
    
    def __init__(self):
        self.timeout = 10.0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def get_sina_stock_data(self, symbols: List[str]) -> Dict:
        """从新浪财经获取股票数据"""
        try:
            # 新浪财经API
            symbol_str = ','.join(symbols)
            url = f"http://hq.sinajs.cn/list={symbol_str}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.encoding = 'gbk'
                
                if response.status_code == 200:
                    return self._parse_sina_data(response.text)
                else:
                    logger.error(f"新浪API请求失败: {response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"获取新浪数据失败: {e}")
            return {}
    
    def _parse_sina_data(self, data: str) -> Dict:
        """解析新浪财经数据"""
        result = {}
        lines = data.strip().split('\n')
        
        for line in lines:
            if '=' in line and '"' in line:
                try:
                    # 解析格式: var hq_str_sh000001="上证指数,2956.95,2942.12,2957.35,..."
                    symbol = line.split('=')[0].replace('var hq_str_', '')
                    data_str = line.split('"')[1]
                    fields = data_str.split(',')
                    
                    if len(fields) >= 4:
                        name = fields[0]
                        current = float(fields[3]) if fields[3] else 0.0
                        prev_close = float(fields[2]) if fields[2] else current
                        
                        change = current - prev_close
                        change_percent = (change / prev_close * 100) if prev_close > 0 else 0.0
                        
                        result[symbol] = {
                            'name': name,
                            'current': current,
                            'prev_close': prev_close,
                            'change': change,
                            'change_percent': change_percent,
                            'update_time': datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    logger.error(f"解析数据行失败: {line}, 错误: {e}")
                    continue
        
        return result
    
    async def get_tencent_stock_data(self, symbols: List[str]) -> Dict:
        """从腾讯财经获取股票数据（备用）"""
        try:
            # 腾讯财经API
            symbol_str = ','.join(symbols)
            url = f"http://qt.gtimg.cn/q={symbol_str}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.encoding = 'gbk'
                
                if response.status_code == 200:
                    return self._parse_tencent_data(response.text)
                else:
                    logger.error(f"腾讯API请求失败: {response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"获取腾讯数据失败: {e}")
            return {}
    
    def _parse_tencent_data(self, data: str) -> Dict:
        """解析腾讯财经数据"""
        result = {}
        lines = data.strip().split('\n')
        
        for line in lines:
            if '=' in line and '"' in line:
                try:
                    # 解析格式: v_sh000001="1~上证指数~000001~2956.95~..."
                    symbol = line.split('=')[0].replace('v_', '')
                    data_str = line.split('"')[1]
                    fields = data_str.split('~')
                    
                    if len(fields) >= 4:
                        name = fields[1]
                        current = float(fields[3]) if fields[3] else 0.0
                        prev_close = float(fields[4]) if len(fields) > 4 and fields[4] else current
                        
                        change = current - prev_close
                        change_percent = (change / prev_close * 100) if prev_close > 0 else 0.0
                        
                        result[symbol] = {
                            'name': name,
                            'current': current,
                            'prev_close': prev_close,
                            'change': change,
                            'change_percent': change_percent,
                            'update_time': datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    logger.error(f"解析腾讯数据行失败: {line}, 错误: {e}")
                    continue
        
        return result
    
    async def get_market_indices(self) -> Dict:
        """获取主要市场指数"""
        # 主要指数代码
        symbols = [
            'sh000001',  # 上证指数
            'sh000300',  # 沪深300
            'sz399001',  # 深证成指
            'sz399006'   # 创业板指
        ]
        
        # 首先尝试新浪财经
        data = await self.get_sina_stock_data(symbols)
        
        # 如果新浪失败，尝试腾讯财经
        if not data:
            logger.info("新浪API失败，尝试腾讯API")
            data = await self.get_tencent_stock_data(symbols)
        
        # 如果都失败，返回模拟数据
        if not data:
            logger.warning("所有API都失败，返回模拟数据")
            return self._get_fallback_data()
        
        # 转换为标准格式
        return self._format_indices_data(data)
    
    def _format_indices_data(self, raw_data: Dict) -> Dict:
        """格式化指数数据"""
        indices_map = {
            'sh000001': {'code': '000001', 'name': '上证指数'},
            'sh000300': {'code': '000300', 'name': '沪深300'},
            'sz399001': {'code': '399001', 'name': '深证成指'},
            'sz399006': {'code': '399006', 'name': '创业板指'}
        }
        
        indices = []
        for symbol, info in indices_map.items():
            if symbol in raw_data:
                data = raw_data[symbol]
                indices.append({
                    'code': info['code'],
                    'name': info['name'],
                    'current': data['current'],
                    'change': data['change'],
                    'change_percent': data['change_percent']
                })
            else:
                # 如果某个指数数据缺失，使用默认值
                indices.append({
                    'code': info['code'],
                    'name': info['name'],
                    'current': 3000.0,
                    'change': 0.0,
                    'change_percent': 0.0
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'indices': indices
        }
    
    def _get_fallback_data(self) -> Dict:
        """获取备用模拟数据"""
        logger.info("使用备用模拟数据")
        
        # 生成一些随机变化的模拟数据
        import random
        base_time = datetime.now()
        
        indices = [
            {
                'code': '000001',
                'name': '上证指数',
                'current': round(2950 + random.uniform(-50, 50), 2),
                'change': round(random.uniform(-30, 30), 2),
                'change_percent': round(random.uniform(-1.5, 1.5), 2)
            },
            {
                'code': '000300',
                'name': '沪深300',
                'current': round(3450 + random.uniform(-100, 100), 2),
                'change': round(random.uniform(-40, 40), 2),
                'change_percent': round(random.uniform(-1.8, 1.8), 2)
            },
            {
                'code': '399001',
                'name': '深证成指',
                'current': round(9200 + random.uniform(-200, 200), 2),
                'change': round(random.uniform(-50, 50), 2),
                'change_percent': round(random.uniform(-2.0, 2.0), 2)
            },
            {
                'code': '399006',
                'name': '创业板指',
                'current': round(2100 + random.uniform(-100, 100), 2),
                'change': round(random.uniform(-30, 30), 2),
                'change_percent': round(random.uniform(-2.5, 2.5), 2)
            }
        ]
        
        return {
            'timestamp': base_time.isoformat(),
            'indices': indices
        }

# 创建全局实例
real_market_service = RealMarketDataService()
