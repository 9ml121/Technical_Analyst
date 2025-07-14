"""
配置验证器

提供配置文件的验证和校验功能
"""
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        """初始化配置验证器"""
        self.errors = []
        self.warnings = []
    
    def validate_system_config(self, config: Dict[str, Any]) -> bool:
        """
        验证系统配置
        
        Args:
            config: 系统配置字典
            
        Returns:
            验证是否通过
        """
        self.errors.clear()
        self.warnings.clear()
        
        # 验证必需的顶级配置项
        required_sections = ['system', 'logging', 'database', 'data_sources']
        for section in required_sections:
            if section not in config:
                self.errors.append(f"缺少必需的配置节: {section}")
        
        # 验证系统配置
        if 'system' in config:
            self._validate_system_section(config['system'])
        
        # 验证日志配置
        if 'logging' in config:
            self._validate_logging_section(config['logging'])
        
        # 验证数据库配置
        if 'database' in config:
            self._validate_database_section(config['database'])
        
        # 验证数据源配置
        if 'data_sources' in config:
            self._validate_data_sources_section(config['data_sources'])
        
        # 验证回测配置
        if 'backtest' in config:
            self._validate_backtest_section(config['backtest'])
        
        # 验证策略配置
        if 'strategy' in config:
            self._validate_strategy_section(config['strategy'])
        
        return len(self.errors) == 0
    
    def validate_strategy_config(self, config: Dict[str, Any]) -> bool:
        """
        验证策略配置
        
        Args:
            config: 策略配置字典
            
        Returns:
            验证是否通过
        """
        self.errors.clear()
        self.warnings.clear()
        
        # 验证策略基本信息
        if 'strategy_info' not in config:
            self.errors.append("缺少策略基本信息 (strategy_info)")
        else:
            self._validate_strategy_info(config['strategy_info'])
        
        # 验证选股条件
        if 'selection_criteria' not in config:
            self.errors.append("缺少选股条件 (selection_criteria)")
        else:
            self._validate_selection_criteria(config['selection_criteria'])
        
        # 验证交易规则
        if 'trading_rules' in config:
            self._validate_trading_rules(config['trading_rules'])
        
        # 验证仓位管理
        if 'position_management' in config:
            self._validate_position_management(config['position_management'])
        
        # 验证风险管理
        if 'risk_management' in config:
            self._validate_risk_management(config['risk_management'])
        
        return len(self.errors) == 0
    
    def validate_data_sources_config(self, config: Dict[str, Any]) -> bool:
        """
        验证数据源配置
        
        Args:
            config: 数据源配置字典
            
        Returns:
            验证是否通过
        """
        self.errors.clear()
        self.warnings.clear()
        
        # 验证优先级配置
        if 'priority' in config:
            self._validate_priority_config(config['priority'])
        
        # 验证各个数据源配置
        data_sources = ['eastmoney', 'tushare', 'yfinance', 'local']
        for source in data_sources:
            if source in config:
                self._validate_data_source_config(source, config[source])
        
        return len(self.errors) == 0
    
    def _validate_system_section(self, system_config: Dict[str, Any]):
        """验证系统配置节"""
        required_fields = ['name', 'version', 'environment']
        for field in required_fields:
            if field not in system_config:
                self.errors.append(f"系统配置缺少必需字段: {field}")
        
        # 验证环境值
        if 'environment' in system_config:
            valid_envs = ['development', 'testing', 'production']
            if system_config['environment'] not in valid_envs:
                self.errors.append(f"无效的环境值: {system_config['environment']}")
    
    def _validate_logging_section(self, logging_config: Dict[str, Any]):
        """验证日志配置节"""
        # 验证日志级别
        if 'level' in logging_config:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if logging_config['level'] not in valid_levels:
                self.errors.append(f"无效的日志级别: {logging_config['level']}")
        
        # 验证文件大小
        if 'max_file_size' in logging_config:
            if not isinstance(logging_config['max_file_size'], int) or logging_config['max_file_size'] <= 0:
                self.errors.append("日志文件最大大小必须是正整数")
        
        # 验证备份数量
        if 'backup_count' in logging_config:
            if not isinstance(logging_config['backup_count'], int) or logging_config['backup_count'] < 0:
                self.errors.append("日志备份数量必须是非负整数")
    
    def _validate_database_section(self, db_config: Dict[str, Any]):
        """验证数据库配置节"""
        # 验证数据库类型
        if 'type' in db_config:
            valid_types = ['sqlite', 'postgresql', 'mysql']
            if db_config['type'] not in valid_types:
                self.errors.append(f"不支持的数据库类型: {db_config['type']}")
        
        # 验证路径
        if 'path' in db_config and db_config['path'] != ':memory:':
            path = Path(db_config['path'])
            if not path.parent.exists():
                self.warnings.append(f"数据库目录不存在: {path.parent}")
    
    def _validate_data_sources_section(self, data_sources_config: Dict[str, Any]):
        """验证数据源配置节"""
        for source_name, source_config in data_sources_config.items():
            if not isinstance(source_config, dict):
                self.errors.append(f"数据源配置必须是字典: {source_name}")
                continue
            
            # 验证启用状态
            if 'enabled' not in source_config:
                self.warnings.append(f"数据源未指定启用状态: {source_name}")
            
            # 验证超时设置
            if 'timeout' in source_config:
                if not isinstance(source_config['timeout'], (int, float)) or source_config['timeout'] <= 0:
                    self.errors.append(f"数据源超时设置无效: {source_name}")
    
    def _validate_backtest_section(self, backtest_config: Dict[str, Any]):
        """验证回测配置节"""
        # 验证初始资金
        if 'initial_capital' in backtest_config:
            if not isinstance(backtest_config['initial_capital'], (int, float)) or backtest_config['initial_capital'] <= 0:
                self.errors.append("初始资金必须是正数")
        
        # 验证最大持仓数
        if 'max_positions' in backtest_config:
            if not isinstance(backtest_config['max_positions'], int) or backtest_config['max_positions'] <= 0:
                self.errors.append("最大持仓数必须是正整数")
        
        # 验证仓位比例
        if 'position_size_pct' in backtest_config:
            pct = backtest_config['position_size_pct']
            if not isinstance(pct, (int, float)) or not (0 < pct <= 1):
                self.errors.append("仓位比例必须在0-1之间")
        
        # 验证费率设置
        rate_fields = ['commission_rate', 'stamp_tax_rate', 'slippage_rate']
        for field in rate_fields:
            if field in backtest_config:
                rate = backtest_config[field]
                if not isinstance(rate, (int, float)) or not (0 <= rate <= 1):
                    self.errors.append(f"{field}必须在0-1之间")
    
    def _validate_strategy_section(self, strategy_config: Dict[str, Any]):
        """验证策略配置节"""
        if 'selection_criteria' in strategy_config:
            criteria = strategy_config['selection_criteria']
            
            # 验证连续天数
            if 'consecutive_days' in criteria:
                if not isinstance(criteria['consecutive_days'], int) or criteria['consecutive_days'] <= 0:
                    self.errors.append("连续天数必须是正整数")
            
            # 验证收益率
            if 'min_total_return' in criteria:
                if not isinstance(criteria['min_total_return'], (int, float)) or criteria['min_total_return'] < 0:
                    self.errors.append("最小总收益率必须是非负数")
            
            # 验证回撤
            if 'max_drawdown' in criteria:
                if not isinstance(criteria['max_drawdown'], (int, float)) or not (0 <= criteria['max_drawdown'] <= 1):
                    self.errors.append("最大回撤必须在0-1之间")
    
    def _validate_strategy_info(self, strategy_info: Dict[str, Any]):
        """验证策略基本信息"""
        required_fields = ['name', 'version', 'description', 'strategy_type']
        for field in required_fields:
            if field not in strategy_info:
                self.errors.append(f"策略信息缺少必需字段: {field}")
        
        # 验证策略类型
        if 'strategy_type' in strategy_info:
            valid_types = ['momentum', 'mean_reversion', 'breakout', 'custom']
            if strategy_info['strategy_type'] not in valid_types:
                self.errors.append(f"无效的策略类型: {strategy_info['strategy_type']}")
    
    def _validate_selection_criteria(self, criteria: Dict[str, Any]):
        """验证选股条件"""
        # 验证基础条件
        if 'basic_criteria' in criteria:
            basic = criteria['basic_criteria']
            
            if 'consecutive_days' in basic:
                if not isinstance(basic['consecutive_days'], int) or basic['consecutive_days'] <= 0:
                    self.errors.append("连续天数必须是正整数")
            
            if 'min_total_return' in basic:
                if not isinstance(basic['min_total_return'], (int, float)):
                    self.errors.append("最小总收益率必须是数字")
        
        # 验证价格筛选
        if 'price_filters' in criteria:
            price = criteria['price_filters']
            
            if 'min_stock_price' in price and 'max_stock_price' in price:
                if price['min_stock_price'] >= price['max_stock_price']:
                    self.errors.append("最小股价必须小于最大股价")
    
    def _validate_trading_rules(self, trading_rules: Dict[str, Any]):
        """验证交易规则"""
        rule_types = ['buy_rules', 'sell_rules', 'risk_rules']
        
        for rule_type in rule_types:
            if rule_type in trading_rules:
                rules = trading_rules[rule_type]
                if not isinstance(rules, list):
                    self.errors.append(f"{rule_type}必须是列表")
                    continue
                
                for i, rule in enumerate(rules):
                    if not isinstance(rule, dict):
                        self.errors.append(f"{rule_type}[{i}]必须是字典")
                        continue
                    
                    required_rule_fields = ['name', 'description', 'condition']
                    for field in required_rule_fields:
                        if field not in rule:
                            self.errors.append(f"{rule_type}[{i}]缺少必需字段: {field}")
    
    def _validate_position_management(self, position_mgmt: Dict[str, Any]):
        """验证仓位管理"""
        # 验证分配方法
        if 'allocation_method' in position_mgmt:
            valid_methods = ['equal_weight', 'risk_parity', 'momentum_weight']
            if position_mgmt['allocation_method'] not in valid_methods:
                self.errors.append(f"无效的仓位分配方法: {position_mgmt['allocation_method']}")
        
        # 验证仓位大小
        size_fields = ['base_position_size', 'max_position_size', 'min_position_size']
        for field in size_fields:
            if field in position_mgmt:
                size = position_mgmt[field]
                if not isinstance(size, (int, float)) or not (0 < size <= 1):
                    self.errors.append(f"{field}必须在0-1之间")
    
    def _validate_risk_management(self, risk_mgmt: Dict[str, Any]):
        """验证风险管理"""
        # 验证止损设置
        if 'stop_loss' in risk_mgmt:
            stop_loss = risk_mgmt['stop_loss']
            
            if 'method' in stop_loss:
                valid_methods = ['percentage', 'atr', 'volatility']
                if stop_loss['method'] not in valid_methods:
                    self.errors.append(f"无效的止损方法: {stop_loss['method']}")
            
            if 'percentage' in stop_loss:
                pct = stop_loss['percentage']
                if not isinstance(pct, (int, float)) or not (0 < pct < 1):
                    self.errors.append("止损比例必须在0-1之间")
    
    def _validate_priority_config(self, priority_config: Dict[str, Any]):
        """验证优先级配置"""
        for data_type, sources in priority_config.items():
            if not isinstance(sources, list):
                self.errors.append(f"优先级配置{data_type}必须是列表")
            elif not sources:
                self.warnings.append(f"优先级配置{data_type}为空")
    
    def _validate_data_source_config(self, source_name: str, source_config: Dict[str, Any]):
        """验证单个数据源配置"""
        # 验证基础字段
        if 'enabled' not in source_config:
            self.warnings.append(f"数据源{source_name}未指定启用状态")
        
        # 验证超时设置
        if 'timeout' in source_config:
            timeout = source_config['timeout']
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                self.errors.append(f"数据源{source_name}超时设置无效")
        
        # 验证重试设置
        if 'retry_count' in source_config:
            retry_count = source_config['retry_count']
            if not isinstance(retry_count, int) or retry_count < 0:
                self.errors.append(f"数据源{source_name}重试次数必须是非负整数")
    
    def get_validation_report(self) -> Dict[str, Any]:
        """
        获取验证报告
        
        Returns:
            验证报告字典
        """
        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy(),
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }
    
    def print_validation_report(self):
        """打印验证报告"""
        if self.errors:
            print("❌ 配置验证失败:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print("⚠️ 配置警告:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ 配置验证通过")
        elif not self.errors:
            print("✅ 配置验证通过 (有警告)")

# 便捷函数
def validate_config_file(config_path: str, config_type: str = 'system') -> bool:
    """
    验证配置文件
    
    Args:
        config_path: 配置文件路径
        config_type: 配置类型 ('system', 'strategy', 'data_sources')
        
    Returns:
        验证是否通过
    """
    try:
        import yaml
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        validator = ConfigValidator()
        
        if config_type == 'system':
            result = validator.validate_system_config(config)
        elif config_type == 'strategy':
            result = validator.validate_strategy_config(config)
        elif config_type == 'data_sources':
            result = validator.validate_data_sources_config(config)
        else:
            print(f"不支持的配置类型: {config_type}")
            return False
        
        validator.print_validation_report()
        return result
        
    except Exception as e:
        print(f"验证配置文件失败: {e}")
        return False
