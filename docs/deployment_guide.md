# 量化投资系统部署指南

本指南详细介绍如何在不同环境中部署量化投资系统。

## 📋 部署前准备

### 系统要求

**最低配置:**
- CPU: 2核心
- 内存: 4GB RAM
- 磁盘: 10GB 可用空间
- 操作系统: Linux/macOS/Windows
- Python: 3.8+

**推荐配置:**
- CPU: 4核心以上
- 内存: 8GB RAM以上
- 磁盘: 50GB 可用空间 (SSD推荐)
- 操作系统: Linux (Ubuntu 20.04+ / CentOS 8+)
- Python: 3.9+

### 依赖检查

```bash
# 检查Python版本
python --version

# 检查pip
pip --version

# 检查git
git --version

# 检查磁盘空间
df -h

# 检查内存
free -h
```

## 🚀 自动化部署

### 使用部署脚本

```bash
# 克隆项目
git clone <repository-url>
cd quantitative-investment-system

# 运行自动化部署
python scripts/deploy.py --env production

# 或者部署到测试环境
python scripts/deploy.py --env testing
```

### 部署选项

```bash
# 查看帮助
python scripts/deploy.py --help

# 部署到指定环境
python scripts/deploy.py --env [development|testing|production]

# 回滚到上一个版本
python scripts/deploy.py --rollback
```

## 🔧 手动部署

### 1. 环境准备

```bash
# 创建部署目录
mkdir -p ~/quant_system_deploy
cd ~/quant_system_deploy

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 升级pip
pip install --upgrade pip
```

### 2. 代码部署

```bash
# 复制源代码
cp -r /path/to/source/src ./
cp -r /path/to/source/config ./
cp -r /path/to/source/scripts ./
cp /path/to/source/requirements.txt ./

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置设置

```bash
# 创建环境配置文件
mkdir -p config/environments

# 复制配置模板
cp config/environments/production.yaml.template config/environments/production.yaml

# 编辑配置文件
vim config/environments/production.yaml
```

### 4. 环境变量

创建 `.env` 文件：

```bash
# 系统环境
ENVIRONMENT=production
PYTHONPATH=/path/to/deploy/src

# 系统路径
QUANT_SYSTEM_HOME=/path/to/deploy
QUANT_SYSTEM_CONFIG=/path/to/deploy/config
QUANT_SYSTEM_DATA=/path/to/deploy/data
QUANT_SYSTEM_LOGS=/path/to/deploy/logs
QUANT_SYSTEM_RESULTS=/path/to/deploy/results
```

### 5. 目录结构

```bash
# 创建必要目录
mkdir -p data logs results

# 设置权限
chmod 755 scripts/*.py
chmod 644 config/*.yaml
```

## 🐳 Docker部署

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# 创建必要目录
RUN mkdir -p data logs results

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV QUANT_SYSTEM_HOME=/app

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-c", "print('量化投资系统启动')"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  quant-system:
    build: .
    container_name: quant_system
    environment:
      - ENVIRONMENT=production
      - PYTHONPATH=/app/src
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./results:/app/results
      - ./config:/app/config
    ports:
      - "8000:8000"
    restart: unless-stopped
    
  redis:
    image: redis:alpine
    container_name: quant_redis
    ports:
      - "6379:6379"
    restart: unless-stopped
    
  mysql:
    image: mysql:8.0
    container_name: quant_mysql
    environment:
      MYSQL_ROOT_PASSWORD: your_password
      MYSQL_DATABASE: quant_system
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  mysql_data:
```

### Docker部署命令

```bash
# 构建镜像
docker build -t quant-system .

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f quant-system

# 停止服务
docker-compose down
```

## ☁️ 云平台部署

### AWS部署

```bash
# 安装AWS CLI
pip install awscli

# 配置AWS凭证
aws configure

# 创建EC2实例
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --count 1 \
    --instance-type t3.medium \
    --key-name my-key-pair \
    --security-groups my-security-group

# 部署到EC2
scp -i my-key.pem deploy.py ec2-user@instance-ip:~/
ssh -i my-key.pem ec2-user@instance-ip
python deploy.py --env production
```

### 阿里云部署

```bash
# 安装阿里云CLI
pip install aliyun-python-sdk-ecs

# 创建ECS实例
aliyun ecs CreateInstance \
    --RegionId cn-hangzhou \
    --ImageId ubuntu_20_04_x64_20G_alibase_20210420.vhd \
    --InstanceType ecs.t6-c1m1.large \
    --SecurityGroupId sg-bp1234567890abcdef \
    --VSwitchId vsw-bp1234567890abcdef

# 部署应用
# (类似AWS部署流程)
```

## 🔧 配置管理

### 环境配置

**开发环境 (development.yaml):**
```yaml
system:
  debug: true
  log_level: DEBUG
  
database:
  host: localhost
  port: 3306
  name: quant_dev
  
cache:
  ttl: 60
  max_size: 100
```

**生产环境 (production.yaml):**
```yaml
system:
  debug: false
  log_level: INFO
  
database:
  host: prod-db-host
  port: 3306
  name: quant_prod
  
cache:
  ttl: 3600
  max_size: 10000
```

### 敏感信息管理

```bash
# 使用环境变量
export DB_PASSWORD=your_secure_password
export API_KEY=your_api_key

# 或使用配置文件
echo "database_password: your_secure_password" > config/secrets.yaml
chmod 600 config/secrets.yaml
```

## 🚦 服务管理

### Systemd服务 (Linux)

创建服务文件 `/etc/systemd/system/quant-system.service`:

```ini
[Unit]
Description=Quantitative Investment System
After=network.target

[Service]
Type=simple
User=quant
WorkingDirectory=/home/quant/quant_system_deploy
Environment=PYTHONPATH=/home/quant/quant_system_deploy/src
ExecStart=/home/quant/quant_system_deploy/venv/bin/python -c "print('系统启动')"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

服务管理命令：

```bash
# 启用服务
sudo systemctl enable quant-system

# 启动服务
sudo systemctl start quant-system

# 查看状态
sudo systemctl status quant-system

# 查看日志
sudo journalctl -u quant-system -f

# 停止服务
sudo systemctl stop quant-system
```

### 进程管理 (PM2)

```bash
# 安装PM2
npm install -g pm2

# 创建PM2配置文件
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'quant-system',
    script: 'python',
    args: '-c "print(\'系统启动\')"',
    cwd: '/path/to/deploy',
    env: {
      PYTHONPATH: '/path/to/deploy/src',
      ENVIRONMENT: 'production'
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G'
  }]
}
EOF

# 启动应用
pm2 start ecosystem.config.js

# 查看状态
pm2 status

# 查看日志
pm2 logs quant-system

# 停止应用
pm2 stop quant-system
```

## 📊 监控和日志

### 日志配置

```yaml
# config/logging.yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

handlers:
  file:
    level: INFO
    class: logging.handlers.RotatingFileHandler
    filename: logs/quant_system.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    formatter: standard
    
  console:
    level: INFO
    class: logging.StreamHandler
    formatter: standard

loggers:
  '':
    handlers: [file, console]
    level: INFO
    propagate: false
```

### 监控脚本

```bash
#!/bin/bash
# monitor.sh - 系统监控脚本

LOG_FILE="/path/to/deploy/logs/monitor.log"
PID_FILE="/path/to/deploy/quant_system.pid"

# 检查进程是否运行
check_process() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "$(date): 系统正常运行 (PID: $PID)" >> $LOG_FILE
            return 0
        fi
    fi
    
    echo "$(date): 系统未运行，尝试重启" >> $LOG_FILE
    restart_system
}

# 重启系统
restart_system() {
    cd /path/to/deploy
    ./start.sh &
    echo $! > $PID_FILE
    echo "$(date): 系统已重启" >> $LOG_FILE
}

# 检查磁盘空间
check_disk_space() {
    USAGE=$(df /path/to/deploy | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $USAGE -gt 80 ]; then
        echo "$(date): 磁盘空间不足: ${USAGE}%" >> $LOG_FILE
    fi
}

# 主监控循环
while true; do
    check_process
    check_disk_space
    sleep 60
done
```

## 🔒 安全配置

### 防火墙设置

```bash
# Ubuntu/Debian
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # 应用端口

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### SSL/TLS配置

```bash
# 生成自签名证书
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# 或使用Let's Encrypt
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com
```

## 🔄 备份和恢复

### 自动备份脚本

```bash
#!/bin/bash
# backup.sh - 自动备份脚本

BACKUP_DIR="/backup/quant_system"
SOURCE_DIR="/path/to/deploy"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份配置和数据
tar -czf $BACKUP_DIR/quant_system_$DATE.tar.gz \
    -C $SOURCE_DIR \
    config data logs

# 保留最近7天的备份
find $BACKUP_DIR -name "quant_system_*.tar.gz" -mtime +7 -delete

echo "备份完成: quant_system_$DATE.tar.gz"
```

### 恢复流程

```bash
# 停止服务
sudo systemctl stop quant-system

# 恢复备份
cd /path/to/deploy
tar -xzf /backup/quant_system/quant_system_YYYYMMDD_HHMMSS.tar.gz

# 重启服务
sudo systemctl start quant-system
```

## 🚨 故障排除

### 常见问题

**1. 端口被占用**
```bash
# 查找占用端口的进程
sudo netstat -tlnp | grep :8000
sudo lsof -i :8000

# 终止进程
sudo kill -9 <PID>
```

**2. 权限问题**
```bash
# 修复文件权限
sudo chown -R quant:quant /path/to/deploy
sudo chmod -R 755 /path/to/deploy
```

**3. 依赖问题**
```bash
# 重新安装依赖
pip install --force-reinstall -r requirements.txt

# 清理pip缓存
pip cache purge
```

**4. 内存不足**
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 增加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 日志分析

```bash
# 查看错误日志
grep -i error logs/quant_system.log

# 查看最近的日志
tail -f logs/quant_system.log

# 按时间过滤日志
grep "2024-01-01" logs/quant_system.log
```

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 查看日志文件获取详细错误信息
2. 检查系统资源使用情况
3. 参考故障排除章节
4. 联系技术支持团队

**联系方式:**
- 📧 邮件: support@quant-system.com
- 📖 文档: 查看在线文档
- 🐛 问题反馈: GitHub Issues

---

*本指南涵盖了量化投资系统的主要部署方式，请根据实际环境选择合适的部署方案。*
