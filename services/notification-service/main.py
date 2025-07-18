from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="通知服务",
    description="量化投资系统通知管理微服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "通知服务",
        "status": "运行中",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "notification-service",
        "database": "connected" if os.getenv("DATABASE_URL") else "not configured"
    }


@app.get("/api/v1/notifications")
async def get_notifications():
    """获取通知列表"""
    try:
        return {
            "notifications": [
                {
                    "id": "notif_001",
                    "type": "trade_alert",
                    "title": "交易信号",
                    "message": "AAPL出现买入信号",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "read": False
                },
                {
                    "id": "notif_002",
                    "type": "system_alert",
                    "title": "系统通知",
                    "message": "策略回测完成",
                    "timestamp": "2024-01-15T09:15:00Z",
                    "read": True
                }
            ],
            "message": "通知服务正常运行"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/notifications")
async def send_notification():
    """发送通知"""
    try:
        return {
            "notification_id": "notif_003",
            "status": "sent",
            "message": "通知发送成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
