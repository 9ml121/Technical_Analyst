"""
自定义异常类测试
"""

import pytest
from quant_system.exceptions import (
    QuantSystemError, DataSourceError, NetworkError, DataValidationError,
    StrategyError, ModelTrainingError, BacktestError, InsufficientDataError,
    ConfigError, ConfigNotFoundError, ConfigValidationError, ConfigFormatError,
    CacheError, PerformanceError, TradingError, InsufficientFundsError,
    PositionLimitError, handle_exception, create_error_response, create_exception
)


class TestQuantSystemError:
    """量化系统基础异常测试"""
    
    def test_basic_exception(self):
        """测试基础异常创建"""
        error = QuantSystemError("测试错误")
        assert str(error) == "测试错误"
        assert error.message == "测试错误"
        assert error.error_code is None
        assert error.details == {}
    
    def test_exception_with_code(self):
        """测试带错误代码的异常"""
        error = QuantSystemError("测试错误", error_code="TEST_ERROR")
        assert str(error) == "[TEST_ERROR] 测试错误"
        assert error.error_code == "TEST_ERROR"
    
    def test_exception_with_details(self):
        """测试带详情的异常"""
        details = {"field": "value", "count": 10}
        error = QuantSystemError("测试错误", details=details)
        assert error.details == details
    
    def test_to_dict(self):
        """测试转换为字典"""
        error = QuantSystemError("测试错误", error_code="TEST_ERROR", 
                                details={"key": "value"})
        error_dict = error.to_dict()
        
        expected = {
            'error_type': 'QuantSystemError',
            'message': '测试错误',
            'error_code': 'TEST_ERROR',
            'details': {'key': 'value'}
        }
        assert error_dict == expected


class TestDataSourceError:
    """数据源错误测试"""
    
    def test_data_source_error(self):
        """测试数据源错误"""
        error = DataSourceError("连接失败", source_name="eastmoney")
        assert error.source_name == "eastmoney"
        assert error.details["source_name"] == "eastmoney"
    
    def test_network_error(self):
        """测试网络错误"""
        error = NetworkError("网络超时", url="http://api.example.com", status_code=500)
        assert error.url == "http://api.example.com"
        assert error.status_code == 500
        assert error.details["url"] == "http://api.example.com"
        assert error.details["status_code"] == 500
        assert error.error_code == "NETWORK_ERROR"


class TestDataValidationError:
    """数据验证错误测试"""
    
    def test_validation_error(self):
        """测试数据验证错误"""
        error = DataValidationError("价格无效", field_name="price", field_value=-10)
        assert error.field_name == "price"
        assert error.field_value == -10
        assert error.details["field_name"] == "price"
        assert error.details["field_value"] == -10
        assert error.error_code == "DATA_VALIDATION_ERROR"


class TestStrategyError:
    """策略错误测试"""
    
    def test_strategy_error(self):
        """测试策略错误"""
        error = StrategyError("策略执行失败", strategy_name="动量策略", strategy_type="momentum")
        assert error.strategy_name == "动量策略"
        assert error.strategy_type == "momentum"
        assert error.details["strategy_name"] == "动量策略"
        assert error.details["strategy_type"] == "momentum"
    
    def test_model_training_error(self):
        """测试模型训练错误"""
        error = ModelTrainingError("训练失败", model_type="random_forest", training_data_size=1000)
        assert error.model_type == "random_forest"
        assert error.training_data_size == 1000
        assert error.details["model_type"] == "random_forest"
        assert error.details["training_data_size"] == 1000
        assert error.error_code == "MODEL_TRAINING_ERROR"


class TestBacktestError:
    """回测错误测试"""
    
    def test_backtest_error(self):
        """测试回测错误"""
        error = BacktestError("回测失败", backtest_period="2023-01-01 to 2023-12-31", 
                            strategy_name="动量策略")
        assert error.backtest_period == "2023-01-01 to 2023-12-31"
        assert error.strategy_name == "动量策略"
        assert error.error_code == "BACKTEST_ERROR"
    
    def test_insufficient_data_error(self):
        """测试数据不足错误"""
        error = InsufficientDataError("数据不足", required_days=30, available_days=10)
        assert error.required_days == 30
        assert error.available_days == 10
        assert error.details["required_days"] == 30
        assert error.details["available_days"] == 10
        assert error.error_code == "INSUFFICIENT_DATA_ERROR"


class TestConfigError:
    """配置错误测试"""
    
    def test_config_error(self):
        """测试配置错误"""
        error = ConfigError("配置无效", config_file="config.yaml", config_section="database")
        assert error.config_file == "config.yaml"
        assert error.config_section == "database"
        assert error.details["config_file"] == "config.yaml"
        assert error.details["config_section"] == "database"
    
    def test_config_not_found_error(self):
        """测试配置文件未找到错误"""
        error = ConfigNotFoundError("missing_config.yaml")
        assert error.config_file == "missing_config.yaml"
        assert "配置文件未找到: missing_config.yaml" in str(error)
        assert error.error_code == "CONFIG_NOT_FOUND_ERROR"
    
    def test_config_validation_error(self):
        """测试配置验证错误"""
        validation_errors = ["字段A无效", "字段B缺失"]
        error = ConfigValidationError("验证失败", validation_errors=validation_errors)
        assert error.validation_errors == validation_errors
        assert error.details["validation_errors"] == validation_errors
        assert error.error_code == "CONFIG_VALIDATION_ERROR"
    
    def test_config_format_error(self):
        """测试配置格式错误"""
        error = ConfigFormatError("YAML格式错误", line_number=15)
        assert error.line_number == 15
        assert error.details["line_number"] == 15
        assert error.error_code == "CONFIG_FORMAT_ERROR"


class TestCacheError:
    """缓存错误测试"""
    
    def test_cache_error(self):
        """测试缓存错误"""
        error = CacheError("缓存操作失败", cache_key="stock_data_000001", cache_type="memory")
        assert error.cache_key == "stock_data_000001"
        assert error.cache_type == "memory"
        assert error.details["cache_key"] == "stock_data_000001"
        assert error.details["cache_type"] == "memory"
        assert error.error_code == "CACHE_ERROR"


class TestPerformanceError:
    """性能错误测试"""
    
    def test_performance_error(self):
        """测试性能错误"""
        error = PerformanceError("性能阈值超标", metric_name="response_time", 
                               threshold=1.0, actual_value=2.5)
        assert error.metric_name == "response_time"
        assert error.threshold == 1.0
        assert error.actual_value == 2.5
        assert error.details["metric_name"] == "response_time"
        assert error.details["threshold"] == 1.0
        assert error.details["actual_value"] == 2.5
        assert error.error_code == "PERFORMANCE_ERROR"


class TestTradingError:
    """交易错误测试"""
    
    def test_trading_error(self):
        """测试交易错误"""
        error = TradingError("交易失败", stock_code="000001", action="BUY")
        assert error.stock_code == "000001"
        assert error.action == "BUY"
        assert error.details["stock_code"] == "000001"
        assert error.details["action"] == "BUY"
        assert error.error_code == "TRADING_ERROR"
    
    def test_insufficient_funds_error(self):
        """测试资金不足错误"""
        error = InsufficientFundsError("资金不足", required_amount=10000.0, available_amount=5000.0)
        assert error.required_amount == 10000.0
        assert error.available_amount == 5000.0
        assert error.details["required_amount"] == 10000.0
        assert error.details["available_amount"] == 5000.0
        assert error.error_code == "INSUFFICIENT_FUNDS_ERROR"
    
    def test_position_limit_error(self):
        """测试持仓限制错误"""
        error = PositionLimitError("持仓超限", current_positions=10, max_positions=5)
        assert error.current_positions == 10
        assert error.max_positions == 5
        assert error.details["current_positions"] == 10
        assert error.details["max_positions"] == 5
        assert error.error_code == "POSITION_LIMIT_ERROR"


class TestExceptionUtils:
    """异常工具函数测试"""
    
    def test_handle_exception_with_quant_error(self):
        """测试处理量化系统异常"""
        error = DataSourceError("测试错误", source_name="test")
        
        # 测试不重新抛出异常
        result = handle_exception(error, reraise=False)
        assert result['error_type'] == 'DataSourceError'
        assert result['message'] == '测试错误'
        assert result['error_code'] is not None
    
    def test_handle_exception_with_standard_error(self):
        """测试处理标准异常"""
        error = ValueError("标准错误")
        
        # 测试不重新抛出异常
        result = handle_exception(error, reraise=False)
        assert result['error_type'] == 'ValueError'
        assert result['message'] == '标准错误'
        assert result['error_code'] is None
    
    def test_handle_exception_reraise(self):
        """测试重新抛出异常"""
        error = DataSourceError("测试错误")
        
        with pytest.raises(DataSourceError):
            handle_exception(error, reraise=True)
    
    def test_create_error_response(self):
        """测试创建错误响应"""
        error = ConfigError("配置错误", error_code="CONFIG_ERROR")
        response = create_error_response(error)
        
        assert response['success'] is False
        assert 'error' in response
        assert 'timestamp' in response
        assert response['error']['error_type'] == 'ConfigError'
        assert response['error']['message'] == '配置错误'
        assert response['error']['error_code'] == 'CONFIG_ERROR'
    
    def test_create_exception(self):
        """测试根据类型创建异常"""
        # 测试已知异常类型
        error = create_exception('data_source', '数据源错误', source_name='test')
        assert isinstance(error, DataSourceError)
        assert error.message == '数据源错误'
        assert error.source_name == 'test'
        
        # 测试未知异常类型
        error = create_exception('unknown_type', '未知错误')
        assert isinstance(error, QuantSystemError)
        assert error.message == '未知错误'
    
    def test_create_exception_with_kwargs(self):
        """测试使用关键字参数创建异常"""
        error = create_exception('network', '网络错误', 
                               url='http://test.com', status_code=404)
        assert isinstance(error, NetworkError)
        assert error.url == 'http://test.com'
        assert error.status_code == 404


class TestExceptionInheritance:
    """异常继承关系测试"""
    
    def test_inheritance_chain(self):
        """测试异常继承链"""
        # 所有自定义异常都应该继承自QuantSystemError
        assert issubclass(DataSourceError, QuantSystemError)
        assert issubclass(NetworkError, DataSourceError)
        assert issubclass(StrategyError, QuantSystemError)
        assert issubclass(ModelTrainingError, StrategyError)
        assert issubclass(BacktestError, QuantSystemError)
        assert issubclass(InsufficientDataError, BacktestError)
        assert issubclass(ConfigError, QuantSystemError)
        assert issubclass(ConfigNotFoundError, ConfigError)
        assert issubclass(TradingError, QuantSystemError)
        assert issubclass(InsufficientFundsError, TradingError)
    
    def test_exception_catching(self):
        """测试异常捕获"""
        # 测试可以用基类捕获子类异常
        try:
            raise NetworkError("网络错误")
        except DataSourceError as e:
            assert isinstance(e, NetworkError)
        
        try:
            raise ModelTrainingError("训练错误")
        except StrategyError as e:
            assert isinstance(e, ModelTrainingError)
        
        try:
            raise InsufficientFundsError("资金不足")
        except TradingError as e:
            assert isinstance(e, InsufficientFundsError)


if __name__ == '__main__':
    pytest.main([__file__])
