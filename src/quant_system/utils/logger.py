"""
日志工具模块

提供统一的日志配置和管理功能
"""
import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class QuantLogger:
    """量化系统日志器"""
    
    def __init__(self, name: str = "quant_system"):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self._configured = False
    
    def configure(self, 
                 level: str = "INFO",
                 log_file: Optional[str] = None,
                 log_dir: str = "logs",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 console_output: bool = True,
                 format_string: Optional[str] = None) -> logging.Logger:
        """
        配置日志器
        
        Args:
            level: 日志级别
            log_file: 日志文件名
            log_dir: 日志目录
            max_file_size: 最大文件大小
            backup_count: 备份文件数量
            console_output: 是否输出到控制台
            format_string: 自定义格式字符串
            
        Returns:
            配置好的日志器
        """
        if self._configured:
            return self.logger
        
        # 设置日志级别
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        
        # 创建日志目录
        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)
        
        # 默认格式
        if format_string is None:
            format_string = (
                '%(asctime)s - %(name)s - %(levelname)s - '
                '%(filename)s:%(lineno)d - %(message)s'
            )
        
        formatter = logging.Formatter(format_string)
        
        # 文件处理器
        if log_file:
            file_path = log_dir_path / log_file
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # 控制台处理器
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # 控制台使用简化格式
            console_format = '%(asctime)s - %(levelname)s - %(message)s'
            console_formatter = logging.Formatter(console_format)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # 错误日志单独文件
        error_file_path = log_dir_path / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file_path,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        self._configured = True
        self.logger.info(f"日志器 {self.name} 配置完成")
        
        return self.logger
    
    def get_logger(self) -> logging.Logger:
        """获取日志器实例"""
        if not self._configured:
            # 使用默认配置
            self.configure()
        return self.logger

class PerformanceLogger:
    """性能日志器"""
    
    def __init__(self, logger: logging.Logger):
        """
        初始化性能日志器
        
        Args:
            logger: 主日志器
        """
        self.logger = logger
        self.start_times: Dict[str, datetime] = {}
    
    def start_timer(self, operation: str):
        """开始计时"""
        self.start_times[operation] = datetime.now()
        self.logger.debug(f"开始执行: {operation}")
    
    def end_timer(self, operation: str, log_level: str = "INFO"):
        """结束计时并记录"""
        if operation not in self.start_times:
            self.logger.warning(f"未找到操作的开始时间: {operation}")
            return
        
        start_time = self.start_times.pop(operation)
        duration = (datetime.now() - start_time).total_seconds()
        
        log_func = getattr(self.logger, log_level.lower(), self.logger.info)
        log_func(f"操作完成: {operation}, 耗时: {duration:.3f}秒")
        
        return duration
    
    def log_memory_usage(self):
        """记录内存使用情况"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            self.logger.info(f"内存使用: {memory_mb:.2f} MB")
        except ImportError:
            self.logger.debug("psutil未安装，无法记录内存使用")

class TradeLogger:
    """交易日志器"""
    
    def __init__(self, logger: logging.Logger):
        """
        初始化交易日志器
        
        Args:
            logger: 主日志器
        """
        self.logger = logger
    
    def log_signal(self, stock_code: str, signal_type: str, price: float, reason: str):
        """记录交易信号"""
        self.logger.info(
            f"交易信号 - 股票: {stock_code}, 信号: {signal_type}, "
            f"价格: {price:.2f}, 原因: {reason}"
        )
    
    def log_order(self, order_id: str, stock_code: str, action: str, 
                  quantity: int, price: float, status: str):
        """记录订单信息"""
        self.logger.info(
            f"订单 - ID: {order_id}, 股票: {stock_code}, 动作: {action}, "
            f"数量: {quantity}, 价格: {price:.2f}, 状态: {status}"
        )
    
    def log_trade(self, trade_id: str, stock_code: str, action: str,
                  quantity: int, price: float, amount: float, pnl: Optional[float] = None):
        """记录成交信息"""
        pnl_str = f", 盈亏: {pnl:.2f}" if pnl is not None else ""
        self.logger.info(
            f"成交 - ID: {trade_id}, 股票: {stock_code}, 动作: {action}, "
            f"数量: {quantity}, 价格: {price:.2f}, 金额: {amount:.2f}{pnl_str}"
        )
    
    def log_portfolio_update(self, total_value: float, cash: float, 
                           positions_count: int, daily_return: float):
        """记录组合更新"""
        self.logger.info(
            f"组合更新 - 总资产: {total_value:.2f}, 现金: {cash:.2f}, "
            f"持仓数: {positions_count}, 日收益率: {daily_return:.4f}"
        )

# 全局日志器实例
_global_logger = None

def get_logger(name: str = "quant_system") -> logging.Logger:
    """
    获取全局日志器实例
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = QuantLogger(name)
        
        # 从环境变量读取配置
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_file = os.getenv("LOG_FILE", "system.log")
        
        _global_logger.configure(
            level=log_level,
            log_file=log_file,
            console_output=True
        )
    
    return _global_logger.get_logger()

def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    根据配置设置日志
    
    Args:
        config: 日志配置字典
        
    Returns:
        配置好的日志器
    """
    logger_config = config.get("logging", {})
    
    quant_logger = QuantLogger()
    return quant_logger.configure(
        level=logger_config.get("level", "INFO"),
        log_file=logger_config.get("file", "system.log"),
        log_dir=logger_config.get("dir", "logs"),
        max_file_size=logger_config.get("max_file_size", 10 * 1024 * 1024),
        backup_count=logger_config.get("backup_count", 5),
        console_output=logger_config.get("console", True)
    )

def log_function_call(func):
    """装饰器：记录函数调用"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = f"{func.__module__}.{func.__name__}"
        
        logger.debug(f"调用函数: {func_name}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数完成: {func_name}")
            return result
        except Exception as e:
            logger.error(f"函数异常: {func_name}, 错误: {e}")
            raise
    
    return wrapper

def log_performance(operation_name: str):
    """装饰器：记录性能"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()
            perf_logger = PerformanceLogger(logger)
            
            perf_logger.start_timer(operation_name)
            try:
                result = func(*args, **kwargs)
                perf_logger.end_timer(operation_name)
                return result
            except Exception as e:
                perf_logger.end_timer(operation_name, "ERROR")
                raise
        
        return wrapper
    return decorator
