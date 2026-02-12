"""
FastAPI路由定義
"""
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Dict, Any

from config.settings import settings
from models.database import get_db
from coordinator.agent_coordinator import coordinator

router = APIRouter()

# 安全性設定 - 簡單 API Key 驗證
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """驗證管理 API 金鑰"""
    if not api_key or api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=403,
            detail="無效的 API 金鑰"
        )
    return api_key


@router.get("/")
async def root():
    """根路徑"""
    return {
        "message": "台灣金銀價格追蹤與分析系統 API",
        "version": "1.1.1",
        "status": "運行中",
        "last_build": "2026-02-12 17:02 (Sync Fix)"
    }


@router.get("/version")
async def get_version():
    """獲獲取版本號 (驗證部署用)"""
    return {"version": "1.1.1", "env": "production"}


@router.get("/health")
async def health_check():
    """健康檢查"""
    return {"status": "healthy", "coordinator_running": coordinator.is_running}


@router.get("/debug/state")
async def get_debug_state(db: Session = Depends(get_db)):
    """獲取調試狀態 (不需要 Key)"""
    from models.database import PriceRecord, StatisticsRecord, AIAnalysisRecord
    
    counts = {
        "price_records": db.query(PriceRecord).count(),
        "statistics_records": db.query(StatisticsRecord).count(),
        "ai_analysis_records": db.query(AIAnalysisRecord).count()
    }
    
    return {
        "status": "success",
        "database_url_configured": settings.database_url != "sqlite:///./gold_silver.db",
        "gemini_api_key_configured": bool(settings.gemini_api_key),
        "data_counts": counts,
        "coordinator_running": coordinator.is_running
    }


@router.get("/debug/collect")
async def debug_collect(db: Session = Depends(get_db)):
    """
    公開的調試採集接口 (方便 Zeabur 測試)
    執行完整的流水線並詳細返回結果
    """
    try:
        result = await coordinator.execute_pipeline(db)
        return {
            "status": "success" if result["success"] else "failed",
            "pipeline_result": {
                "success": result["success"],
                "errors": result["errors"],
                "data_captured": list(result["data"].keys())
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/collect")
async def trigger_collection(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    手動觸發一次數據採集 (需要 API Key)
    
    執行完整的流水線：數據採集 -> 分析 -> AI分析
    """
    try:
        result = await coordinator.execute_pipeline(db)
        
        if result["success"]:
            return {
                "status": "success",
                "message": "數據採集完成",
                "data": result["data"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": "數據採集失敗",
                    "errors": result["errors"]
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )


@router.get("/latest")
async def get_latest_data(db: Session = Depends(get_db)):
    """
    獲取最新的綜合數據
    
    包括：
    - 最新價格
    - 最新統計分析
    - 最新AI分析
    """
    try:
        data = await coordinator.get_latest_data(db)
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )


@router.get("/history")
async def get_historical_data(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    獲取歷史數據
    
    Args:
        days: 獲取最近幾天的數據（默認30天）
    
    Returns:
        時間序列數據供圖表使用
    """
    try:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "message": "days必須在1-365之間"}
            )
        
        data = await coordinator.get_historical_data(db, days)
        return {
            "status": "success",
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )


@router.get("/prices/current")
async def get_current_prices(db: Session = Depends(get_db)):
    """獲取當前金銀價格"""
    try:
        from models.database import PriceRecord
        
        latest = db.query(PriceRecord).order_by(
            PriceRecord.timestamp.desc()
        ).first()
        
        if not latest:
            return {
                "status": "success",
                "data": None,
                "message": "暫無數據"
            }
        
        return {
            "status": "success",
            "data": latest.to_dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )


@router.get("/statistics/monthly")
async def get_monthly_statistics(db: Session = Depends(get_db)):
    """獲取月度統計數據"""
    try:
        from models.database import StatisticsRecord
        
        latest = db.query(StatisticsRecord).filter(
            StatisticsRecord.period == "monthly"
        ).order_by(StatisticsRecord.timestamp.desc()).first()
        
        if not latest:
            return {
                "status": "success",
                "data": None,
                "message": "暫無統計數據"
            }
        
        return {
            "status": "success",
            "data": latest.to_dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )


@router.get("/ai-analysis/latest")
async def get_latest_ai_analysis(db: Session = Depends(get_db)):
    """獲取最新的AI分析"""
    try:
        from models.database import AIAnalysisRecord
        
        latest = db.query(AIAnalysisRecord).order_by(
            AIAnalysisRecord.timestamp.desc()
        ).first()
        
        if not latest:
            return {
                "status": "success",
                "data": None,
                "message": "暫無AI分析"
            }
        
        return {
            "status": "success",
            "data": latest.to_dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": str(e)}
        )
