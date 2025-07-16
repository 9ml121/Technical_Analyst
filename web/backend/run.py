#!/usr/bin/env python3
"""
Technical_Analyst Web Backend 启动脚本
"""

import uvicorn
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 启动Technical_Analyst Web Backend...")
    print("📍 API文档地址: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/health")

    # 开发环境配置
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下启用热重载
        log_level="info",
        access_log=True
    )
