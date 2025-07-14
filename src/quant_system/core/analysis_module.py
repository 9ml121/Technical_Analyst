"""
样本数据分析模块
分析符合条件的股票，生成统计报告和图表
"""
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from collections import defaultdict, Counter

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)

class SampleAnalyzer:
    """样本数据分析器"""
    
    def __init__(self, output_dir: str = './Stat_Analysis'):
        """
        初始化分析器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建子目录
        self.charts_dir = os.path.join(output_dir, 'charts')
        self.reports_dir = os.path.join(output_dir, 'reports')
        os.makedirs(self.charts_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        logger.info(f"样本分析器初始化完成，输出目录: {output_dir}")
    
    def analyze_sample_stocks(self, sample_stocks: List[Dict]) -> Dict:
        """
        分析样本股票
        
        Args:
            sample_stocks: 符合条件的股票列表
            
        Returns:
            分析结果
        """
        if not sample_stocks:
            logger.warning("没有样本股票数据")
            return {}
        
        logger.info(f"开始分析{len(sample_stocks)}只样本股票")
        
        # 转换为DataFrame便于分析
        df = pd.DataFrame(sample_stocks)
        
        # 基础统计分析
        basic_stats = self._calculate_basic_statistics(df)
        
        # 时间分布分析
        time_distribution = self._analyze_time_distribution(df)
        
        # 收益率分析
        return_analysis = self._analyze_returns(df)
        
        # 行业分析
        industry_analysis = self._analyze_industries(df)
        
        # 风险分析
        risk_analysis = self._analyze_risks(df)
        
        # 生成图表
        self._generate_charts(df)
        
        # 汇总分析结果
        analysis_result = {
            'basic_stats': basic_stats,
            'time_distribution': time_distribution,
            'return_analysis': return_analysis,
            'industry_analysis': industry_analysis,
            'risk_analysis': risk_analysis,
            'sample_count': len(sample_stocks),
            'analysis_date': datetime.now().isoformat()
        }
        
        # 保存分析报告
        self._save_analysis_report(analysis_result)
        
        # 检查策略有效性
        self._check_strategy_validity(analysis_result)
        
        logger.info("样本分析完成")
        return analysis_result
    
    def _calculate_basic_statistics(self, df: pd.DataFrame) -> Dict:
        """计算基础统计信息"""
        stats = {
            'total_count': len(df),
            'avg_return': df['total_return'].mean(),
            'median_return': df['total_return'].median(),
            'std_return': df['total_return'].std(),
            'min_return': df['total_return'].min(),
            'max_return': df['total_return'].max(),
            'avg_drawdown': df['max_drawdown'].mean(),
            'max_drawdown': df['max_drawdown'].max(),
            'avg_volume': df['avg_volume'].mean(),
            'avg_amount': df['avg_amount'].mean()
        }
        
        # 收益率分布
        stats['return_distribution'] = {
            '15%-20%': len(df[(df['total_return'] >= 0.15) & (df['total_return'] < 0.20)]),
            '20%-30%': len(df[(df['total_return'] >= 0.20) & (df['total_return'] < 0.30)]),
            '30%-50%': len(df[(df['total_return'] >= 0.30) & (df['total_return'] < 0.50)]),
            '50%+': len(df[df['total_return'] >= 0.50])
        }
        
        return stats
    
    def _analyze_time_distribution(self, df: pd.DataFrame) -> Dict:
        """分析时间分布"""
        # 转换日期
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['end_date'] = pd.to_datetime(df['end_date'])
        
        # 按周统计
        df['week'] = df['start_date'].dt.to_period('W')
        weekly_counts = df.groupby('week').size().to_dict()
        weekly_counts = {str(k): v for k, v in weekly_counts.items()}
        
        # 按月统计
        df['month'] = df['start_date'].dt.to_period('M')
        monthly_counts = df.groupby('month').size().to_dict()
        monthly_counts = {str(k): v for k, v in monthly_counts.items()}
        
        # 按季度统计
        df['quarter'] = df['start_date'].dt.to_period('Q')
        quarterly_counts = df.groupby('quarter').size().to_dict()
        quarterly_counts = {str(k): v for k, v in quarterly_counts.items()}
        
        # 按年统计
        df['year'] = df['start_date'].dt.to_period('Y')
        yearly_counts = df.groupby('year').size().to_dict()
        yearly_counts = {str(k): v for k, v in yearly_counts.items()}
        
        return {
            'weekly': weekly_counts,
            'monthly': monthly_counts,
            'quarterly': quarterly_counts,
            'yearly': yearly_counts
        }
    
    def _analyze_returns(self, df: pd.DataFrame) -> Dict:
        """分析收益率"""
        returns = df['total_return']
        
        # 收益率统计
        return_stats = {
            'mean': returns.mean(),
            'median': returns.median(),
            'std': returns.std(),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'percentiles': {
                '25%': returns.quantile(0.25),
                '50%': returns.quantile(0.50),
                '75%': returns.quantile(0.75),
                '90%': returns.quantile(0.90),
                '95%': returns.quantile(0.95)
            }
        }
        
        # 胜率分析
        win_rate = len(df[df['total_return'] > 0]) / len(df) if len(df) > 0 else 0
        
        # 风险收益比
        risk_return_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
        
        return {
            'statistics': return_stats,
            'win_rate': win_rate,
            'risk_return_ratio': risk_return_ratio
        }
    
    def _analyze_industries(self, df: pd.DataFrame) -> Dict:
        """分析行业分布"""
        # 简化的行业分类（基于股票名称关键词）
        industry_keywords = {
            '银行': ['银行', '农行', '工行', '建行', '中行'],
            '科技': ['科技', '软件', '信息', '网络', '数据', '云'],
            '医药': ['医药', '生物', '制药', '医疗', '健康'],
            '地产': ['地产', '房地产', '置业', '发展'],
            '能源': ['石油', '煤炭', '电力', '能源', '新能源'],
            '制造': ['制造', '机械', '设备', '汽车', '钢铁'],
            '消费': ['消费', '食品', '饮料', '零售', '商贸'],
            '金融': ['证券', '保险', '信托', '租赁', '金融']
        }
        
        industry_distribution = defaultdict(int)
        industry_returns = defaultdict(list)
        
        for _, row in df.iterrows():
            name = row['name']
            classified = False
            
            for industry, keywords in industry_keywords.items():
                if any(keyword in name for keyword in keywords):
                    industry_distribution[industry] += 1
                    industry_returns[industry].append(row['total_return'])
                    classified = True
                    break
            
            if not classified:
                industry_distribution['其他'] += 1
                industry_returns['其他'].append(row['total_return'])
        
        # 计算各行业平均收益率
        industry_avg_returns = {}
        for industry, returns in industry_returns.items():
            industry_avg_returns[industry] = np.mean(returns) if returns else 0
        
        return {
            'distribution': dict(industry_distribution),
            'avg_returns': industry_avg_returns
        }
    
    def _analyze_risks(self, df: pd.DataFrame) -> Dict:
        """分析风险指标"""
        # 最大回撤分析
        drawdowns = df['max_drawdown']
        
        risk_metrics = {
            'avg_drawdown': drawdowns.mean(),
            'max_drawdown': drawdowns.max(),
            'drawdown_std': drawdowns.std(),
            'high_risk_count': len(df[df['max_drawdown'] > 0.03]),  # 回撤超过3%
            'low_risk_count': len(df[df['max_drawdown'] <= 0.01])   # 回撤小于1%
        }
        
        # 收益风险比
        returns = df['total_return']
        risk_metrics['sharpe_like_ratio'] = returns.mean() / drawdowns.mean() if drawdowns.mean() > 0 else 0
        
        return risk_metrics
    
    def _generate_charts(self, df: pd.DataFrame):
        """生成分析图表"""
        # 设置图表样式
        plt.style.use('seaborn-v0_8')
        
        # 1. 收益率分布直方图
        plt.figure(figsize=(10, 6))
        plt.hist(df['total_return'] * 100, bins=30, alpha=0.7, edgecolor='black')
        plt.title('收益率分布', fontsize=14, fontweight='bold')
        plt.xlabel('收益率 (%)')
        plt.ylabel('频次')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.charts_dir, 'return_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 时间序列分布
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['month'] = df['start_date'].dt.to_period('M')
        monthly_counts = df.groupby('month').size()
        
        plt.figure(figsize=(12, 6))
        monthly_counts.plot(kind='bar')
        plt.title('月度样本股票数量分布', fontsize=14, fontweight='bold')
        plt.xlabel('月份')
        plt.ylabel('股票数量')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.charts_dir, 'monthly_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 收益率vs回撤散点图
        plt.figure(figsize=(10, 8))
        plt.scatter(df['max_drawdown'] * 100, df['total_return'] * 100, alpha=0.6)
        plt.title('收益率 vs 最大回撤', fontsize=14, fontweight='bold')
        plt.xlabel('最大回撤 (%)')
        plt.ylabel('收益率 (%)')
        plt.grid(True, alpha=0.3)
        
        # 添加趋势线
        z = np.polyfit(df['max_drawdown'], df['total_return'], 1)
        p = np.poly1d(z)
        plt.plot(df['max_drawdown'] * 100, p(df['max_drawdown']) * 100, "r--", alpha=0.8)
        
        plt.savefig(os.path.join(self.charts_dir, 'return_vs_drawdown.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. 成交量分布
        plt.figure(figsize=(10, 6))
        plt.hist(np.log10(df['avg_amount'] + 1), bins=30, alpha=0.7, edgecolor='black')
        plt.title('成交额分布 (对数尺度)', fontsize=14, fontweight='bold')
        plt.xlabel('log10(成交额)')
        plt.ylabel('频次')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.charts_dir, 'volume_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"图表已保存到: {self.charts_dir}")
    
    def _save_analysis_report(self, analysis_result: Dict):
        """保存分析报告"""
        # JSON格式报告
        json_file = os.path.join(self.reports_dir, 'analysis_report.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
        
        # 文本格式报告
        txt_file = os.path.join(self.reports_dir, 'analysis_summary.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("样本股票分析报告\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"分析时间: {analysis_result['analysis_date']}\n")
            f.write(f"样本数量: {analysis_result['sample_count']}只\n\n")
            
            # 基础统计
            basic = analysis_result['basic_stats']
            f.write("基础统计信息:\n")
            f.write(f"  平均收益率: {basic['avg_return']:.2%}\n")
            f.write(f"  收益率中位数: {basic['median_return']:.2%}\n")
            f.write(f"  收益率标准差: {basic['std_return']:.2%}\n")
            f.write(f"  最大收益率: {basic['max_return']:.2%}\n")
            f.write(f"  最小收益率: {basic['min_return']:.2%}\n")
            f.write(f"  平均最大回撤: {basic['avg_drawdown']:.2%}\n\n")
            
            # 时间分布
            time_dist = analysis_result['time_distribution']
            f.write("时间分布统计:\n")
            f.write("  季度分布:\n")
            for quarter, count in time_dist['quarterly'].items():
                f.write(f"    {quarter}: {count}只\n")
            f.write("\n")
            
            # 收益率分析
            return_analysis = analysis_result['return_analysis']
            f.write("收益率分析:\n")
            f.write(f"  胜率: {return_analysis['win_rate']:.2%}\n")
            f.write(f"  风险收益比: {return_analysis['risk_return_ratio']:.2f}\n\n")
            
            # 行业分析
            industry = analysis_result['industry_analysis']
            f.write("行业分布:\n")
            for ind, count in industry['distribution'].items():
                avg_return = industry['avg_returns'].get(ind, 0)
                f.write(f"  {ind}: {count}只 (平均收益: {avg_return:.2%})\n")
        
        logger.info(f"分析报告已保存到: {self.reports_dir}")
    
    def _check_strategy_validity(self, analysis_result: Dict):
        """检查策略有效性"""
        quarterly_counts = analysis_result['time_distribution']['quarterly']
        
        # 检查每个季度的股票数量
        low_count_quarters = []
        for quarter, count in quarterly_counts.items():
            if count < 3:
                low_count_quarters.append((quarter, count))
        
        if low_count_quarters:
            print("\n⚠️  策略有效性警告:")
            print("以下季度符合条件的股票少于3只:")
            for quarter, count in low_count_quarters:
                print(f"  {quarter}: {count}只")
            
            response = input("\n该选股策略可能过于严格，是否继续？(Y/N): ").strip().upper()
            if response == 'N':
                print("程序终止")
                exit(0)
            else:
                print("继续执行...")
        else:
            print("✅ 策略有效性检查通过")

if __name__ == "__main__":
    # 测试样本分析器
    print("测试样本数据分析模块...")
    
    # 创建模拟样本数据
    sample_data = []
    for i in range(50):
        sample_data.append({
            'code': f'00000{i:02d}',
            'name': f'测试股票{i}',
            'start_date': date(2024, 1, 1) + timedelta(days=i*7),
            'end_date': date(2024, 1, 3) + timedelta(days=i*7),
            'total_return': np.random.uniform(0.15, 0.50),
            'max_drawdown': np.random.uniform(0.01, 0.05),
            'avg_volume': np.random.uniform(1000000, 10000000),
            'avg_amount': np.random.uniform(10000000, 100000000),
            'consecutive_days': 3
        })
    
    # 创建分析器并分析
    analyzer = SampleAnalyzer()
    result = analyzer.analyze_sample_stocks(sample_data)
    
    print(f"分析完成，样本数量: {result['sample_count']}")
    print(f"平均收益率: {result['basic_stats']['avg_return']:.2%}")
    print(f"胜率: {result['return_analysis']['win_rate']:.2%}")
    
    print("分析报告和图表已生成！")
