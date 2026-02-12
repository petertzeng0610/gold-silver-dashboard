"""
數據分析Agent - 負責統計分析和趨勢計算
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from config.settings import settings
from models.database import PriceRecord, StatisticsRecord

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class DataAnalyzerAgent:
    """數據分析Agent - 計算統計指標和趨勢"""
    
    def __init__(self):
        self.name = "DataAnalyzerAgent"
    
    def get_monthly_data(self, db: Session) -> List[PriceRecord]:
        """獲取最近一個月的數據"""
        one_month_ago = datetime.now() - timedelta(days=30)
        
        records = db.query(PriceRecord).filter(
            PriceRecord.timestamp >= one_month_ago
        ).order_by(PriceRecord.timestamp.asc()).all()
        
        logger.info(f"[{self.name}] 獲取到 {len(records)} 筆月度數據")
        return records
    
    def calculate_monthly_average(self, db: Session) -> Dict[str, float]:
        """計算月度平均價格"""
        records = self.get_monthly_data(db)
        
        if not records:
            logger.warning("沒有足夠的數據計算月平均")
            return {"gold_avg": 0, "silver_avg": 0, "platinum_avg": 0}
        
        gold_prices = [r.gold_price for r in records]
        silver_prices = [r.silver_price for r in records]
        
        gold_avg = round(float(np.mean(gold_prices or [0])), 2)
        silver_avg = round(float(np.mean(silver_prices or [0])), 2)
        platinum_prices = [r.platinum_price for r in records if r.platinum_price is not None]
        platinum_avg = round(float(np.mean(platinum_prices or [0])), 2)
        
        logger.info(f"[{self.name}] 月平均 - 金: {gold_avg}, 銀: {silver_avg}, 白金: {platinum_avg}")
        
        return {
            "gold_avg": gold_avg,
            "silver_avg": silver_avg,
            "platinum_avg": platinum_avg
        }
    
    def calculate_statistics(self, db: Session) -> Dict[str, Any]:
        """計算完整的統計數據"""
        records = self.get_monthly_data(db)
        
        if not records:
            return self._empty_statistics()
        
        gold_prices = np.array([r.gold_price for r in records])
        silver_prices = np.array([r.silver_price for r in records])
        
        gold_stats = {
            "avg": round(float(np.mean(gold_prices)), 2),
            "max": round(float(np.max(gold_prices)), 2),
            "min": round(float(np.min(gold_prices)), 2),
            "std": round(float(np.std(gold_prices)), 2),
            "median": round(float(np.median(gold_prices)), 2),
        }
        
        silver_stats = {
            "avg": round(float(np.mean(silver_prices)), 2),
            "max": round(float(np.max(silver_prices)), 2),
            "min": round(float(np.min(silver_prices)), 2),
            "std": round(float(np.std(silver_prices)), 2),
            "median": round(float(np.median(silver_prices)), 2),
        }
        
        platinum_prices = np.array([r.platinum_price for r in records if r.platinum_price is not None])
        if platinum_prices.size > 0:
            platinum_stats = {
                "avg": round(float(np.mean(platinum_prices)), 2),
                "max": round(float(np.max(platinum_prices)), 2),
                "min": round(float(np.min(platinum_prices)), 2),
                "std": round(float(np.std(platinum_prices)), 2),
                "median": round(float(np.median(platinum_prices)), 2),
            }
        else:
            platinum_stats = {"avg": 0, "max": 0, "min": 0, "std": 0, "median": 0}
        
        logger.info(f"[{self.name}] 統計分析完成")
        
        return {
            "gold": gold_stats,
            "silver": silver_stats,
            "platinum": platinum_stats,
            "period": "monthly",
            "data_points": len(records),
            "timestamp": datetime.now()
        }
    
    def analyze_trend(self, db: Session) -> Dict[str, str]:
        """分析價格趨勢"""
        records = self.get_monthly_data(db)
        
        if len(records) < 2:
            return {"gold_trend": "insufficient_data", "silver_trend": "insufficient_data"}
        
        # 取最近7天和之前7天的數據比較
        mid_point = len(records) // 2
        
        gold_prices = [r.gold_price for r in records]
        silver_prices = [r.silver_price for r in records]
        
        # 簡單趨勢判斷：比較前半段和後半段平均值
        gold_first_half = np.mean(gold_prices[:mid_point])
        gold_second_half = np.mean(gold_prices[mid_point:])
        
        silver_first_half = np.mean(silver_prices[:mid_point])
        silver_second_half = np.mean(silver_prices[mid_point:])
        
        # 判斷趨勢
        gold_trend = self._determine_trend(gold_first_half, gold_second_half)
        silver_trend = self._determine_trend(silver_first_half, silver_second_half)
        
        logger.info(f"[{self.name}] 趨勢分析 - 金: {gold_trend}, 銀: {silver_trend}")
        
        return {
            "gold_trend": gold_trend,
            "silver_trend": silver_trend,
            "gold_change_percent": round((gold_second_half - gold_first_half) / gold_first_half * 100, 2),
            "silver_change_percent": round((silver_second_half - silver_first_half) / silver_first_half * 100, 2),
        }
    
    def _determine_trend(self, first_value: float, second_value: float) -> str:
        """判斷趨勢方向"""
        change_percent = (second_value - first_value) / first_value * 100
        
        if change_percent > 2:
            return "上升"
        elif change_percent < -2:
            return "下降"
        else:
            return "持平"
    
    def detect_anomalies(self, db: Session) -> List[Dict[str, Any]]:
        """檢測價格異常波動"""
        records = self.get_monthly_data(db)
        
        if len(records) < 10:
            return []
        
        gold_prices = np.array([r.gold_price for r in records])
        silver_prices = np.array([r.silver_price for r in records])
        
        gold_mean = np.mean(gold_prices)
        gold_std = np.std(gold_prices)
        silver_mean = np.mean(silver_prices)
        silver_std = np.std(silver_prices)
        
        anomalies = []
        
        # 使用3個標準差作為異常判定標準
        for record in records:
            if abs(record.gold_price - gold_mean) > 3 * gold_std:
                anomalies.append({
                    "type": "gold",
                    "timestamp": record.timestamp,
                    "price": record.gold_price,
                    "deviation": abs(record.gold_price - gold_mean) / gold_std
                })
            
            if abs(record.silver_price - silver_mean) > 3 * silver_std:
                anomalies.append({
                    "type": "silver",
                    "timestamp": record.timestamp,
                    "price": record.silver_price,
                    "deviation": abs(record.silver_price - silver_mean) / silver_std
                })
        
        if anomalies:
            logger.warning(f"[{self.name}] 檢測到 {len(anomalies)} 個異常數據")
        
        return anomalies
    
    def save_statistics(self, stats: Dict[str, Any], db: Session) -> Optional[StatisticsRecord]:
        """保存統計結果到數據庫"""
        try:
            record = StatisticsRecord(
                timestamp=stats["timestamp"],
                period=stats["period"],
                gold_avg=stats["gold"]["avg"],
                gold_max=stats["gold"]["max"],
                gold_min=stats["gold"]["min"],
                gold_std=stats["gold"]["std"],
                silver_avg=stats["silver"]["avg"],
                silver_max=stats["silver"]["max"],
                silver_min=stats["silver"]["min"],
                silver_std=stats["silver"]["std"],
                platinum_avg=stats["platinum"]["avg"],
                platinum_max=stats["platinum"]["max"],
                platinum_min=stats["platinum"]["min"],
                platinum_std=stats["platinum"]["std"],
            )
            
            db.add(record)
            db.commit()
            db.refresh(record)
            
            logger.info(f"[{self.name}] 統計數據已保存, ID={record.id}")
            return record
            
        except Exception as e:
            logger.error(f"保存統計數據失敗: {str(e)}")
            db.rollback()
            return None
    
    def _empty_statistics(self) -> Dict[str, Any]:
        """返回空統計數據"""
        return {
            "gold": {"avg": 0, "max": 0, "min": 0, "std": 0, "median": 0},
            "silver": {"avg": 0, "max": 0, "min": 0, "std": 0, "median": 0},
            "period": "monthly",
            "data_points": 0,
            "timestamp": datetime.now()
        }
    
    async def run(self, db: Session) -> Dict[str, Any]:
        """執行完整的數據分析流程"""
        logger.info(f"[{self.name}] 開始數據分析...")
        
        # 1. 計算統計數據
        statistics = self.calculate_statistics(db)
        
        # 2. 分析趨勢
        trend = self.analyze_trend(db)
        
        # 3. 檢測異常
        anomalies = self.detect_anomalies(db)
        
        # 4. 保存統計結果
        self.save_statistics(statistics, db)
        
        result = {
            "statistics": statistics,
            "trend": trend,
            "anomalies": anomalies
        }
        
        logger.info(f"[{self.name}] 分析完成")
        return result


# 創建全域實例
data_analyzer = DataAnalyzerAgent()
