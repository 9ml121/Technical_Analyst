"""
异常类定义 - 微服务架构共享工具
定义量化交易系统的各种异常类型
"""


class QuantSystemError(Exception):
    """量化系统基础异常类"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        初始化异常

        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigError(QuantSystemError):
    """配置相关异常"""

    def __init__(self, message: str, config_file: str = None, config_key: str = None):
        """
        初始化配置异常

        Args:
            message: 错误消息
            config_file: 配置文件路径
            config_key: 配置键名
        """
        super().__init__(message, "CONFIG_ERROR")
        self.config_file = config_file
        self.config_key = config_key
        self.details.update({
            "config_file": config_file,
            "config_key": config_key
        })


class DataError(QuantSystemError):
    """数据相关异常"""

    def __init__(self, message: str, data_source: str = None, data_type: str = None):
        """
        初始化数据异常

        Args:
            message: 错误消息
            data_source: 数据源
            data_type: 数据类型
        """
        super().__init__(message, "DATA_ERROR")
        self.data_source = data_source
        self.data_type = data_type
        self.details.update({
            "data_source": data_source,
            "data_type": data_type
        })


class StrategyError(QuantSystemError):
    """策略相关异常"""

    def __init__(self, message: str, strategy_name: str = None, strategy_type: str = None):
        """
        初始化策略异常

        Args:
            message: 错误消息
            strategy_name: 策略名称
            strategy_type: 策略类型
        """
        super().__init__(message, "STRATEGY_ERROR")
        self.strategy_name = strategy_name
        self.strategy_type = strategy_type
        self.details.update({
            "strategy_name": strategy_name,
            "strategy_type": strategy_type
        })


class BacktestError(QuantSystemError):
    """回测相关异常"""

    def __init__(self, message: str, backtest_id: str = None, period: str = None):
        """
        初始化回测异常

        Args:
            message: 错误消息
            backtest_id: 回测ID
            period: 回测期间
        """
        super().__init__(message, "BACKTEST_ERROR")
        self.backtest_id = backtest_id
        self.period = period
        self.details.update({
            "backtest_id": backtest_id,
            "period": period
        })


class ValidationError(QuantSystemError):
    """验证相关异常"""

    def __init__(self, message: str, field: str = None, value: any = None):
        """
        初始化验证异常

        Args:
            message: 错误消息
            field: 字段名
            value: 字段值
        """
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value
        self.details.update({
            "field": field,
            "value": str(value) if value is not None else None
        })


class NetworkError(QuantSystemError):
    """网络相关异常"""

    def __init__(self, message: str, url: str = None, status_code: int = None):
        """
        初始化网络异常

        Args:
            message: 错误消息
            url: 请求URL
            status_code: HTTP状态码
        """
        super().__init__(message, "NETWORK_ERROR")
        self.url = url
        self.status_code = status_code
        self.details.update({
            "url": url,
            "status_code": status_code
        })


class DatabaseError(QuantSystemError):
    """数据库相关异常"""

    def __init__(self, message: str, table: str = None, operation: str = None):
        """
        初始化数据库异常

        Args:
            message: 错误消息
            table: 表名
            operation: 操作类型
        """
        super().__init__(message, "DATABASE_ERROR")
        self.table = table
        self.operation = operation
        self.details.update({
            "table": table,
            "operation": operation
        })


class ServiceError(QuantSystemError):
    """微服务相关异常"""

    def __init__(self, message: str, service_name: str = None, endpoint: str = None):
        """
        初始化服务异常

        Args:
            message: 错误消息
            service_name: 服务名称
            endpoint: 端点
        """
        super().__init__(message, "SERVICE_ERROR")
        self.service_name = service_name
        self.endpoint = endpoint
        self.details.update({
            "service_name": service_name,
            "endpoint": endpoint
        })


class AuthenticationError(QuantSystemError):
    """认证相关异常"""

    def __init__(self, message: str, user_id: str = None, permission: str = None):
        """
        初始化认证异常

        Args:
            message: 错误消息
            user_id: 用户ID
            permission: 权限
        """
        super().__init__(message, "AUTHENTICATION_ERROR")
        self.user_id = user_id
        self.permission = permission
        self.details.update({
            "user_id": user_id,
            "permission": permission
        })


class RateLimitError(QuantSystemError):
    """限流相关异常"""

    def __init__(self, message: str, limit: int = None, window: int = None):
        """
        初始化限流异常

        Args:
            message: 错误消息
            limit: 限制次数
            window: 时间窗口
        """
        super().__init__(message, "RATE_LIMIT_ERROR")
        self.limit = limit
        self.window = window
        self.details.update({
            "limit": limit,
            "window": window
        })


class ModelError(QuantSystemError):
    """模型相关异常"""

    def __init__(self, message: str, model_name: str = None, model_type: str = None):
        """
        初始化模型异常

        Args:
            message: 错误消息
            model_name: 模型名称
            model_type: 模型类型
        """
        super().__init__(message, "MODEL_ERROR")
        self.model_name = model_name
        self.model_type = model_type
        self.details.update({
            "model_name": model_name,
            "model_type": model_type
        })


class FeatureError(QuantSystemError):
    """特征工程相关异常"""

    def __init__(self, message: str, feature_name: str = None, feature_type: str = None):
        """
        初始化特征异常

        Args:
            message: 错误消息
            feature_name: 特征名称
            feature_type: 特征类型
        """
        super().__init__(message, "FEATURE_ERROR")
        self.feature_name = feature_name
        self.feature_type = feature_type
        self.details.update({
            "feature_name": feature_name,
            "feature_type": feature_type
        })


class TradingError(QuantSystemError):
    """交易相关异常"""

    def __init__(self, message: str, order_id: str = None, stock_code: str = None):
        """
        初始化交易异常

        Args:
            message: 错误消息
            order_id: 订单ID
            stock_code: 股票代码
        """
        super().__init__(message, "TRADING_ERROR")
        self.order_id = order_id
        self.stock_code = stock_code
        self.details.update({
            "order_id": order_id,
            "stock_code": stock_code
        })


class RiskError(QuantSystemError):
    """风控相关异常"""

    def __init__(self, message: str, risk_type: str = None, threshold: float = None):
        """
        初始化风控异常

        Args:
            message: 错误消息
            risk_type: 风险类型
            threshold: 阈值
        """
        super().__init__(message, "RISK_ERROR")
        self.risk_type = risk_type
        self.threshold = threshold
        self.details.update({
            "risk_type": risk_type,
            "threshold": threshold
        })


# 异常处理工具函数
def handle_exception(func):
    """异常处理装饰器"""
    import functools
    import logging

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except QuantSystemError as e:
            logging.error(f"量化系统异常: {e}")
            raise
        except Exception as e:
            logging.error(f"未预期的异常: {e}")
            raise QuantSystemError(f"未预期的异常: {e}", "UNEXPECTED_ERROR")

    return wrapper


def is_retryable_error(error: Exception) -> bool:
    """
    判断错误是否可重试

    Args:
        error: 异常对象

    Returns:
        是否可重试
    """
    retryable_errors = (
        NetworkError,
        DatabaseError,
        ServiceError,
        RateLimitError
    )

    return isinstance(error, retryable_errors)


def get_error_summary(error: Exception) -> dict:
    """
    获取错误摘要

    Args:
        error: 异常对象

    Returns:
        错误摘要字典
    """
    if isinstance(error, QuantSystemError):
        return {
            "error_type": error.__class__.__name__,
            "error_code": error.error_code,
            "message": error.message,
            "details": error.details
        }
    else:
        return {
            "error_type": error.__class__.__name__,
            "error_code": "UNKNOWN_ERROR",
            "message": str(error),
            "details": {}
        }
