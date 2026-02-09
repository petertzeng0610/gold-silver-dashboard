"""
FastAPI路由定義
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from models.database import get_db
from coordinator.agent_coordinator import coordinator

router = APIRouter()


@router.get("/")
async def root():
    """根路徑"""
    return {
        "message": "台灣金銀價格追蹤與分析系統 API",
        "version": "1.0.0",
        "status": "運行中"
    }


@router.get("/health")
async def health_check():
    """健康檢查"""
    return {"status": "healthy", "coordinator_running": coordinator.is_running}


@router.post("/collect")
async def trigger_collection(db: Session = Depends(get_db)):
    """
    手動觸發一次數據採集
    
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
