"""
FastAPI主應用程式
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(router, prefix="/api", tags=["api"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
