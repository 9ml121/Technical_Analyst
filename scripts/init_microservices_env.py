#!/usr/bin/env python3
"""
微服务项目初始化脚本
运行此脚本来快速设置开发环境
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """运行命令并显示进度"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 开始初始化微服务项目...")
    
    # 检查Docker
    if not run_command("docker --version", "检查Docker"):
        print("请先安装Docker")
        return
    
    # 复制环境配置
    if Path(".env").exists():
        print("✅ .env文件已存在")
    else:
        run_command("cp .env.example .env", "复制环境配置文件")
    
    # 启动基础服务（数据库等）
    run_command("make dev-up", "启动开发环境基础服务")
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    import time
    time.sleep(10)
    
    print("🎉 微服务项目初始化完成！")
    print("📝 下一步操作：")
    print("  1. 检查 .env 文件配置")
    print("  2. 运行 'make up' 启动所有服务")
    print("  3. 访问 http://localhost:8000 查看API网关")


if __name__ == "__main__":
    main()
