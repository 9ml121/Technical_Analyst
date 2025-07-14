"""
股票数据获取演示 - 使用原生API调用
不依赖pandas，直接使用requests获取数据
"""
import requests
import json
import time
from datetime import datetime

class SimpleStockAPI:
    """简单的股票数据API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_a_stock_realtime_simple(self):
        """获取A股实时行情 - 简化版本"""
        print("正在获取A股实时行情...")
        
        try:
            # 使用东方财富的API
            url = "http://82.push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': '1',
                'pz': '20',  # 只获取前20只股票
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
                    
                    print(f"✅ 成功获取A股数据，共{len(stocks)}只股票")
                    print("\n股票信息:")
                    print("-" * 80)
                    print(f"{'序号':<4} {'代码':<8} {'名称':<12} {'最新价':<8} {'涨跌幅':<8} {'成交量':<12}")
                    print("-" * 80)
                    
                    for i, stock in enumerate(stocks[:10], 1):  # 只显示前10只
                        code = stock.get('f12', 'N/A')
                        name = stock.get('f14', 'N/A')
                        price = stock.get('f2', 0) / 100 if stock.get('f2') else 'N/A'
                        change_pct = stock.get('f3', 0) / 100 if stock.get('f3') else 'N/A'
                        volume = stock.get('f5', 0)
                        
                        print(f"{i:<4} {code:<8} {name:<12} {price:<8} {change_pct:<8}% {volume:<12}")
                    
                    return True
                else:
                    print("❌ 数据格式异常")
                    return False
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取A股数据失败: {e}")
            return False
    
    def get_hk_stock_info(self, symbol):
        """获取港股信息"""
        print(f"正在获取港股 {symbol} 信息...")
        
        try:
            # 使用新浪财经API
            url = f"https://hq.sinajs.cn/list=hk{symbol}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                if content and 'var hq_str_hk' in content:
                    # 解析数据
                    data_part = content.split('="')[1].split('";')[0]
                    fields = data_part.split(',')
                    
                    if len(fields) > 10:
                        name = fields[1]
                        price = fields[6]
                        change = fields[7]
                        change_pct = fields[8]
                        
                        print(f"✅ 港股信息:")
                        print(f"   代码: {symbol}")
                        print(f"   名称: {name}")
                        print(f"   最新价: {price}")
                        print(f"   涨跌额: {change}")
                        print(f"   涨跌幅: {change_pct}%")
                        
                        return True
                    else:
                        print("❌ 数据解析失败")
                        return False
                else:
                    print("❌ 未获取到有效数据")
                    return False
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取港股数据失败: {e}")
            return False
    
    def get_market_status(self):
        """获取市场状态"""
        print("正在检查市场状态...")
        
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        weekday = current_time.weekday()  # 0=Monday, 6=Sunday
        
        # 检查是否为工作日
        if weekday >= 5:  # Saturday or Sunday
            status = "休市 (周末)"
        elif (hour == 9 and minute >= 30) or (10 <= hour <= 11) or (hour == 13) or (hour == 14) or (hour == 15 and minute == 0):
            status = "开市中"
        else:
            status = "休市"
        
        print(f"✅ 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"✅ 市场状态: {status}")
        
        return status

def main():
    """主函数"""
    print("股票实时行情获取演示")
    print("=" * 60)
    print("本演示使用原生API调用，不依赖复杂的数据分析库")
    print("=" * 60)
    
    api = SimpleStockAPI()
    
    # 检查市场状态
    api.get_market_status()
    print()
    
    # 获取A股数据
    print("1. A股实时行情演示:")
    success_a = api.get_a_stock_realtime_simple()
    print()
    
    # 获取港股数据
    print("2. 港股实时行情演示:")
    hk_symbols = ['00700', '00941', '03690']  # 腾讯、中国移动、美团
    
    for symbol in hk_symbols:
        success_hk = api.get_hk_stock_info(symbol)
        print()
        time.sleep(1)  # 避免请求过于频繁
    
    print("=" * 60)
    print("演示完成!")
    print()
    print("说明:")
    print("1. 本演示展示了如何直接调用股票数据API")
    print("2. A股数据来源: 东方财富")
    print("3. 港股数据来源: 新浪财经")
    print("4. 实际使用时建议:")
    print("   - 配置专业的数据源API (如Tushare)")
    print("   - 添加数据缓存和错误重试机制")
    print("   - 遵守API调用频率限制")
    print("   - 使用更稳定的数据源")

if __name__ == "__main__":
    main()
