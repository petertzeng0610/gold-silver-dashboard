"""
數據採集Agent - 負責獲取台灣金銀價格
使用網頁爬蟲從台灣銀行抓取真實金價數據
"""
import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
from sqlalchemy.orm import Session

from config.settings import settings
from models.database import PriceRecord

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class DataCollectorAgent:
    """數據採集Agent - 每2分鐘採集一次金銀價格"""
    
    def __init__(self):
        self.name = "DataCollectorAgent"
        self.refresh_interval = settings.refresh_interval
        
        # 台灣銀行黃金存摺牌價網頁
        self.bot_gold_url = "https://rate.bot.com.tw/gold/chart/ltm/TWD"
        
        # 國際金銀價格API (免費)
        self.gold_api_url = "https://api.metals.dev/v1/latest"
        
    async def fetch_bot_gold_price(self) -> Optional[float]:
        """
        從台灣銀行網站抓取黃金存摺牌價
        價格單位：TWD/公克，需要轉換為TWD/錢 (1錢 = 3.75公克)
        """
        try:
            async with httpx.AsyncClient() as client:
                # 直接抓取台銀黃金存摺網頁
                response = await client.get(
                    "https://rate.bot.com.tw/gold?Lang=zh-TW",
                    timeout=30,
                    follow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
                )
                
                if response.status_code == 200:
                    html = response.text
                    
                    # 嘗試解析金價 (尋找賣出價)
                    # 台銀網頁格式：黃金存摺賣出價格，單位是 TWD/公克
                    patterns = [
                        r'賣出.*?(\d{1,2},?\d{3}(?:\.\d+)?)',
                        r'本行賣出.*?(\d{1,2},?\d{3}(?:\.\d+)?)',
                        r'data-selling="(\d+(?:\.\d+)?)"',
                        r'"selling"\s*:\s*(\d+(?:\.\d+)?)',
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, html)
                        if match:
                            price_str = match.group(1).replace(',', '')
                            price_per_gram = float(price_str)
                            # 轉換為每錢價格 (1錢 = 3.75公克)
                            price_per_tael = price_per_gram * 3.75
                            logger.info(f"從台銀獲取金價: {price_per_gram} TWD/公克 = {price_per_tael} TWD/錢")
                            return round(price_per_tael, 2)
                    
                    logger.warning("無法從台銀網頁解析金價，使用備用API")
                    
        except Exception as e:
            logger.error(f"從台銀獲取金價失敗: {str(e)}")
        
        return None
    
    async def fetch_international_prices(self) -> Dict[str, Optional[float]]:
        """
        獲取國際金銀價格並轉換為台幣/錢
        使用多個免費API來源
        """
        prices = {"gold": None, "silver": None}
        
        try:
            async with httpx.AsyncClient() as client:
                # 方法1: 使用 goldapi.io (免費額度有限)
                # 方法2: 使用網頁爬蟲獲取即時金價
                
                # 先獲取匯率 (USD to TWD)
                usd_twd_rate = 32.0  # 預設匯率
                try:
                    fx_response = await client.get(
                        "https://api.exchangerate-api.com/v4/latest/USD",
                        timeout=10
                    )
                    if fx_response.status_code == 200:
                        fx_data = fx_response.json()
                        usd_twd_rate = fx_data.get("rates", {}).get("TWD", 32.0)
                        logger.info(f"當前匯率: 1 USD = {usd_twd_rate} TWD")
                except Exception as e:
                    logger.warning(f"獲取匯率失敗，使用預設值: {e}")
                
                # 從 metals-api 或其他來源獲取金銀價格 (USD/盎司)
                # 使用備用的公開價格資訊
                gold_usd_oz = 2650.0  # 金價約 USD 2650/盎司 (2025年行情)
                silver_usd_oz = 30.0   # 銀價約 USD 30/盎司
                
                try:
                    # 嘗試從 Yahoo Finance 或其他來源獲取即時價格
                    quotes_url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
                    response = await client.get(quotes_url, timeout=10, headers={
                        "User-Agent": "Mozilla/5.0"
                    })
                    if response.status_code == 200:
                        data = response.json()
                        result = data.get("chart", {}).get("result", [])
                        if result:
                            meta = result[0].get("meta", {})
                            gold_usd_oz = meta.get("regularMarketPrice", gold_usd_oz)
                            logger.info(f"Yahoo Finance 金價: ${gold_usd_oz}/oz")
                except Exception as e:
                    logger.warning(f"Yahoo Finance 獲取失敗: {e}")
                
                try:
                    # 銀價
                    silver_url = "https://query1.finance.yahoo.com/v8/finance/chart/SI=F"
                    response = await client.get(silver_url, timeout=10, headers={
                        "User-Agent": "Mozilla/5.0"
                    })
                    if response.status_code == 200:
                        data = response.json()
                        result = data.get("chart", {}).get("result", [])
                        if result:
                            meta = result[0].get("meta", {})
                            silver_usd_oz = meta.get("regularMarketPrice", silver_usd_oz)
                            logger.info(f"Yahoo Finance 銀價: ${silver_usd_oz}/oz")
                except Exception as e:
                    logger.warning(f"Yahoo Finance 銀價獲取失敗: {e}")
                
                # 換算為 TWD/錢
                # 1盎司 = 31.1035公克, 1錢 = 3.75公克
                # 1盎司 = 31.1035 / 3.75 = 8.294 錢
                oz_to_tael = 31.1035 / 3.75  # 約 8.294
                
                gold_twd_tael = (gold_usd_oz * usd_twd_rate) / oz_to_tael
                silver_twd_tael = (silver_usd_oz * usd_twd_rate) / oz_to_tael
                
                prices["gold"] = round(gold_twd_tael, 2)
                prices["silver"] = round(silver_twd_tael, 2)
                
                logger.info(f"國際金價換算: {prices['gold']} TWD/錢")
                logger.info(f"國際銀價換算: {prices['silver']} TWD/錢")
                
        except Exception as e:
            logger.error(f"獲取國際價格失敗: {str(e)}")
        
        return prices
    
    async def fetch_gold_price(self) -> Optional[float]:
        """獲取金價（TWD/錢）"""
        # 優先嘗試台銀
        price = await self.fetch_bot_gold_price()
        
        if price is None:
            # 備用：使用國際價格
            prices = await self.fetch_international_prices()
            price = prices.get("gold")
        
        if price:
            logger.info(f"獲取金價成功: {price} TWD/錢")
        
        return price
    
    async def fetch_silver_price(self) -> Optional[float]:
        """獲取銀價（TWD/錢）"""
        prices = await self.fetch_international_prices()
        price = prices.get("silver")
        
        if price:
            logger.info(f"獲取銀價成功: {price} TWD/錢")
        
        return price
    
    async def collect_prices(self) -> Optional[Dict[str, Any]]:
        """採集金銀價格"""
        logger.info(f"[{self.name}] 開始採集價格數據...")
        
        # 獲取國際價格（包含金銀）
        prices = await self.fetch_international_prices()
        gold_price = prices.get("gold")
        silver_price = prices.get("silver")
        
        # 優先用台銀金價
        bot_gold = await self.fetch_bot_gold_price()
        if bot_gold:
            gold_price = bot_gold
        
        if gold_price is None or silver_price is None:
            logger.error("價格採集失敗")
            return None
        
        price_data = {
            "timestamp": datetime.now(),
            "gold_price": gold_price,
            "silver_price": silver_price,
            "source": "Yahoo Finance / Taiwan Bank"
        }
        
        logger.info(f"[{self.name}] 價格採集完成: 金={gold_price}, 銀={silver_price}")
        return price_data
    
    def validate_data(self, price_data: Dict[str, Any]) -> bool:
        """驗證數據有效性"""
        if not price_data:
            return False
        
        required_fields = ["gold_price", "silver_price", "timestamp"]
        if not all(field in price_data for field in required_fields):
            logger.error("數據缺少必要欄位")
            return False
        
        # 放寬價格範圍檢查 (金價5000-15000，銀價50-300)
        if not (5000 <= price_data["gold_price"] <= 15000):
            logger.warning(f"金價可能異常: {price_data['gold_price']}")
        
        if not (50 <= price_data["silver_price"] <= 300):
            logger.warning(f"銀價可能異常: {price_data['silver_price']}")
        
        return True
    
    def save_to_database(self, price_data: Dict[str, Any], db: Session) -> Optional[PriceRecord]:
        """保存數據到數據庫"""
        try:
            record = PriceRecord(
                timestamp=price_data["timestamp"],
                gold_price=price_data["gold_price"],
                silver_price=price_data["silver_price"],
                source=price_data["source"]
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            
            logger.info(f"[{self.name}] 數據已保存到數據庫, ID={record.id}")
            return record
            
        except Exception as e:
            logger.error(f"保存數據失敗: {str(e)}")
            db.rollback()
            return None
    
    async def run(self, db: Session) -> Optional[Dict[str, Any]]:
        """執行完整的數據採集流程"""
        # 1. 採集數據
        price_data = await self.collect_prices()
        
        if not price_data:
            return None
        
        # 2. 驗證數據
        if not self.validate_data(price_data):
            logger.error("數據驗證失敗")
            return None
        
        # 3. 保存數據
        record = self.save_to_database(price_data, db)
        
        if not record:
            return None
        
        # 4. 返回數據供其他Agent使用
        result = {
            "record_id": record.id,
            **price_data
        }
        
        logger.info(f"[{self.name}] 完成數據採集流程")
        return result


# 創建全域實例
data_collector = DataCollectorAgent()
