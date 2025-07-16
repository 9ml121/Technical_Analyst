#!/usr/bin/env python3
"""
数据验证器工具

提供数据质量检查和验证功能，确保数据的完整性和准确性。
"""

import sys
import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import logging

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quant_system.models.stock_data import StockData, StockDataValidator
from quant_system.utils.logger import get_logger
from quant_system.exceptions import DataValidationError

logger = get_logger(__name__)


class DataQualityChecker:
    """数据质量检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.validator = StockDataValidator()
        self.issues = []
        self.warnings = []
        self.stats = {}
    
    def check_database(self, db_path: str) -> Dict[str, Any]:
        """检查数据库数据质量"""
        logger.info(f"开始检查数据库: {db_path}")
        
        if not Path(db_path).exists():
            raise FileNotFoundError(f"数据库文件不存在: {db_path}")
        
        self.issues.clear()
        self.warnings.clear()
        self.stats.clear()
        
        try:
            conn = sqlite3.connect(db_path)
            
            # 检查表结构
            self._check_table_structure(conn)
            
            # 检查数据完整性
            self._check_data_integrity(conn)
            
            # 检查数据质量
            self._check_data_quality(conn)
            
            # 检查数据一致性
            self._check_data_consistency(conn)
            
            # 生成统计信息
            self._generate_statistics(conn)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"检查数据库时出错: {e}")
            self.issues.append(f"数据库访问错误: {e}")
        
        return self._generate_report()
    
    def check_csv_file(self, csv_path: str) -> Dict[str, Any]:
        """检查CSV文件数据质量"""
        logger.info(f"开始检查CSV文件: {csv_path}")
        
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV文件不存在: {csv_path}")
        
        self.issues.clear()
        self.warnings.clear()
        self.stats.clear()
        
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_path)
            
            # 检查文件结构
            self._check_csv_structure(df)
            
            # 检查数据质量
            self._check_csv_data_quality(df)
            
            # 生成统计信息
            self._generate_csv_statistics(df)
            
        except Exception as e:
            logger.error(f"检查CSV文件时出错: {e}")
            self.issues.append(f"CSV文件读取错误: {e}")
        
        return self._generate_report()
    
    def validate_stock_data_list(self, stock_data_list: List[StockData]) -> Dict[str, Any]:
        """验证股票数据列表"""
        logger.info(f"开始验证 {len(stock_data_list)} 条股票数据")
        
        self.issues.clear()
        self.warnings.clear()
        self.stats.clear()
        
        valid_count = 0
        invalid_count = 0
        
        for i, stock_data in enumerate(stock_data_list):
            try:
                errors = self.validator.validate_stock_data(stock_data)
                if errors:
                    invalid_count += 1
                    for error in errors:
                        self.issues.append(f"第{i+1}条数据 ({stock_data.code}): {error}")
                else:
                    valid_count += 1
            except Exception as e:
                invalid_count += 1
                self.issues.append(f"第{i+1}条数据验证失败: {e}")
        
        self.stats = {
            'total_records': len(stock_data_list),
            'valid_records': valid_count,
            'invalid_records': invalid_count,
            'validation_rate': valid_count / len(stock_data_list) if stock_data_list else 0
        }
        
        return self._generate_report()
    
    def _check_table_structure(self, conn: sqlite3.Connection):
        """检查表结构"""
        cursor = conn.cursor()
        
        # 检查是否存在股票数据表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock_data'")
        if not cursor.fetchone():
            self.issues.append("缺少股票数据表 (stock_data)")
            return
        
        # 检查表字段
        cursor.execute("PRAGMA table_info(stock_data)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['code', 'name', 'date', 'open_price', 'close_price', 
                          'high_price', 'low_price', 'volume', 'amount']
        
        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            self.issues.append(f"缺少必需字段: {', '.join(missing_columns)}")
    
    def _check_data_integrity(self, conn: sqlite3.Connection):
        """检查数据完整性"""
        cursor = conn.cursor()
        
        # 检查空值
        cursor.execute("""
            SELECT COUNT(*) FROM stock_data 
            WHERE code IS NULL OR name IS NULL OR date IS NULL 
            OR open_price IS NULL OR close_price IS NULL
        """)
        null_count = cursor.fetchone()[0]
        if null_count > 0:
            self.issues.append(f"发现 {null_count} 条记录包含空值")
        
        # 检查重复记录
        cursor.execute("""
            SELECT code, date, COUNT(*) as cnt 
            FROM stock_data 
            GROUP BY code, date 
            HAVING cnt > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            self.issues.append(f"发现 {len(duplicates)} 组重复记录")
    
    def _check_data_quality(self, conn: sqlite3.Connection):
        """检查数据质量"""
        cursor = conn.cursor()
        
        # 检查价格异常
        cursor.execute("""
            SELECT COUNT(*) FROM stock_data 
            WHERE open_price <= 0 OR close_price <= 0 
            OR high_price <= 0 OR low_price <= 0
        """)
        invalid_price_count = cursor.fetchone()[0]
        if invalid_price_count > 0:
            self.issues.append(f"发现 {invalid_price_count} 条记录包含无效价格")
        
        # 检查价格逻辑
        cursor.execute("""
            SELECT COUNT(*) FROM stock_data 
            WHERE high_price < GREATEST(open_price, close_price)
            OR low_price > LEAST(open_price, close_price)
        """)
        illogical_price_count = cursor.fetchone()[0]
        if illogical_price_count > 0:
            self.issues.append(f"发现 {illogical_price_count} 条记录价格逻辑异常")
        
        # 检查成交量异常
        cursor.execute("""
            SELECT COUNT(*) FROM stock_data 
            WHERE volume < 0
        """)
        invalid_volume_count = cursor.fetchone()[0]
        if invalid_volume_count > 0:
            self.issues.append(f"发现 {invalid_volume_count} 条记录成交量为负")
        
        # 检查异常涨跌幅
        cursor.execute("""
            SELECT COUNT(*) FROM stock_data s1
            JOIN stock_data s2 ON s1.code = s2.code 
            AND s1.date = date(s2.date, '+1 day')
            WHERE ABS((s1.close_price - s2.close_price) / s2.close_price) > 0.2
        """)
        extreme_change_count = cursor.fetchone()[0]
        if extreme_change_count > 0:
            self.warnings.append(f"发现 {extreme_change_count} 条记录涨跌幅超过20%")
    
    def _check_data_consistency(self, conn: sqlite3.Connection):
        """检查数据一致性"""
        cursor = conn.cursor()
        
        # 检查股票代码格式
        cursor.execute("""
            SELECT COUNT(*) FROM stock_data 
            WHERE LENGTH(code) != 6 OR code NOT GLOB '[0-9][0-9][0-9][0-9][0-9][0-9]'
        """)
        invalid_code_count = cursor.fetchone()[0]
        if invalid_code_count > 0:
            self.issues.append(f"发现 {invalid_code_count} 条记录股票代码格式异常")
        
        # 检查日期格式
        cursor.execute("""
            SELECT COUNT(*) FROM stock_data 
            WHERE date NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        """)
        invalid_date_count = cursor.fetchone()[0]
        if invalid_date_count > 0:
            self.issues.append(f"发现 {invalid_date_count} 条记录日期格式异常")
    
    def _generate_statistics(self, conn: sqlite3.Connection):
        """生成统计信息"""
        cursor = conn.cursor()
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM stock_data")
        total_records = cursor.fetchone()[0]
        
        # 股票数量
        cursor.execute("SELECT COUNT(DISTINCT code) FROM stock_data")
        unique_stocks = cursor.fetchone()[0]
        
        # 日期范围
        cursor.execute("SELECT MIN(date), MAX(date) FROM stock_data")
        date_range = cursor.fetchone()
        
        # 平均每日记录数
        cursor.execute("SELECT COUNT(DISTINCT date) FROM stock_data")
        unique_dates = cursor.fetchone()[0]
        avg_daily_records = total_records / unique_dates if unique_dates > 0 else 0
        
        self.stats = {
            'total_records': total_records,
            'unique_stocks': unique_stocks,
            'unique_dates': unique_dates,
            'date_range': {
                'start': date_range[0],
                'end': date_range[1]
            },
            'avg_daily_records': round(avg_daily_records, 2)
        }
    
    def _check_csv_structure(self, df: pd.DataFrame):
        """检查CSV结构"""
        required_columns = ['code', 'name', 'date', 'open_price', 'close_price', 
                          'high_price', 'low_price', 'volume', 'amount']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.issues.append(f"CSV缺少必需字段: {', '.join(missing_columns)}")
        
        if df.empty:
            self.issues.append("CSV文件为空")
    
    def _check_csv_data_quality(self, df: pd.DataFrame):
        """检查CSV数据质量"""
        # 检查空值
        null_counts = df.isnull().sum()
        for column, count in null_counts.items():
            if count > 0:
                self.warnings.append(f"字段 '{column}' 有 {count} 个空值")
        
        # 检查价格字段
        price_columns = ['open_price', 'close_price', 'high_price', 'low_price']
        for col in price_columns:
            if col in df.columns:
                invalid_prices = (df[col] <= 0).sum()
                if invalid_prices > 0:
                    self.issues.append(f"字段 '{col}' 有 {invalid_prices} 个无效价格")
        
        # 检查成交量
        if 'volume' in df.columns:
            invalid_volumes = (df['volume'] < 0).sum()
            if invalid_volumes > 0:
                self.issues.append(f"成交量字段有 {invalid_volumes} 个负值")
    
    def _generate_csv_statistics(self, df: pd.DataFrame):
        """生成CSV统计信息"""
        self.stats = {
            'total_records': len(df),
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        if 'code' in df.columns:
            self.stats['unique_stocks'] = df['code'].nunique()
        
        if 'date' in df.columns:
            self.stats['unique_dates'] = df['date'].nunique()
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        return {
            'timestamp': datetime.now().isoformat(),
            'is_valid': len(self.issues) == 0,
            'issues': self.issues,
            'warnings': self.warnings,
            'statistics': self.stats,
            'summary': {
                'total_issues': len(self.issues),
                'total_warnings': len(self.warnings),
                'quality_score': self._calculate_quality_score()
            }
        }
    
    def _calculate_quality_score(self) -> float:
        """计算数据质量评分"""
        if not self.stats:
            return 0.0
        
        # 基础分数
        score = 100.0
        
        # 根据问题数量扣分
        score -= len(self.issues) * 10
        score -= len(self.warnings) * 2
        
        # 确保分数在0-100之间
        return max(0.0, min(100.0, score))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据质量检查工具")
    parser.add_argument("--type", choices=['database', 'csv'], required=True,
                       help="数据类型")
    parser.add_argument("--path", required=True, help="数据文件路径")
    parser.add_argument("--output", help="输出报告文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.WARNING)
    
    # 创建数据质量检查器
    checker = DataQualityChecker()
    
    try:
        # 执行检查
        if args.type == 'database':
            report = checker.check_database(args.path)
        elif args.type == 'csv':
            report = checker.check_csv_file(args.path)
        else:
            print(f"不支持的数据类型: {args.type}")
            return 1
        
        # 输出报告
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"报告已保存到: {args.output}")
        else:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        
        # 输出摘要
        print(f"\n{'='*50}")
        print("数据质量检查摘要")
        print(f"{'='*50}")
        print(f"检查时间: {report['timestamp']}")
        print(f"数据质量评分: {report['summary']['quality_score']:.1f}/100")
        print(f"发现问题: {report['summary']['total_issues']} 个")
        print(f"警告信息: {report['summary']['total_warnings']} 个")
        
        if report['issues']:
            print(f"\n❌ 发现的问题:")
            for i, issue in enumerate(report['issues'], 1):
                print(f"  {i}. {issue}")
        
        if report['warnings']:
            print(f"\n⚠️ 警告信息:")
            for i, warning in enumerate(report['warnings'], 1):
                print(f"  {i}. {warning}")
        
        if report['is_valid']:
            print(f"\n✅ 数据质量检查通过")
            return 0
        else:
            print(f"\n❌ 数据质量检查失败")
            return 1
            
    except Exception as e:
        logger.error(f"数据质量检查失败: {e}")
        print(f"错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
