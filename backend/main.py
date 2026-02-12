"""
FastAPI主應用程式
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware  # 新增
from fastapi.middleware.gzip import GZipMiddleware  # 新增

from config.settings import settings
from models.database import init_db, get_db
from api.routes import router
from coordinator.agent_coordinator import coordinator

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


# 後台任務引用
background_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    應用程式生命週期管理
    
    啟動時：
    - 初始化數據庫
    - 啟動定時採集任務
    
    關閉時：
    - 停止定時採集任務
    """
    global background_task
    
    # 啟動
    logger.info("========== 應用程式啟動 ==========")
    
    # 初始化數據庫
    logger.info("初始化數據庫...")
    init_db()
    logger.info("✓ 數據庫初始化完成")

    # 立即執行一次採集，確保啟動後即有資料
    logger.info("執行啟動時立即採集...")
    async def run_initial_collection():
        from models.database import SessionLocal
        db = SessionLocal()
        try:
            await coordinator.execute_pipeline(db)
        finally:
            db.close()
    
    asyncio.create_task(run_initial_collection())
    
    # 啟動後台定時任務
    logger.info("啟動定時採集任務...")
    background_task = asyncio.create_task(
        coordinator.start_scheduled_collection(get_db)
    )
    logger.info("✓ 定時採集任務已啟動")
    
    logger.info("========== 應用程式準備就緒 ==========")
    
    yield
    
    # 關閉
    logger.info("========== 應用程式關閉 ==========")
    
    # 停止定時任務
    logger.info("停止定時採集任務...")
    coordinator.stop_scheduled_collection()
    
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            logger.info("✓ 定時採集任務已停止")
    
    logger.info("========== 應用程式已關閉 ==========")


# 創建FastAPI應用
app = FastAPI(
    title="台灣金銀價格追蹤與分析系統",
    description="基於多Agent架構的智能金銀價格追蹤系統",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # 限制為僅使用 GET 和 POST
    allow_headers=["*"],
)

# 增加 TrustedHostMiddleware 保護 Host Header Injection
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 部署後建議修改為具體域名，例如 ["api.zeabur.app", "localhost"]
)

# 增加 GZip 壓縮回應，優化傳輸速度
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 註冊路由
app.include_router(router, prefix="/api", tags=["api"])


if __name__ == "__main__":
    import uvicorn
    import os
    
    # 讀取環境變數 PORT，預設為 8000
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
