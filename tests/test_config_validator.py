"""
配置验证器测试
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from quant_system.utils.config_validator import ConfigValidator, validate_config_file


class TestConfigValidator:
    """配置验证器测试类"""

    def setup_method(self):
        """测试前设置"""
        self.validator = ConfigValidator()

    def test_validate_system_config_success(self):
        """测试系统配置验证成功"""
        config = {
            'system': {
                'name': '量化投资系统',
                'version': '2.0.0',
                'environment': 'development'
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/system.log',
                'max_size': '10MB',
                'backup_count': 5
            },
            'database': {
                'type': 'sqlite',
                'path': 'data/stock_data.db',
                'pool_size': 10,
                'timeout': 30
            },
            'data_sources': {
                'eastmoney': {
                    'enabled': True,
                    'priority': 1
                }
            }
        }

        assert self.validator.validate_system_config(config) is True
        report = self.validator.get_validation_report()
        assert len(report['errors']) == 0

    def test_validate_system_config_missing_sections(self):
        """测试系统配置缺少必需节"""
        config = {
            'system': {
                'name': '量化投资系统',
                'version': '2.0.0'
            }
            # 缺少logging和database节
        }

        assert self.validator.validate_system_config(config) is False
        report = self.validator.get_validation_report()
        errors = report['errors']
        assert any('缺少必需的配置节: logging' in error for error in errors)
        assert any('缺少必需的配置节: database' in error for error in errors)
        assert any('缺少必需的配置节: data_sources' in error for error in errors)

    def test_validate_system_config_invalid_version(self):
        """测试系统配置版本格式无效"""
        config = {
            'system': {
                'name': '量化投资系统',
                'version': '2.0',  # 无效版本格式
                'environment': 'development'
            },
            'logging': {
                'level': 'INFO'
            },
            'database': {
                'type': 'sqlite'
            },
            'data_sources': {
                'eastmoney': {'enabled': True}
            }
        }

        assert self.validator.validate_system_config(config) is False
        report = self.validator.get_validation_report()
        errors = report['errors']
        assert any('版本格式无效' in error for error in errors)

    def test_validate_system_config_invalid_log_level(self):
        """测试系统配置日志级别无效"""
        config = {
            'system': {
                'name': '量化投资系统',
                'version': '2.0.0'
            },
            'logging': {
                'level': 'INVALID_LEVEL'  # 无效日志级别
            },
            'database': {
                'type': 'sqlite'
            },
            'data_sources': {
                'eastmoney': {'enabled': True}
            }
        }

        assert self.validator.validate_system_config(config) is False
        report = self.validator.get_validation_report()
        errors = report['errors']
        assert any('无效的日志级别' in error for error in errors)

    def test_validate_strategy_config_success(self):
        """测试策略配置验证成功"""
        config = {
            'strategy_info': {
                'name': '动量策略',
                'version': '1.0.0',
                'strategy_type': 'momentum'
            },
            'basic_criteria': {
                'consecutive_days': 3,
                'min_total_return': 0.15,
                'max_drawdown': 0.05
            },
            'price_filters': {
                'min_stock_price': 5.0,
                'max_stock_price': 200.0
            },
            'risk_management': {
                'max_positions': 5,
                'position_size_pct': 0.20,
                'stop_loss_pct': 0.08
            }
        }

        assert self.validator.validate_strategy_config(config) is True
        report = self.validator.get_validation_report()
        assert len(report['errors']) == 0

    def test_validate_strategy_config_missing_info(self):
        """测试策略配置缺少策略信息"""
        config = {
            'basic_criteria': {
                'consecutive_days': 3,
                'min_total_return': 0.15
            }
            # 缺少strategy_info节
        }

        assert self.validator.validate_strategy_config(config) is False
        report = self.validator.get_validation_report()
        errors = report['errors']
        assert any('缺少策略信息' in error for error in errors)

    def test_validate_strategy_config_invalid_consecutive_days(self):
        """测试策略配置连续天数无效"""
        config = {
            'strategy_info': {
                'name': '动量策略',
                'version': '1.0.0',
                'strategy_type': 'momentum'
            },
            'basic_criteria': {
                'consecutive_days': 0,  # 无效值
                'min_total_return': 0.15
            }
        }

        assert self.validator.validate_strategy_config(config) is False
        report = self.validator.get_validation_report()
        errors = report['errors']
        assert any('连续天数必须是正整数' in error for error in errors)

    def test_validate_strategy_config_invalid_price_range(self):
        """测试策略配置价格范围无效"""
        config = {
            'strategy_info': {
                'name': '动量策略',
                'version': '1.0.0',
                'strategy_type': 'momentum'
            },
            'price_filters': {
                'min_stock_price': 200.0,  # 最低价高于最高价
                'max_stock_price': 100.0
            }
        }

        assert self.validator.validate_strategy_config(config) is False
        report = self.validator.get_validation_report()
        errors = report['errors']
        assert any('最低股价必须小于最高股价' in error for error in errors)

    def test_validate_data_source_config_success(self):
        """测试数据源配置验证成功"""
        config = {
            'data_sources': {
                'eastmoney': {
                    'enabled': True,
                    'priority': 1,
                    'timeout': 30,
                    'retry_count': 3
                },
                'tushare': {
                    'enabled': False,
                    'priority': 2,
                    'timeout': 30
                }
            },
            'default_source': 'eastmoney',
            'fallback_enabled': True
        }

        assert self.validator.validate_data_sources_config(config) is True
        report = self.validator.get_validation_report()
        assert len(report['errors']) == 0

    def test_validate_data_source_config_missing_sources(self):
        """测试数据源配置缺少数据源节"""
        config = {
            'default_source': 'eastmoney'
            # 缺少data_sources节
        }

        assert self.validator.validate_data_sources_config(config) is False
        report = self.validator.get_validation_report()
        errors = report['errors']
        assert any('缺少数据源配置' in error for error in errors)

    def test_validate_data_source_config_invalid_default(self):
        """测试数据源配置默认源无效"""
        config = {
            'data_sources': {
                'eastmoney': {
                    'enabled': True,
                    'priority': 1
                }
            },
            'default_source': 'nonexistent'  # 不存在的数据源
        }

        assert self.validator.validate_data_sources_config(config) is False
        report = self.validator.get_validation_report()
        errors = report['errors']
        assert any('默认数据源' in error and '未在数据源列表中定义' in error for error in errors)

    def test_validate_data_source_invalid_priority(self):
        """测试数据源优先级无效"""
        config = {
            'data_sources': {
                'eastmoney': {
                    'enabled': True,
                    'priority': 0,  # 无效优先级
                    'timeout': 30
                }
            }
        }

        assert self.validator.validate_data_sources_config(config) is False
        report = self.validator.get_validation_report()
        errors = report['errors']
        assert any('优先级必须是正整数' in error for error in errors)

    def test_get_validation_warnings(self):
        """测试获取验证警告"""
        config = {
            'system': {
                'name': '量化投资系统',
                'version': '2.0.0',
                'environment': 'unknown_env'  # 未知环境，应产生警告
            },
            'logging': {
                'level': 'INFO'
            },
            'database': {
                'type': 'unknown_db'  # 未知数据库类型，应产生警告
            }
        }

        self.validator.validate_system_config(config)
        report = self.validator.get_validation_report()
        warnings = report['warnings']
        assert len(warnings) > 0
        assert any('未知的环境类型' in warning for warning in warnings)
        assert any('未知的数据库类型' in warning for warning in warnings)

    def test_has_errors_and_warnings(self):
        """测试错误和警告检查方法"""
        # 初始状态
        report = self.validator.get_validation_report()
        assert len(report['errors']) == 0
        assert len(report['warnings']) == 0

        # 验证有错误的配置
        config = {
            'system': {
                'version': 'invalid'  # 无效版本
            }
            # 缺少必需节
        }

        self.validator.validate_system_config(config)
        report = self.validator.get_validation_report()
        assert len(report['errors']) > 0


class TestValidateConfigFile:
    """配置文件验证函数测试类"""

    def test_validate_config_file_success(self):
        """测试配置文件验证成功"""
        config_data = {
            'system': {
                'name': '量化投资系统',
                'version': '2.0.0'
            },
            'logging': {
                'level': 'INFO'
            },
            'database': {
                'type': 'sqlite'
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            result = validate_config_file(temp_path, 'system')
            assert result is True
        finally:
            Path(temp_path).unlink()

    def test_validate_config_file_not_found(self):
        """测试配置文件不存在"""
        result = validate_config_file('nonexistent.yaml', 'system')
        assert result is False

    def test_validate_config_file_invalid_yaml(self):
        """测试无效YAML文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')  # 无效YAML
            temp_path = f.name

        try:
            result = validate_config_file(temp_path, 'system')
            assert result is False
        finally:
            Path(temp_path).unlink()

    def test_validate_config_file_empty(self):
        """测试空配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('')  # 空文件
            temp_path = f.name

        try:
            result = validate_config_file(temp_path, 'system')
            assert result is False
        finally:
            Path(temp_path).unlink()

    def test_validate_config_file_unknown_type(self):
        """测试未知配置类型"""
        config_data = {'test': 'data'}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            result = validate_config_file(temp_path, 'unknown_type')
            assert result is False
        finally:
            Path(temp_path).unlink()

    @patch('builtins.open', mock_open(read_data='test: data'))
    @patch('yaml.safe_load')
    def test_validate_config_file_yaml_error(self, mock_yaml_load):
        """测试YAML加载错误"""
        mock_yaml_load.side_effect = yaml.YAMLError("YAML parsing error")

        result = validate_config_file('test.yaml', 'system')
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__])
