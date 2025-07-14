"""
配置系统集成测试

测试配置加载、验证、管理的完整流程
"""
from quant_system.utils.config_validator import ConfigValidator
from quant_system.utils.config_loader import ConfigLoader
import pytest
import tempfile
import yaml
from pathlib import Path

# 添加src目录到Python路径
import sys
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestConfigSystemIntegration:
    """配置系统集成测试"""

    def setup_method(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_loader = ConfigLoader(self.temp_dir)
        self.validator = ConfigValidator()

        # 创建测试配置目录结构
        (Path(self.temp_dir) / "environments").mkdir(exist_ok=True)
        (Path(self.temp_dir) / "strategies").mkdir(exist_ok=True)

    def test_complete_config_workflow(self):
        """测试完整的配置工作流程"""
        # 1. 创建默认配置
        default_config = {
            "system": {
                "name": "测试系统",
                "version": "1.0.0",
                "environment": "testing"
            },
            "logging": {
                "level": "INFO",
                "console": True
            },
            "database": {
                "type": "sqlite",
                "path": ":memory:"
            },
            "data_sources": {
                "eastmoney": {
                    "enabled": True,
                    "timeout": 10
                }
            }
        }

        default_file = Path(self.temp_dir) / "default.yaml"
        with open(default_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, allow_unicode=True)

        # 2. 创建环境配置
        env_config = {
            "system": {
                "name": "测试系统",
                "version": "1.0.0",
                "environment": "testing",
                "debug": True
            },
            "logging": {
                "level": "DEBUG"
            },
            "database": {
                "type": "sqlite",
                "path": ":memory:"
            },
            "data_sources": {
                "eastmoney": {
                    "enabled": True
                }
            }
        }

        env_file = Path(self.temp_dir) / "environments" / "testing.yaml"
        with open(env_file, 'w', encoding='utf-8') as f:
            yaml.dump(env_config, f, allow_unicode=True)

        # 3. 创建策略配置
        strategy_config = {
            "strategy_info": {
                "name": "测试策略",
                "version": "1.0.0",
                "description": "集成测试策略",
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

        strategy_file = Path(self.temp_dir) / \
            "strategies" / "test_strategy.yaml"
        with open(strategy_file, 'w', encoding='utf-8') as f:
            yaml.dump(strategy_config, f, allow_unicode=True)

        # 4. 测试配置加载
        loaded_default = self.config_loader.load_config("default")
        loaded_env = self.config_loader.get_environment_config("testing")
        loaded_strategy = self.config_loader.load_strategy_config(
            "test_strategy")

        # 验证加载结果
        assert loaded_default == default_config
        assert loaded_env == env_config
        assert loaded_strategy == strategy_config

        # 5. 测试配置验证
        default_valid = self.validator.validate_system_config(loaded_default)
        env_valid = self.validator.validate_system_config(loaded_env)
        strategy_valid = self.validator.validate_strategy_config(
            loaded_strategy)

        assert default_valid is True
        assert env_valid is True
        assert strategy_valid is True

        # 6. 测试配置列表功能
        strategies = self.config_loader.list_available_strategies()
        environments = self.config_loader.list_available_environments()

        assert "test_strategy" in strategies
        assert "testing" in environments

    def test_config_inheritance_and_override(self):
        """测试配置继承和覆盖"""
        # 创建基础配置
        base_config = {
            "system": {
                "name": "基础系统",
                "version": "1.0.0",
                "environment": "development"
            },
            "logging": {
                "level": "INFO",
                "console": True,
                "file": "base.log"
            },
            "database": {
                "type": "sqlite",
                "path": "base.db"
            },
            "data_sources": {
                "eastmoney": {
                    "enabled": True,
                    "timeout": 10
                }
            }
        }

        base_file = Path(self.temp_dir) / "base.yaml"
        with open(base_file, 'w', encoding='utf-8') as f:
            yaml.dump(base_config, f)

        # 创建覆盖配置
        override_config = {
            "system": {
                "name": "基础系统",
                "version": "1.0.0",
                "environment": "production",  # 覆盖环境
                "debug": False
            },
            "logging": {
                "level": "WARNING",  # 覆盖日志级别
                "file": "production.log"  # 覆盖日志文件
            },
            "database": {
                "type": "sqlite",
                "path": "production.db"  # 覆盖数据库路径
            },
            "data_sources": {
                "eastmoney": {
                    "enabled": True,
                    "timeout": 15  # 覆盖超时时间
                }
            }
        }

        override_file = Path(self.temp_dir) / \
            "environments" / "production.yaml"
        with open(override_file, 'w', encoding='utf-8') as f:
            yaml.dump(override_config, f)

        # 加载配置
        base_loaded = self.config_loader.load_config("base")
        override_loaded = self.config_loader.get_environment_config(
            "production")

        # 验证覆盖效果
        assert base_loaded["system"]["environment"] == "development"
        assert override_loaded["system"]["environment"] == "production"

        assert base_loaded["logging"]["level"] == "INFO"
        assert override_loaded["logging"]["level"] == "WARNING"

        assert base_loaded["data_sources"]["eastmoney"]["timeout"] == 10
        assert override_loaded["data_sources"]["eastmoney"]["timeout"] == 15

    def test_config_validation_with_errors(self):
        """测试配置验证错误处理"""
        # 创建有错误的配置
        invalid_config = {
            "system": {
                "name": "测试系统",
                # 缺少version和environment
            },
            "logging": {
                "level": "INVALID_LEVEL",  # 无效的日志级别
                "max_file_size": -1,       # 无效的文件大小
                "backup_count": -5         # 无效的备份数量
            },
            "database": {
                "type": "unsupported_db"   # 不支持的数据库类型
            },
            # 缺少data_sources节
        }

        invalid_file = Path(self.temp_dir) / "invalid.yaml"
        with open(invalid_file, 'w', encoding='utf-8') as f:
            yaml.dump(invalid_config, f)

        # 加载并验证配置
        loaded_config = self.config_loader.load_config("invalid")
        is_valid = self.validator.validate_system_config(loaded_config)

        # 应该验证失败
        assert is_valid is False
        assert len(self.validator.errors) > 0

        # 检查具体错误
        errors = self.validator.errors
        error_messages = ' '.join(errors)

        assert "version" in error_messages or "environment" in error_messages
        assert "无效的日志级别" in error_messages
        assert "数据源" in error_messages or "data_sources" in error_messages

    def test_config_caching_mechanism(self):
        """测试配置缓存机制"""
        # 创建测试配置
        test_config = {
            "test": {
                "value": "original"
            }
        }

        config_file = Path(self.temp_dir) / "cache_test.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)

        # 第一次加载
        config1 = self.config_loader.load_config("cache_test")
        assert config1["test"]["value"] == "original"

        # 修改文件内容
        modified_config = {
            "test": {
                "value": "modified"
            }
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(modified_config, f)

        # 第二次加载（应该使用缓存）
        config2 = self.config_loader.load_config("cache_test")
        assert config2["test"]["value"] == "original"  # 仍然是缓存的值

        # 禁用缓存重新加载
        config3 = self.config_loader.load_config("cache_test", use_cache=False)
        assert config3["test"]["value"] == "modified"  # 新的值

    def test_strategy_config_validation_workflow(self):
        """测试策略配置验证工作流程"""
        # 创建完整的策略配置
        complete_strategy = {
            "strategy_info": {
                "name": "完整策略",
                "version": "2.0.0",
                "description": "完整的策略配置示例",
                "author": "测试作者",
                "created_date": "2024-01-01",
                "strategy_type": "momentum"
            },
            "selection_criteria": {
                "basic_criteria": {
                    "consecutive_days": 5,
                    "min_total_return": 0.20,
                    "max_drawdown": 0.03,
                    "exclude_limit_up_first_day": True
                },
                "price_filters": {
                    "min_stock_price": 8.0,
                    "max_stock_price": 150.0,
                    "min_market_cap": 5000000000,
                    "max_market_cap": 200000000000
                },
                "volume_filters": {
                    "min_avg_volume": 20000000,
                    "min_turnover_rate": 0.02,
                    "max_turnover_rate": 0.15
                }
            },
            "trading_rules": {
                "buy_rules": [
                    {
                        "name": "动量确认",
                        "description": "确认动量信号",
                        "condition": "momentum_confirmed",
                        "priority": 1,
                        "enabled": True
                    }
                ],
                "sell_rules": [
                    {
                        "name": "止盈",
                        "description": "达到止盈目标",
                        "condition": "profit_target_reached",
                        "priority": 1,
                        "enabled": True
                    }
                ],
                "risk_rules": [
                    {
                        "name": "仓位限制",
                        "description": "单只股票仓位限制",
                        "condition": "position_limit_check",
                        "priority": 1,
                        "enabled": True
                    }
                ]
            },
            "position_management": {
                "allocation_method": "equal_weight",
                "base_position_size": 0.20,
                "max_position_size": 0.25,
                "min_position_size": 0.05
            },
            "risk_management": {
                "stop_loss": {
                    "method": "percentage",
                    "percentage": 0.05,
                    "trailing_stop": True
                },
                "take_profit": {
                    "method": "percentage",
                    "percentage": 0.25
                }
            }
        }

        strategy_file = Path(self.temp_dir) / \
            "strategies" / "complete_strategy.yaml"
        with open(strategy_file, 'w', encoding='utf-8') as f:
            yaml.dump(complete_strategy, f, allow_unicode=True)

        # 加载并验证策略配置
        loaded_strategy = self.config_loader.load_strategy_config(
            "complete_strategy")
        is_valid = self.validator.validate_strategy_config(loaded_strategy)

        # 验证应该通过
        assert is_valid is True
        assert len(self.validator.errors) == 0

        # 验证配置内容
        assert loaded_strategy["strategy_info"]["name"] == "完整策略"
        assert loaded_strategy["strategy_info"]["strategy_type"] == "momentum"
        assert loaded_strategy["selection_criteria"]["basic_criteria"]["consecutive_days"] == 5
        assert len(loaded_strategy["trading_rules"]["buy_rules"]) == 1
        assert len(loaded_strategy["trading_rules"]["sell_rules"]) == 1
        assert len(loaded_strategy["trading_rules"]["risk_rules"]) == 1

    def test_multi_environment_config_loading(self):
        """测试多环境配置加载"""
        environments = ["development", "testing", "production"]

        for env in environments:
            env_config = {
                "system": {
                    "name": "多环境系统",
                    "version": "1.0.0",
                    "environment": env,
                    "debug": env != "production"
                },
                "logging": {
                    "level": "DEBUG" if env == "development" else "INFO",
                    "console": env != "production"
                },
                "database": {
                    "type": "sqlite",
                    "path": f"{env}.db"
                },
                "data_sources": {
                    "eastmoney": {
                        "enabled": True,
                        "timeout": 5 if env == "development" else 10
                    }
                }
            }

            env_file = Path(self.temp_dir) / "environments" / f"{env}.yaml"
            with open(env_file, 'w', encoding='utf-8') as f:
                yaml.dump(env_config, f)

        # 测试加载所有环境配置
        for env in environments:
            loaded_config = self.config_loader.get_environment_config(env)

            # 验证环境特定设置
            assert loaded_config["system"]["environment"] == env
            assert loaded_config["database"]["path"] == f"{env}.db"

            if env == "development":
                assert loaded_config["logging"]["level"] == "DEBUG"
                assert loaded_config["data_sources"]["eastmoney"]["timeout"] == 5
            elif env == "production":
                assert loaded_config["logging"]["console"] is False
                assert loaded_config["system"]["debug"] is False

            # 验证配置有效性
            is_valid = self.validator.validate_system_config(loaded_config)
            assert is_valid is True

        # 测试环境列表功能
        available_envs = self.config_loader.list_available_environments()
        for env in environments:
            assert env in available_envs

# 测试夹具


@pytest.fixture
def config_system():
    """配置系统夹具"""
    temp_dir = tempfile.mkdtemp()
    config_loader = ConfigLoader(temp_dir)
    validator = ConfigValidator()

    # 创建目录结构
    (Path(temp_dir) / "environments").mkdir(exist_ok=True)
    (Path(temp_dir) / "strategies").mkdir(exist_ok=True)

    return {
        'temp_dir': temp_dir,
        'config_loader': config_loader,
        'validator': validator
    }


@pytest.fixture
def sample_system_config():
    """示例系统配置夹具"""
    return {
        "system": {
            "name": "夹具测试系统",
            "version": "1.0.0",
            "environment": "testing"
        },
        "logging": {
            "level": "INFO",
            "console": True
        },
        "database": {
            "type": "sqlite",
            "path": ":memory:"
        },
        "data_sources": {
            "eastmoney": {
                "enabled": True,
                "timeout": 10
            }
        }
    }


def test_config_system_with_fixtures(config_system, sample_system_config):
    """使用夹具的配置系统测试"""
    config_loader = config_system['config_loader']
    validator = config_system['validator']
    temp_dir = config_system['temp_dir']

    # 保存配置到文件
    config_file = Path(temp_dir) / "fixture_test.yaml"
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(sample_system_config, f)

    # 加载并验证配置
    loaded_config = config_loader.load_config("fixture_test")
    is_valid = validator.validate_system_config(loaded_config)

    assert loaded_config == sample_system_config
    assert is_valid is True
    assert len(validator.errors) == 0
