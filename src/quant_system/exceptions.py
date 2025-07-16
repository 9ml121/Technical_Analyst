"""
量化投资系统自定义异常类

定义系统中使用的各种异常类型，提供更精确的错误处理和调试信息。
"""

from typing import Optional, Dict, Any


class QuantSystemError(Exception):
    """量化系统基础异常类"""

    def __init__(self, message: str, error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
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

    def __str__(self) -> str:
        """返回异常字符串表示"""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }


class DataSourceError(QuantSystemError):
    """数据源相关错误"""

    def __init__(self, message: str, source_name: Optional[str] = None,
                 error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        初始化数据源错误

        Args:
            message: 错误消息
            source_name: 数据源名称
            error_code: 错误代码
            details: 错误详情
        """
        # 如果没有指定error_code，使用默认值
        if error_code is None:
            error_code = "DATA_SOURCE_ERROR"

        super().__init__(message, error_code, details)
        self.source_name = source_name

        if source_name:
            self.details['source_name'] = source_name


class NetworkError(DataSourceError):
    """网络连接错误"""

    def __init__(self, message: str, url: Optional[str] = None,
                 status_code: Optional[int] = None, **kwargs):
        """
        初始化网络错误

        Args:
            message: 错误消息
            url: 请求URL
            status_code: HTTP状态码
        """
        details = kwargs.get('details', {})
        if url:
            details['url'] = url
        if status_code:
            details['status_code'] = status_code

        # 移除details参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('details', None)

        super().__init__(message, error_code="NETWORK_ERROR", details=details, **kwargs_copy)
        self.url = url
        self.status_code = status_code


class DataValidationError(QuantSystemError):
    """数据验证错误"""

    def __init__(self, message: str, field_name: Optional[str] = None,
                 field_value: Optional[Any] = None, **kwargs):
        """
        初始化数据验证错误

        Args:
            message: 错误消息
            field_name: 字段名称
            field_value: 字段值
        """
        details = kwargs.get('details', {})
        if field_name:
            details['field_name'] = field_name
        if field_value is not None:
            details['field_value'] = field_value

        # 移除details参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('details', None)

        super().__init__(message, error_code="DATA_VALIDATION_ERROR",
                         details=details, **kwargs_copy)
        self.field_name = field_name
        self.field_value = field_value


class StrategyError(QuantSystemError):
    """策略执行错误"""

    def __init__(self, message: str, strategy_name: Optional[str] = None,
                 strategy_type: Optional[str] = None, **kwargs):
        """
        初始化策略错误

        Args:
            message: 错误消息
            strategy_name: 策略名称
            strategy_type: 策略类型
        """
        details = kwargs.get('details', {})
        if strategy_name:
            details['strategy_name'] = strategy_name
        if strategy_type:
            details['strategy_type'] = strategy_type

        # 移除details参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('details', None)

        super().__init__(message, error_code="STRATEGY_ERROR", details=details, **kwargs_copy)
        self.strategy_name = strategy_name
        self.strategy_type = strategy_type


class ModelTrainingError(StrategyError):
    """机器学习模型训练错误"""

    def __init__(self, message: str, model_type: Optional[str] = None,
                 training_data_size: Optional[int] = None, **kwargs):
        """
        初始化模型训练错误

        Args:
            message: 错误消息
            model_type: 模型类型
            training_data_size: 训练数据大小
        """
        details = kwargs.get('details', {})
        if model_type:
            details['model_type'] = model_type
        if training_data_size:
            details['training_data_size'] = training_data_size

        # 移除error_code参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('error_code', None)
        kwargs_copy['details'] = details

        super().__init__(message, **kwargs_copy)
        self.error_code = "MODEL_TRAINING_ERROR"
        self.model_type = model_type
        self.training_data_size = training_data_size


class BacktestError(QuantSystemError):
    """回测执行错误"""

    def __init__(self, message: str, backtest_period: Optional[str] = None,
                 strategy_name: Optional[str] = None, **kwargs):
        """
        初始化回测错误

        Args:
            message: 错误消息
            backtest_period: 回测期间
            strategy_name: 策略名称
        """
        details = kwargs.get('details', {})
        if backtest_period:
            details['backtest_period'] = backtest_period
        if strategy_name:
            details['strategy_name'] = strategy_name

        # 移除details参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('details', None)

        super().__init__(message, error_code="BACKTEST_ERROR", details=details, **kwargs_copy)
        self.backtest_period = backtest_period
        self.strategy_name = strategy_name


class InsufficientDataError(BacktestError):
    """数据不足错误"""

    def __init__(self, message: str, required_days: Optional[int] = None,
                 available_days: Optional[int] = None, **kwargs):
        """
        初始化数据不足错误

        Args:
            message: 错误消息
            required_days: 需要的天数
            available_days: 可用的天数
        """
        details = kwargs.get('details', {})
        if required_days:
            details['required_days'] = required_days
        if available_days:
            details['available_days'] = available_days

        # 移除error_code参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('error_code', None)
        kwargs_copy['details'] = details

        super().__init__(message, **kwargs_copy)
        self.error_code = "INSUFFICIENT_DATA_ERROR"
        self.required_days = required_days
        self.available_days = available_days


class ConfigError(QuantSystemError):
    """配置相关错误"""

    def __init__(self, message: str, config_file: Optional[str] = None,
                 config_section: Optional[str] = None, **kwargs):
        """
        初始化配置错误

        Args:
            message: 错误消息
            config_file: 配置文件路径
            config_section: 配置节名称
        """
        details = kwargs.get('details', {})
        if config_file:
            details['config_file'] = config_file
        if config_section:
            details['config_section'] = config_section

        # 移除details和error_code参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('details', None)
        kwargs_copy.pop('error_code', None)

        super().__init__(message, error_code="CONFIG_ERROR", details=details, **kwargs_copy)
        self.config_file = config_file
        self.config_section = config_section


class ConfigNotFoundError(ConfigError):
    """配置文件未找到错误"""

    def __init__(self, config_file: str, **kwargs):
        """
        初始化配置文件未找到错误

        Args:
            config_file: 配置文件路径
        """
        message = f"配置文件未找到: {config_file}"
        # 移除error_code参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('error_code', None)

        super().__init__(message, config_file=config_file, **kwargs_copy)
        self.error_code = "CONFIG_NOT_FOUND_ERROR"


class ConfigValidationError(ConfigError):
    """配置验证错误"""

    def __init__(self, message: str, validation_errors: Optional[list] = None, **kwargs):
        """
        初始化配置验证错误

        Args:
            message: 错误消息
            validation_errors: 验证错误列表
        """
        details = kwargs.get('details', {})
        if validation_errors:
            details['validation_errors'] = validation_errors

        # 移除error_code参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('error_code', None)
        kwargs_copy['details'] = details

        super().__init__(message, **kwargs_copy)
        self.error_code = "CONFIG_VALIDATION_ERROR"
        self.validation_errors = validation_errors or []


class ConfigFormatError(ConfigError):
    """配置格式错误"""

    def __init__(self, message: str, line_number: Optional[int] = None, **kwargs):
        """
        初始化配置格式错误

        Args:
            message: 错误消息
            line_number: 错误行号
        """
        details = kwargs.get('details', {})
        if line_number:
            details['line_number'] = line_number

        # 移除error_code参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('error_code', None)
        kwargs_copy['details'] = details

        super().__init__(message, **kwargs_copy)
        self.error_code = "CONFIG_FORMAT_ERROR"
        self.line_number = line_number


class CacheError(QuantSystemError):
    """缓存操作错误"""

    def __init__(self, message: str, cache_key: Optional[str] = None,
                 cache_type: Optional[str] = None, **kwargs):
        """
        初始化缓存错误

        Args:
            message: 错误消息
            cache_key: 缓存键
            cache_type: 缓存类型
        """
        details = kwargs.get('details', {})
        if cache_key:
            details['cache_key'] = cache_key
        if cache_type:
            details['cache_type'] = cache_type

        # 移除details参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('details', None)

        super().__init__(message, error_code="CACHE_ERROR", details=details, **kwargs_copy)
        self.cache_key = cache_key
        self.cache_type = cache_type


class PerformanceError(QuantSystemError):
    """性能相关错误"""

    def __init__(self, message: str, metric_name: Optional[str] = None,
                 threshold: Optional[float] = None, actual_value: Optional[float] = None, **kwargs):
        """
        初始化性能错误

        Args:
            message: 错误消息
            metric_name: 指标名称
            threshold: 阈值
            actual_value: 实际值
        """
        details = kwargs.get('details', {})
        if metric_name:
            details['metric_name'] = metric_name
        if threshold is not None:
            details['threshold'] = threshold
        if actual_value is not None:
            details['actual_value'] = actual_value

        # 移除details参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('details', None)

        super().__init__(message, error_code="PERFORMANCE_ERROR", details=details, **kwargs_copy)
        self.metric_name = metric_name
        self.threshold = threshold
        self.actual_value = actual_value


class TradingError(QuantSystemError):
    """交易执行错误"""

    def __init__(self, message: str, stock_code: Optional[str] = None,
                 action: Optional[str] = None, **kwargs):
        """
        初始化交易错误

        Args:
            message: 错误消息
            stock_code: 股票代码
            action: 交易动作
        """
        details = kwargs.get('details', {})
        if stock_code:
            details['stock_code'] = stock_code
        if action:
            details['action'] = action

        # 移除details参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('details', None)

        super().__init__(message, error_code="TRADING_ERROR", details=details, **kwargs_copy)
        self.stock_code = stock_code
        self.action = action


class InsufficientFundsError(TradingError):
    """资金不足错误"""

    def __init__(self, message: str, required_amount: Optional[float] = None,
                 available_amount: Optional[float] = None, **kwargs):
        """
        初始化资金不足错误

        Args:
            message: 错误消息
            required_amount: 需要金额
            available_amount: 可用金额
        """
        details = kwargs.get('details', {})
        if required_amount:
            details['required_amount'] = required_amount
        if available_amount:
            details['available_amount'] = available_amount

        # 移除error_code参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('error_code', None)
        kwargs_copy['details'] = details

        super().__init__(message, **kwargs_copy)
        self.error_code = "INSUFFICIENT_FUNDS_ERROR"
        self.required_amount = required_amount
        self.available_amount = available_amount


class PositionLimitError(TradingError):
    """持仓限制错误"""

    def __init__(self, message: str, current_positions: Optional[int] = None,
                 max_positions: Optional[int] = None, **kwargs):
        """
        初始化持仓限制错误

        Args:
            message: 错误消息
            current_positions: 当前持仓数
            max_positions: 最大持仓数
        """
        details = kwargs.get('details', {})
        if current_positions:
            details['current_positions'] = current_positions
        if max_positions:
            details['max_positions'] = max_positions

        # 移除error_code参数，避免重复传递
        kwargs_copy = kwargs.copy()
        kwargs_copy.pop('error_code', None)
        kwargs_copy['details'] = details

        super().__init__(message, **kwargs_copy)
        self.error_code = "POSITION_LIMIT_ERROR"
        self.current_positions = current_positions
        self.max_positions = max_positions


# 异常处理工具函数
def handle_exception(exception: Exception, logger=None, reraise: bool = True) -> Dict[str, Any]:
    """
    统一异常处理函数

    Args:
        exception: 异常对象
        logger: 日志记录器
        reraise: 是否重新抛出异常

    Returns:
        异常信息字典
    """
    if isinstance(exception, QuantSystemError):
        error_info = exception.to_dict()
    else:
        error_info = {
            'error_type': exception.__class__.__name__,
            'message': str(exception),
            'error_code': None,
            'details': {}
        }

    if logger:
        logger.error(f"异常处理: {error_info['error_type']} - {error_info['message']}",
                     exc_info=True)

    if reraise:
        raise exception

    return error_info


def create_error_response(exception: Exception) -> Dict[str, Any]:
    """
    创建错误响应

    Args:
        exception: 异常对象

    Returns:
        错误响应字典
    """
    error_info = handle_exception(exception, reraise=False)

    return {
        'success': False,
        'error': error_info,
        'timestamp': str(Exception.__class__.__module__)  # 简化的时间戳
    }


# 异常映射表，用于根据错误类型快速创建异常
EXCEPTION_MAPPING = {
    'data_source': DataSourceError,
    'network': NetworkError,
    'data_validation': DataValidationError,
    'strategy': StrategyError,
    'model_training': ModelTrainingError,
    'backtest': BacktestError,
    'insufficient_data': InsufficientDataError,
    'config': ConfigError,
    'config_not_found': ConfigNotFoundError,
    'config_validation': ConfigValidationError,
    'config_format': ConfigFormatError,
    'cache': CacheError,
    'performance': PerformanceError,
    'trading': TradingError,
    'insufficient_funds': InsufficientFundsError,
    'position_limit': PositionLimitError,
}


def create_exception(error_type: str, message: str, **kwargs) -> QuantSystemError:
    """
    根据错误类型创建异常

    Args:
        error_type: 错误类型
        message: 错误消息
        **kwargs: 其他参数

    Returns:
        异常对象
    """
    exception_class = EXCEPTION_MAPPING.get(error_type, QuantSystemError)
    return exception_class(message, **kwargs)


if __name__ == "__main__":
    # 异常使用示例
    try:
        # 数据源错误示例
        raise DataSourceError("无法连接到东方财富API", source_name="eastmoney",
                              error_code="CONNECTION_FAILED")
    except DataSourceError as e:
        print(f"捕获数据源错误: {e}")
        print(f"错误详情: {e.to_dict()}")

    try:
        # 配置错误示例
        raise ConfigValidationError("策略配置验证失败",
                                    config_file="momentum_strategy.yaml",
                                    validation_errors=["连续天数必须是正整数", "最小收益率不能为负"])
    except ConfigValidationError as e:
        print(f"捕获配置错误: {e}")
        print(f"验证错误: {e.validation_errors}")

    try:
        # 交易错误示例
        raise InsufficientFundsError("资金不足，无法买入",
                                     stock_code="000001",
                                     required_amount=10000.0,
                                     available_amount=5000.0)
    except InsufficientFundsError as e:
        print(f"捕获交易错误: {e}")
        print(f"需要资金: {e.required_amount}, 可用资金: {e.available_amount}")
