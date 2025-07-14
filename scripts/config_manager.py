#!/usr/bin/env python3
"""
配置管理工具

提供配置文件的管理、验证和操作功能
"""

import sys
import argparse
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from quant_system.utils.config_loader import ConfigLoader
from quant_system.utils.config_validator import ConfigValidator, validate_config_file

def list_configs():
    """列出所有可用的配置"""
    print("📋 可用配置列表")
    print("=" * 50)
    
    config_loader = ConfigLoader()
    
    # 列出环境配置
    environments = config_loader.list_available_environments()
    print(f"\n🌍 环境配置 ({len(environments)}个):")
    for env in environments:
        print(f"  - {env}")
    
    # 列出策略配置
    strategies = config_loader.list_available_strategies()
    print(f"\n📈 策略配置 ({len(strategies)}个):")
    for strategy in strategies:
        print(f"  - {strategy}")
    
    # 检查其他配置文件
    config_dir = Path("config")
    other_configs = []
    
    if (config_dir / "default.yaml").exists():
        other_configs.append("default.yaml")
    if (config_dir / "data_sources.yaml").exists():
        other_configs.append("data_sources.yaml")
    
    if other_configs:
        print(f"\n⚙️ 其他配置 ({len(other_configs)}个):")
        for config in other_configs:
            print(f"  - {config}")

def validate_configs():
    """验证所有配置文件"""
    print("🔍 配置验证")
    print("=" * 50)
    
    config_dir = Path("config")
    validator = ConfigValidator()
    
    validation_results = []
    
    # 验证默认配置
    default_config = config_dir / "default.yaml"
    if default_config.exists():
        print(f"\n验证默认配置: {default_config}")
        result = validate_config_file(str(default_config), 'system')
        validation_results.append(("default.yaml", result))
    
    # 验证环境配置
    env_dir = config_dir / "environments"
    if env_dir.exists():
        for env_file in env_dir.glob("*.yaml"):
            print(f"\n验证环境配置: {env_file}")
            result = validate_config_file(str(env_file), 'system')
            validation_results.append((f"environments/{env_file.name}", result))
    
    # 验证策略配置
    strategy_dir = config_dir / "strategies"
    if strategy_dir.exists():
        for strategy_file in strategy_dir.glob("*.yaml"):
            print(f"\n验证策略配置: {strategy_file}")
            result = validate_config_file(str(strategy_file), 'strategy')
            validation_results.append((f"strategies/{strategy_file.name}", result))
    
    # 验证数据源配置
    data_sources_config = config_dir / "data_sources.yaml"
    if data_sources_config.exists():
        print(f"\n验证数据源配置: {data_sources_config}")
        result = validate_config_file(str(data_sources_config), 'data_sources')
        validation_results.append(("data_sources.yaml", result))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("验证结果汇总")
    print("=" * 50)
    
    passed = 0
    total = len(validation_results)
    
    for config_name, result in validation_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{config_name:30}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个配置文件验证通过")
    
    if passed == total:
        print("🎉 所有配置文件验证通过！")
        return True
    else:
        print("⚠️ 部分配置文件验证失败，请检查错误信息")
        return False

def show_config(config_name: str, config_type: str = "auto"):
    """显示配置内容"""
    print(f"📄 配置内容: {config_name}")
    print("=" * 50)
    
    config_loader = ConfigLoader()
    
    try:
        if config_type == "auto":
            # 自动判断配置类型
            if config_name in config_loader.list_available_strategies():
                config = config_loader.load_strategy_config(config_name)
            elif config_name in config_loader.list_available_environments():
                config = config_loader.get_environment_config(config_name)
            elif config_name == "data_sources":
                config = config_loader.load_data_sources_config()
            else:
                config = config_loader.load_config(config_name)
        elif config_type == "strategy":
            config = config_loader.load_strategy_config(config_name)
        elif config_type == "environment":
            config = config_loader.get_environment_config(config_name)
        elif config_type == "data_sources":
            config = config_loader.load_data_sources_config()
        else:
            config = config_loader.load_config(config_name)
        
        if config:
            import yaml
            print(yaml.dump(config, default_flow_style=False, allow_unicode=True))
        else:
            print(f"❌ 配置 {config_name} 不存在或为空")
            
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")

def test_config_loading():
    """测试配置加载功能"""
    print("🧪 配置加载测试")
    print("=" * 50)
    
    config_loader = ConfigLoader()
    
    tests = [
        ("默认配置", lambda: config_loader.load_config("default")),
        ("开发环境配置", lambda: config_loader.get_environment_config("development")),
        ("数据源配置", lambda: config_loader.load_data_sources_config()),
        ("策略列表", lambda: config_loader.list_available_strategies()),
        ("环境列表", lambda: config_loader.list_available_environments()),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name}: 成功")
                results.append((test_name, True))
            else:
                print(f"⚠️ {test_name}: 空结果")
                results.append((test_name, False))
        except Exception as e:
            print(f"❌ {test_name}: 失败 - {e}")
            results.append((test_name, False))
    
    # 汇总结果
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    return passed == total

def create_sample_strategy():
    """创建示例策略配置"""
    print("📝 创建示例策略配置")
    print("=" * 50)
    
    strategy_name = input("请输入策略名称: ").strip()
    if not strategy_name:
        print("❌ 策略名称不能为空")
        return
    
    strategy_dir = Path("config/strategies")
    strategy_dir.mkdir(parents=True, exist_ok=True)
    
    strategy_file = strategy_dir / f"{strategy_name}.yaml"
    
    if strategy_file.exists():
        overwrite = input(f"策略配置 {strategy_name} 已存在，是否覆盖？(y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ 操作已取消")
            return
    
    # 创建基础策略配置模板
    sample_config = f"""# {strategy_name} 策略配置
# 自动生成的策略配置模板

# 策略基本信息
strategy_info:
  name: "{strategy_name}"
  version: "1.0.0"
  description: "{strategy_name}策略描述"
  author: "量化投资系统"
  created_date: "2024-01-01"
  strategy_type: "custom"

# 选股条件
selection_criteria:
  basic_criteria:
    consecutive_days: 3
    min_total_return: 0.15
    max_drawdown: 0.05
    exclude_limit_up_first_day: true
    
  price_filters:
    min_stock_price: 5.0
    max_stock_price: 200.0
    min_market_cap: 1000000000
    max_market_cap: 500000000000
    
  volume_filters:
    min_avg_volume: 10000000
    min_turnover_rate: 0.01
    max_turnover_rate: 0.20

# 交易规则
trading_rules:
  buy_rules:
    - name: "基础买入条件"
      description: "满足基本选股条件"
      condition: "meets_selection_criteria"
      priority: 1
      enabled: true
      
  sell_rules:
    - name: "止盈"
      description: "达到止盈目标"
      condition: "profit_pct >= 0.20"
      priority: 1
      enabled: true
      
    - name: "止损"
      description: "达到止损线"
      condition: "loss_pct >= 0.05"
      priority: 1
      enabled: true

# 风险管理
risk_management:
  stop_loss:
    method: "percentage"
    percentage: 0.05
    trailing_stop: false
    
  take_profit:
    method: "percentage"
    percentage: 0.20

# 回测参数
backtest_params:
  start_date: "2023-01-01"
  end_date: "2024-01-01"
  initial_capital: 1000000
  max_positions: 5
"""
    
    try:
        with open(strategy_file, 'w', encoding='utf-8') as f:
            f.write(sample_config)
        
        print(f"✅ 策略配置已创建: {strategy_file}")
        print(f"📝 请编辑 {strategy_file} 来自定义策略参数")
        
        # 验证创建的配置
        print("\n🔍 验证创建的配置...")
        result = validate_config_file(str(strategy_file), 'strategy')
        
        if result:
            print("✅ 配置验证通过")
        else:
            print("⚠️ 配置验证有问题，请检查并修正")
            
    except Exception as e:
        print(f"❌ 创建策略配置失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="量化投资系统配置管理工具")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出配置命令
    subparsers.add_parser('list', help='列出所有可用配置')
    
    # 验证配置命令
    subparsers.add_parser('validate', help='验证所有配置文件')
    
    # 显示配置命令
    show_parser = subparsers.add_parser('show', help='显示配置内容')
    show_parser.add_argument('name', help='配置名称')
    show_parser.add_argument('--type', choices=['auto', 'strategy', 'environment', 'data_sources'], 
                           default='auto', help='配置类型')
    
    # 测试配置命令
    subparsers.add_parser('test', help='测试配置加载功能')
    
    # 创建示例策略命令
    subparsers.add_parser('create-strategy', help='创建示例策略配置')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_configs()
    elif args.command == 'validate':
        success = validate_configs()
        sys.exit(0 if success else 1)
    elif args.command == 'show':
        show_config(args.name, args.type)
    elif args.command == 'test':
        success = test_config_loading()
        sys.exit(0 if success else 1)
    elif args.command == 'create-strategy':
        create_sample_strategy()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
