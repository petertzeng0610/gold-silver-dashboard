"""
Agent協調器 - 負責協調所有Agent的工作流程
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from config.settings import settings
from agents.data_collector import data_collector
from agents.data_analyzer import data_analyzer
from agents.ai_analyzer import ai_analyzer

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Agent協調器
    負責：
    1. 定時觸發數據採集
    2. 協調Agent間的協作
    3. 管理數據流程
    4. 錯誤處理和重試
    """
    
    def __init__(self):
        self.name = "AgentCoordinator"
        self.refresh_interval = settings.refresh_interval
        self.is_running = False
    
    async def execute_pipeline(self, db: Session) -> Dict[str, Any]:
        """
        執行完整的數據處理流水線
        
        流程：
        1. Data Collector: 採集價格數據
        2. Data Analyzer: 分析統計數據
        3. AI Analyzer: 生成AI分析
        4. 返回整合結果
        """
        logger.info(f"[{self.name}] ========== 開始執行流水線 ==========")
        start_time = datetime.now()
        
        result = {
            "success": False,
            "timestamp": start_time,
            "data": {},
            "errors": []
        }
        
        try:
            # Step 1: 數據採集
            logger.info(f"[{self.name}] Step 1: 數據採集")
            price_data = await data_collector.run(db)
            
            if not price_data:
                error_msg = "數據採集失敗"
                logger.error(f"[{self.name}] {error_msg}")
                result["errors"].append(error_msg)
                return result
            
            result["data"]["prices"] = price_data
            logger.info(f"[{self.name}] ✓ 數據採集成功")
            
            # Step 2: 數據分析
            logger.info(f"[{self.name}] Step 2: 數據分析")
            analysis_result = await data_analyzer.run(db)
            
            if not analysis_result:
                error_msg = "數據分析失敗"
                logger.warning(f"[{self.name}] {error_msg}")
                result["errors"].append(error_msg)
            else:
                result["data"]["analysis"] = analysis_result
                logger.info(f"[{self.name}] ✓ 數據分析成功")
            
            # Step 3: AI分析
            logger.info(f"[{self.name}] Step 3: AI分析")
            ai_result = await ai_analyzer.run(
                current_data=price_data,
                statistics=analysis_result.get("statistics", {}),
                trend=analysis_result.get("trend", {}),
                db=db
            )
            
            if not ai_result:
                error_msg = "AI分析失敗"
                logger.warning(f"[{self.name}] {error_msg}")
                result["errors"].append(error_msg)
            else:
                result["data"]["ai_analysis"] = ai_result
                logger.info(f"[{self.name}] ✓ AI分析成功")
            
            # 流水線成功
            result["success"] = True
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"[{self.name}] ========== 流水線執行完成 "
                f"(耗時: {elapsed_time:.2f}秒) =========="
            )
            
        except Exception as e:
            error_msg = f"流水線執行異常: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}", exc_info=True)
            result["errors"].append(error_msg)
        
        return result
    
    async def start_scheduled_collection(self, db_session_factory):
        """
        啟動定時採集任務
        
        Args:
            db_session_factory: 數據庫會話工廠函數
        """
        logger.info(
            f"[{self.name}] 啟動定時採集任務 "
            f"(間隔: {self.refresh_interval}秒)"
        )
        self.is_running = True
        
        while self.is_running:
            try:
                # 創建新的數據庫會話
                db = next(db_session_factory())
                
                # 執行流水線
                result = await self.execute_pipeline(db)
                
                # 記錄結果
                if result["success"]:
                    logger.info(f"[{self.name}] 定時任務執行成功")
                else:
                    logger.error(
                        f"[{self.name}] 定時任務執行失敗: "
                        f"{', '.join(result['errors'])}"
                    )
                
                # 關閉數據庫會話
                db.close()
                
            except Exception as e:
                logger.error(
                    f"[{self.name}] 定時任務異常: {str(e)}",
                    exc_info=True
                )
            
            # 等待下一次執行
            logger.info(
                f"[{self.name}] 等待 {self.refresh_interval} 秒後執行下一次採集"
            )
            await asyncio.sleep(self.refresh_interval)
    
    def stop_scheduled_collection(self):
        """停止定時採集任務"""
        logger.info(f"[{self.name}] 停止定時採集任務")
        self.is_running = False
    
    async def get_latest_data(self, db: Session) -> Dict[str, Any]:
        """
        獲取最新的綜合數據（不執行新的採集）
        
        用於前端直接查詢最新數據
        """
        try:
            from models.database import PriceRecord, StatisticsRecord, AIAnalysisRecord
            
            # 獲取最新價格
            latest_price = db.query(PriceRecord).order_by(
                PriceRecord.timestamp.desc()
            ).first()
            
            # 獲取最新統計
            latest_stats = db.query(StatisticsRecord).order_by(
                StatisticsRecord.timestamp.desc()
            ).first()
            
            # 獲取最新AI分析
            latest_ai = db.query(AIAnalysisRecord).order_by(
                AIAnalysisRecord.timestamp.desc()
            ).first()
            
            return {
                "prices": latest_price.to_dict() if latest_price else None,
                "statistics": latest_stats.to_dict() if latest_stats else None,
                "ai_analysis": latest_ai.to_dict() if latest_ai else None,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] 獲取最新數據失敗: {str(e)}", exc_info=True)
            return {"error": str(e), "note": "這通常意味著數據庫表結構與程式碼不一致，或者是數據庫為空且獲取邏輯出錯"}
    
    async def get_historical_data(
        self, 
        db: Session, 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        獲取歷史數據
        
        Args:
            db: 數據庫會話
            days: 獲取最近幾天的數據
        """
        try:
            from models.database import PriceRecord
            from datetime import timedelta
            
            start_date = datetime.now() - timedelta(days=days)
            
            records = db.query(PriceRecord).filter(
                PriceRecord.timestamp >= start_date
            ).order_by(PriceRecord.timestamp.asc()).all()
            
            # 格式化數據供圖表使用
            timestamps = []
            gold_prices = []
            silver_prices = []
            platinum_prices = []
            
            for record in records:
                timestamps.append(record.timestamp.isoformat())
                gold_prices.append(record.gold_price)
                silver_prices.append(record.silver_price)
                platinum_prices.append(record.platinum_price)
            
            return {
                "timestamps": timestamps,
                "gold_prices": gold_prices,
                "silver_prices": silver_prices,
                "platinum_prices": platinum_prices,
                "count": len(records)
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] 獲取歷史數據失敗: {str(e)}")
            return {}


# 創建全域實例
coordinator = AgentCoordinator()
