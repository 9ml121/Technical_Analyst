"""
配置系统单元测试

测试配置加载器、验证器等配置相关功能
"""
from quant_system.utils.config_validator import ConfigValidator
from quant_system.utils.config_loader import ConfigLoader
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

# 添加src目录到Python路径
import sys
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestConfigLoader:
    """配置加载器测试"""

    def setup_method(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_loader = ConfigLoader(self.temp_dir)

    def test_init(self):
        """测试初始化"""
        assert self.config_loader.config_dir == Path(self.temp_dir)
        # 环境变量可能被设置为其他值，所以不强制检查
        assert self.config_loader.environment in [
            "development", "testing", "production"]
        # 检查缓存是否正确初始化
        if self.config_loader.enable_cache:
            assert self.config_loader._cache is not None
        else:
            assert self.config_loader._cache is None

    def test_load_config_with_cache(self):
        """测试配置加载和缓存"""
        # 创建测试配置文件
        config_data = {"test": "value"}
        config_file = Path(self.temp_dir) / "test.yaml"

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        # 第一次加载
        result1 = self.config_loader.load_config("test")
        # 配置加载器会合并默认配置，所以检查关键字段
        assert "test" in result1
        assert result1["test"] == "value"

        # 第二次加载应该使用缓存
        result2 = self.config_loader.load_config("test")
        assert result1 == result2

        # 检查缓存
        if self.config_loader.enable_cache and self.config_loader._cache:
            # 使用缓存对象的方法检查
            cached_value = self.config_loader._cache.get("test")
            assert cached_value is not None

    def test_load_nonexistent_config(self):
        """测试加载不存在的配置"""
        result = self.config_loader.load_config("nonexistent")
        assert isinstance(result, dict)

    def test_load_strategy_config(self):
        """测试策略配置加载"""
        # 创建策略目录和文件
        strategy_dir = Path(self.temp_dir) / "strategies"
        strategy_dir.mkdir(exist_ok=True)

        strategy_data = {
            "strategy_info": {
                "name": "test_strategy",
                "version": "1.0.0"
            }
        }

        strategy_file = strategy_dir / "test_strategy.yaml"
        with open(strategy_file, 'w') as f:
            yaml.dump(strategy_data, f)

        result = self.config_loader.load_strategy_config("test_strategy")
        assert result == strategy_data

    def test_load_data_sources_config(self):
        """测试数据源配置加载"""
        # 创建数据源配置文件
        data_sources_data = {
            "eastmoney": {"enabled": True},
            "tushare": {"enabled": False}
        }

        data_sources_file = Path(self.temp_dir) / "data_sources.yaml"
        with open(data_sources_file, 'w') as f:
            yaml.dump(data_sources_data, f)

        result = self.config_loader.load_data_sources_config()
        assert result == data_sources_data

    def test_get_environment_config(self):
        """测试环境配置获取"""
        # 创建环境目录和文件
        env_dir = Path(self.temp_dir) / "environments"
        env_dir.mkdir(exist_ok=True)

        env_data = {
            "system": {
                "environment": "testing",
                "debug": False
            }
        }

        env_file = env_dir / "testing.yaml"
        with open(env_file, 'w') as f:
            yaml.dump(env_data, f)

        result = self.config_loader.get_environment_config("testing")
        assert result == env_data

    def test_list_available_strategies(self):
        """测试列出可用策略"""
        # 创建策略目录和文件
        strategy_dir = Path(self.temp_dir) / "strategies"
        strategy_dir.mkdir(exist_ok=True)

        # 创建几个策略文件
        (strategy_dir / "momentum.yaml").touch()
        (strategy_dir / "mean_reversion.yaml").touch()
        (strategy_dir / "default.yaml").touch()  # 应该被排除

        strategies = self.config_loader.list_available_strategies()
        assert "momentum" in strategies
        assert "mean_reversion" in strategies
        assert "default" not in strategies

    def test_list_available_environments(self):
        """测试列出可用环境"""
        # 创建环境目录和文件
        env_dir = Path(self.temp_dir) / "environments"
        env_dir.mkdir(exist_ok=True)

        (env_dir / "development.yaml").touch()
        (env_dir / "testing.yaml").touch()
        (env_dir / "production.yaml").touch()

        environments = self.config_loader.list_available_environments()
        assert "development" in environments
        assert "testing" in environments
        assert "production" in environments


class TestConfigValidator:
    """配置验证器测试"""

    def setup_method(self):
        """测试前设置"""
        self.validator = ConfigValidator()

    def test_validate_system_config_valid(self):
        """测试有效的系统配置验证"""
        valid_config = {
            "system": {
                "name": "Test System",
                "version": "1.0.0",
                "environment": "development"
            },
            "logging": {
                "level": "INFO",
                "max_file_size": 1024,
                "backup_count": 5
            },
            "database": {
                "type": "sqlite",
                "path": "/tmp/test.db"
            },
            "data_sources": {
                "eastmoney": {
                    "enabled": True,
                    "timeout": 10
                }
            }
        }

        result = self.validator.validate_system_config(valid_config)
        assert result is True
        assert len(self.validator.errors) == 0

    def test_validate_system_config_missing_sections(self):
        """测试缺少必需节的系统配置"""
        invalid_config = {
            "system": {
                "name": "Test System"
            }
        }

        result = self.validator.validate_system_config(invalid_config)
        assert result is False
        assert len(self.validator.errors) > 0

    def test_validate_strategy_config_valid(self):
        """测试有效的策略配置验证"""
        valid_strategy = {
            "strategy_info": {
                "name": "Test Strategy",
                "version": "1.0.0",
                "description": "Test description",
                "strategy_type": "momentum"
            },
            "selection_criteria": {
                "basic_criteria": {
                    "consecutive_days": 3,
                    "min_total_return": 0.15
                }
            }
        }

        result = self.validator.validate_strategy_config(valid_strategy)
        assert result is True
        assert len(self.validator.errors) == 0

    def test_validate_strategy_config_invalid_type(self):
        """测试无效策略类型"""
        invalid_strategy = {
            "strategy_info": {
                "name": "Test Strategy",
                "version": "1.0.0",
                "description": "Test description",
                "strategy_type": "invalid_type"
            },
            "selection_criteria": {}
        }

        result = self.validator.validate_strategy_config(invalid_strategy)
        assert result is False
        assert any("无效的策略类型" in error for error in self.validator.errors)

    def test_validate_data_sources_config(self):
        """测试数据源配置验证"""
        data_sources_config = {
            "priority": {
                "realtime_data": ["eastmoney", "tushare"]
            },
            "eastmoney": {
                "enabled": True,
                "timeout": 10,
                "retry_count": 3
            },
            "tushare": {
                "enabled": False,
                "timeout": 30,
                "retry_count": 2
            }
        }

        result = self.validator.validate_data_sources_config(
            data_sources_config)
        assert result is True
        assert len(self.validator.errors) == 0

    def test_get_validation_report(self):
        """测试获取验证报告"""
        # 添加一些错误和警告
        self.validator.errors.append("Test error")
        self.validator.warnings.append("Test warning")

        report = self.validator.get_validation_report()

        assert report['is_valid'] is False
        assert report['error_count'] == 1
        assert report['warning_count'] == 1
        assert "Test error" in report['errors']
        assert "Test warning" in report['warnings']


class TestConfigIntegration:
    """配置系统集成测试"""

    def test_config_loader_and_validator_integration(self):
        """测试配置加载器和验证器的集成"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建配置加载器
            loader = ConfigLoader(temp_dir)
            validator = ConfigValidator()

            # 创建有效的配置文件
            config_data = {
                "system": {
                    "name": "Integration Test",
                    "version": "1.0.0",
                    "environment": "testing"
                },
                "logging": {"level": "INFO"},
                "database": {"type": "sqlite"},
                "data_sources": {"eastmoney": {"enabled": True}}
            }

            config_file = Path(temp_dir) / "integration_test.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)

            # 加载配置
            loaded_config = loader.load_config("integration_test")

            # 验证配置
            is_valid = validator.validate_system_config(loaded_config)

            assert is_valid is True
            # 检查关键配置字段而不是完全相等
            assert loaded_config["system"]["name"] == "Integration Test"
            assert loaded_config["system"]["version"] == "1.0.0"
            # 检查日志级别存在（可能有默认值）
            assert "level" in loaded_config["logging"]
            assert loaded_config["database"]["type"] == "sqlite"
            assert loaded_config["data_sources"]["eastmoney"]["enabled"] is True
            assert len(validator.errors) == 0

# 测试夹具


@pytest.fixture
def sample_config():
    """示例配置夹具"""
    return {
        "system": {
            "name": "Test System",
            "version": "1.0.0",
            "environment": "testing"
        },
        "logging": {
            "level": "DEBUG",
            "console": True
        }
    }


@pytest.fixture
def sample_strategy_config():
    """示例策略配置夹具"""
    return {
        "strategy_info": {
            "name": "Test Strategy",
            "version": "1.0.0",
            "description": "Test strategy for unit testing",
            "strategy_type": "momentum"
        },
        "selection_criteria": {
            "basic_criteria": {
                "consecutive_days": 3,
                "min_total_return": 0.15,
                "max_drawdown": 0.05
            }
        }
    }


def test_config_with_fixtures(sample_config, sample_strategy_config):
    """使用夹具的配置测试"""
    validator = ConfigValidator()

    # 测试系统配置
    system_valid = validator.validate_system_config(sample_config)

    # 测试策略配置
    strategy_valid = validator.validate_strategy_config(sample_strategy_config)

    # 由于缺少必需的节，系统配置应该无效
    assert system_valid is False

    # 策略配置应该有效
    assert strategy_valid is True
