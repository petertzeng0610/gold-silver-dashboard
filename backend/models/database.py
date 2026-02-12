"""
數據庫模型定義
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

Base = declarative_base()


class PriceRecord(Base):
    """金銀價格記錄"""
    __tablename__ = "price_records"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    gold_price = Column(Float, nullable=False, comment="金價 (TWD/錢)")
    silver_price = Column(Float, nullable=False, comment="銀價 (TWD/錢)")
    platinum_price = Column(Float, nullable=True, comment="白金牌價 (TWD/錢)")
    source = Column(String(100), comment="數據來源")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "gold_price": self.gold_price,
            "silver_price": self.silver_price,
            "platinum_price": self.platinum_price,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StatisticsRecord(Base):
    """統計分析記錄"""
    __tablename__ = "statistics_records"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    period = Column(String(50), comment="統計期間 (daily/weekly/monthly)")
    
    # 金價統計
    gold_avg = Column(Float, comment="金價平均")
    gold_max = Column(Float, comment="金價最高")
    gold_min = Column(Float, comment="金價最低")
    gold_std = Column(Float, comment="金價標準差")
    
    # 銀價統計
    silver_avg = Column(Float, comment="銀價平均")
    silver_max = Column(Float, comment="銀價最高")
    silver_min = Column(Float, comment="銀價最低")
    silver_std = Column(Float, comment="銀價標準差")
    
    # 白金統計
    platinum_avg = Column(Float, comment="白金平均")
    platinum_max = Column(Float, comment="白金最高")
    platinum_min = Column(Float, comment="白金最低")
    platinum_std = Column(Float, comment="白金標準差")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "period": self.period,
            "gold": {
                "avg": self.gold_avg,
                "max": self.gold_max,
                "min": self.gold_min,
                "std": self.gold_std,
            },
            "silver": {
                "avg": self.silver_avg,
                "max": self.silver_max,
                "min": self.silver_min,
                "std": self.silver_std,
            },
            "platinum": {
                "avg": self.platinum_avg,
                "max": self.platinum_max,
                "min": self.platinum_min,
                "std": self.platinum_std,
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AIAnalysisRecord(Base):
    """AI分析記錄"""
    __tablename__ = "ai_analysis_records"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    analysis_type = Column(String(50), comment="分析類型")
    
    # AI分析結果
    market_analysis = Column(Text, comment="市場分析")
    trend_prediction = Column(Text, comment="趨勢預測")
    investment_advice = Column(Text, comment="投資建議")
    risk_warning = Column(Text, comment="風險提示")
    
    # 元數據
    model_name = Column(String(100), comment="AI模型名稱")
    confidence_score = Column(Float, comment="信心分數")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "analysis_type": self.analysis_type,
            "market_analysis": self.market_analysis,
            "trend_prediction": self.trend_prediction,
            "investment_advice": self.investment_advice,
            "risk_warning": self.risk_warning,
            "model_name": self.model_name,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# 數據庫引擎和會話
engine = create_engine(
    settings.database_url,
    echo=settings.log_level == "DEBUG",
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化數據庫"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """獲取數據庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
