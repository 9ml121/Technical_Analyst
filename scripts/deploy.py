#!/usr/bin/env python3
"""
部署脚本

自动化部署量化投资系统
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
import yaml
import json

class DeploymentManager:
    """部署管理器"""
    
    def __init__(self, target_env='production'):
        self.target_env = target_env
        self.project_root = Path(__file__).parent.parent
        self.deploy_dir = Path.home() / "quant_system_deploy"
        self.backup_dir = Path.home() / "quant_system_backup"
        
    def deploy(self):
        """执行部署"""
        print(f"🚀 开始部署量化投资系统到 {self.target_env} 环境")
        print("=" * 60)
        
        try:
            # 1. 预检查
            self.pre_deployment_checks()
            
            # 2. 创建备份
            self.create_backup()
            
            # 3. 准备部署目录
            self.prepare_deployment_directory()
            
            # 4. 复制文件
            self.copy_files()
            
            # 5. 安装依赖
            self.install_dependencies()
            
            # 6. 配置环境
            self.configure_environment()
            
            # 7. 运行测试
            self.run_deployment_tests()
            
            # 8. 启动服务
            self.start_services()
            
            # 9. 验证部署
            self.verify_deployment()
            
            print("\n🎉 部署成功完成！")
            self.print_deployment_info()
            
        except Exception as e:
            print(f"\n❌ 部署失败: {e}")
            self.rollback()
            sys.exit(1)
    
    def pre_deployment_checks(self):
        """部署前检查"""
        print("\n🔍 执行部署前检查...")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version < (3, 8):
            raise RuntimeError(f"需要Python 3.8+，当前版本: {python_version.major}.{python_version.minor}")
        print(f"  ✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查必需文件
        required_files = [
            'src/quant_system/__init__.py',
            'config/default.yaml',
            'requirements.txt'
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                raise FileNotFoundError(f"缺少必需文件: {file_path}")
        print("  ✅ 必需文件检查通过")
        
        # 检查磁盘空间
        disk_usage = shutil.disk_usage(Path.home())
        free_gb = disk_usage.free / (1024**3)
        if free_gb < 1.0:
            raise RuntimeError(f"磁盘空间不足，需要至少1GB，当前可用: {free_gb:.1f}GB")
        print(f"  ✅ 磁盘空间: {free_gb:.1f}GB 可用")
        
        # 检查网络连接
        try:
            import urllib.request
            urllib.request.urlopen('https://pypi.org', timeout=10)
            print("  ✅ 网络连接正常")
        except:
            print("  ⚠️ 网络连接检查失败，可能影响依赖安装")
    
    def create_backup(self):
        """创建备份"""
        print("\n💾 创建备份...")
        
        if self.deploy_dir.exists():
            # 创建备份目录
            self.backup_dir.mkdir(exist_ok=True)
            
            # 生成备份名称
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"quant_system_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            # 复制现有部署
            shutil.copytree(self.deploy_dir, backup_path)
            print(f"  ✅ 备份已创建: {backup_path}")
            
            # 保留最近5个备份
            self.cleanup_old_backups()
        else:
            print("  ℹ️ 首次部署，无需备份")
    
    def cleanup_old_backups(self):
        """清理旧备份"""
        if not self.backup_dir.exists():
            return
        
        backups = sorted([d for d in self.backup_dir.iterdir() if d.is_dir()], 
                        key=lambda x: x.stat().st_mtime, reverse=True)
        
        # 保留最近5个备份
        for old_backup in backups[5:]:
            shutil.rmtree(old_backup)
            print(f"  🗑️ 删除旧备份: {old_backup.name}")
    
    def prepare_deployment_directory(self):
        """准备部署目录"""
        print("\n📁 准备部署目录...")
        
        # 删除现有部署目录
        if self.deploy_dir.exists():
            shutil.rmtree(self.deploy_dir)
        
        # 创建新的部署目录
        self.deploy_dir.mkdir(parents=True)
        
        # 创建子目录
        subdirs = ['src', 'config', 'logs', 'data', 'results', 'scripts']
        for subdir in subdirs:
            (self.deploy_dir / subdir).mkdir()
        
        print(f"  ✅ 部署目录已准备: {self.deploy_dir}")
    
    def copy_files(self):
        """复制文件"""
        print("\n📋 复制项目文件...")
        
        # 定义要复制的文件和目录
        copy_items = [
            ('src', 'src'),
            ('config', 'config'),
            ('scripts', 'scripts'),
            ('requirements.txt', 'requirements.txt'),
            ('README.md', 'README.md')
        ]
        
        for src_item, dst_item in copy_items:
            src_path = self.project_root / src_item
            dst_path = self.deploy_dir / dst_item
            
            if src_path.is_file():
                shutil.copy2(src_path, dst_path)
                print(f"  📄 复制文件: {src_item}")
            elif src_path.is_dir():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                print(f"  📁 复制目录: {src_item}")
            else:
                print(f"  ⚠️ 跳过不存在的项目: {src_item}")
        
        # 复制文档（如果存在）
        docs_src = self.project_root / "docs"
        if docs_src.exists():
            docs_dst = self.deploy_dir / "docs"
            shutil.copytree(docs_src, docs_dst)
            print("  📚 复制文档目录")
    
    def install_dependencies(self):
        """安装依赖"""
        print("\n📦 安装Python依赖...")
        
        requirements_file = self.deploy_dir / "requirements.txt"
        if not requirements_file.exists():
            print("  ⚠️ requirements.txt 不存在，跳过依赖安装")
            return
        
        # 创建虚拟环境
        venv_path = self.deploy_dir / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("  ✅ 虚拟环境已创建")
        
        # 确定pip路径
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"
        
        # 升级pip
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # 安装依赖
        subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
        print("  ✅ 依赖安装完成")
    
    def configure_environment(self):
        """配置环境"""
        print("\n⚙️ 配置环境...")
        
        # 设置环境变量
        env_file = self.deploy_dir / ".env"
        env_config = {
            'ENVIRONMENT': self.target_env,
            'PYTHONPATH': str(self.deploy_dir / "src"),
            'QUANT_SYSTEM_HOME': str(self.deploy_dir),
            'QUANT_SYSTEM_CONFIG': str(self.deploy_dir / "config"),
            'QUANT_SYSTEM_DATA': str(self.deploy_dir / "data"),
            'QUANT_SYSTEM_LOGS': str(self.deploy_dir / "logs"),
            'QUANT_SYSTEM_RESULTS': str(self.deploy_dir / "results")
        }
        
        with open(env_file, 'w') as f:
            for key, value in env_config.items():
                f.write(f"{key}={value}\n")
        
        print("  ✅ 环境变量配置完成")
        
        # 创建环境特定的配置文件
        self.create_environment_config()
        
        # 设置日志配置
        self.setup_logging()
    
    def create_environment_config(self):
        """创建环境特定配置"""
        env_config_dir = self.deploy_dir / "config" / "environments"
        env_config_dir.mkdir(exist_ok=True)
        
        env_config = {
            'system': {
                'environment': self.target_env,
                'debug': self.target_env != 'production',
                'log_level': 'INFO' if self.target_env == 'production' else 'DEBUG'
            },
            'database': {
                'host': 'localhost',
                'port': 3306,
                'name': f'quant_system_{self.target_env}',
                'pool_size': 10 if self.target_env == 'production' else 5
            },
            'cache': {
                'enabled': True,
                'ttl': 3600 if self.target_env == 'production' else 300,
                'max_size': 10000 if self.target_env == 'production' else 1000
            },
            'performance': {
                'monitoring': True,
                'parallel_processing': True,
                'max_workers': 8 if self.target_env == 'production' else 4
            }
        }
        
        env_config_file = env_config_dir / f"{self.target_env}.yaml"
        with open(env_config_file, 'w') as f:
            yaml.dump(env_config, f, default_flow_style=False)
        
        print(f"  ✅ {self.target_env} 环境配置已创建")
    
    def setup_logging(self):
        """设置日志配置"""
        log_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                }
            },
            'handlers': {
                'file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': str(self.deploy_dir / 'logs' / 'quant_system.log'),
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'formatter': 'standard'
                },
                'console': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['file', 'console'],
                    'level': 'INFO',
                    'propagate': False
                }
            }
        }
        
        log_config_file = self.deploy_dir / "config" / "logging.yaml"
        with open(log_config_file, 'w') as f:
            yaml.dump(log_config, f, default_flow_style=False)
        
        print("  ✅ 日志配置已设置")
    
    def run_deployment_tests(self):
        """运行部署测试"""
        print("\n🧪 运行部署测试...")
        
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.deploy_dir / "src")
        env['ENVIRONMENT'] = self.target_env
        
        # 运行基本导入测试
        test_script = f"""
import sys
sys.path.insert(0, '{self.deploy_dir / "src"}')

try:
    from quant_system.utils.config_loader import ConfigLoader
    from quant_system.utils.logger import get_logger
    from quant_system.utils.cache import cache_manager
    print("✅ 核心模块导入成功")
    
    # 测试配置加载
    config_loader = ConfigLoader('{self.deploy_dir / "config"}')
    config = config_loader.load_config('default')
    print("✅ 配置加载成功")
    
    # 测试日志
    logger = get_logger('deployment_test')
    logger.info('部署测试日志')
    print("✅ 日志系统正常")
    
    print("🎉 部署测试全部通过")
    
except Exception as e:
    print(f"❌ 部署测试失败: {{e}}")
    sys.exit(1)
"""
        
        # 确定Python路径
        venv_path = self.deploy_dir / "venv"
        if os.name == 'nt':  # Windows
            python_path = venv_path / "Scripts" / "python"
        else:  # Unix/Linux/macOS
            python_path = venv_path / "bin" / "python"
        
        # 运行测试
        result = subprocess.run([str(python_path), "-c", test_script], 
                              env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ 部署测试通过")
            print(result.stdout)
        else:
            print("  ❌ 部署测试失败")
            print(result.stderr)
            raise RuntimeError("部署测试失败")
    
    def start_services(self):
        """启动服务"""
        print("\n🚀 启动服务...")
        
        # 创建启动脚本
        self.create_startup_scripts()
        
        # 这里可以添加实际的服务启动逻辑
        # 例如：启动Web服务、数据服务等
        
        print("  ✅ 服务启动脚本已创建")
        print("  ℹ️ 请根据需要手动启动相关服务")
    
    def create_startup_scripts(self):
        """创建启动脚本"""
        # Unix/Linux启动脚本
        startup_script = f"""#!/bin/bash
# 量化投资系统启动脚本

export ENVIRONMENT={self.target_env}
export PYTHONPATH={self.deploy_dir}/src
export QUANT_SYSTEM_HOME={self.deploy_dir}

cd {self.deploy_dir}

# 激活虚拟环境
source venv/bin/activate

# 启动系统
echo "启动量化投资系统..."
python -c "
import sys
sys.path.insert(0, 'src')
from quant_system.utils.logger import get_logger
logger = get_logger('system')
logger.info('量化投资系统启动')
print('系统启动成功')
"

echo "系统运行中..."
"""
        
        script_path = self.deploy_dir / "start.sh"
        with open(script_path, 'w') as f:
            f.write(startup_script)
        
        # 设置执行权限
        os.chmod(script_path, 0o755)
        
        # Windows启动脚本
        windows_script = f"""@echo off
REM 量化投资系统启动脚本

set ENVIRONMENT={self.target_env}
set PYTHONPATH={self.deploy_dir}\\src
set QUANT_SYSTEM_HOME={self.deploy_dir}

cd /d {self.deploy_dir}

REM 激活虚拟环境
call venv\\Scripts\\activate.bat

REM 启动系统
echo 启动量化投资系统...
python -c "import sys; sys.path.insert(0, 'src'); from quant_system.utils.logger import get_logger; logger = get_logger('system'); logger.info('量化投资系统启动'); print('系统启动成功')"

echo 系统运行中...
pause
"""
        
        windows_script_path = self.deploy_dir / "start.bat"
        with open(windows_script_path, 'w') as f:
            f.write(windows_script)
    
    def verify_deployment(self):
        """验证部署"""
        print("\n✅ 验证部署...")
        
        # 检查关键文件
        key_files = [
            'src/quant_system/__init__.py',
            'config/default.yaml',
            'venv',
            '.env',
            'start.sh'
        ]
        
        for file_path in key_files:
            full_path = self.deploy_dir / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path} 缺失")
                raise FileNotFoundError(f"关键文件缺失: {file_path}")
        
        print("  ✅ 部署验证通过")
    
    def rollback(self):
        """回滚部署"""
        print("\n🔄 执行回滚...")
        
        if not self.backup_dir.exists():
            print("  ⚠️ 没有可用的备份，无法回滚")
            return
        
        # 找到最新的备份
        backups = sorted([d for d in self.backup_dir.iterdir() if d.is_dir()], 
                        key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not backups:
            print("  ⚠️ 没有找到备份文件")
            return
        
        latest_backup = backups[0]
        
        # 删除当前部署
        if self.deploy_dir.exists():
            shutil.rmtree(self.deploy_dir)
        
        # 恢复备份
        shutil.copytree(latest_backup, self.deploy_dir)
        print(f"  ✅ 已从备份恢复: {latest_backup.name}")
    
    def print_deployment_info(self):
        """打印部署信息"""
        print("\n📋 部署信息:")
        print(f"  部署目录: {self.deploy_dir}")
        print(f"  环境: {self.target_env}")
        print(f"  Python版本: {sys.version_info.major}.{sys.version_info.minor}")
        
        print("\n🚀 启动命令:")
        print(f"  Unix/Linux: cd {self.deploy_dir} && ./start.sh")
        print(f"  Windows: cd {self.deploy_dir} && start.bat")
        
        print("\n📁 重要目录:")
        print(f"  配置文件: {self.deploy_dir}/config")
        print(f"  日志文件: {self.deploy_dir}/logs")
        print(f"  数据目录: {self.deploy_dir}/data")
        print(f"  结果目录: {self.deploy_dir}/results")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='量化投资系统部署脚本')
    parser.add_argument('--env', choices=['development', 'testing', 'production'], 
                       default='production', help='目标环境')
    parser.add_argument('--rollback', action='store_true', help='回滚到上一个版本')
    
    args = parser.parse_args()
    
    manager = DeploymentManager(args.env)
    
    if args.rollback:
        manager.rollback()
    else:
        manager.deploy()

if __name__ == "__main__":
    main()
