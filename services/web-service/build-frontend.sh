#!/bin/bash

# Web Service 前端构建脚本

echo "🚀 开始构建前端..."

# 进入前端目录
cd frontend

# 安装依赖
echo "📦 安装前端依赖..."
npm install

# 构建生产版本
echo "🔨 构建前端应用..."
npm run build

echo "✅ 前端构建完成！"
echo "📁 构建文件位于: frontend/dist/" 