"""
初始化數據腳本 - 生成過去30天的模擬歷史數據
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from config.settings import settings
from models.database import init_db, get_db, PriceRecord, StatisticsRecord

# 確保數據庫已初始化
init_db()

def generate_historical_data():
    """生成過去30天的歷史數據"""
    db = next(get_db())
    
    try:
        # 檢查是否已有數據
        count = db.query(PriceRecord).count()
        if count > 100:
            print(f"數據庫已有 {count} 筆數據，跳過生成")
            return

        print("開始生成歷史數據...")
        
        # 設定基準價格
        base_gold_price = 9600.0  # TWD/錢
        base_silver_price = 115.0  # TWD/錢
        
        start_date = datetime.now() - timedelta(days=30)
        
        records = []
        current_date = start_date
        
        while current_date <= datetime.now():
            # 每天生成約 24*30 = 720 筆數據太大了，我們每小時生成一筆即可
            # 或者每4小時一筆，一天6筆
            
            # 隨機波動
            gold_fluctuation = random.uniform(-50, 50)
            silver_fluctuation = random.uniform(-1, 1)
            
            # 加上趨勢 (讓價格有點波浪)
            day_offset = (current_date - start_date).days
            trend_gold = 100 * (1 if day_offset % 10 < 5 else -1)
            trend_silver = 2 * (1 if day_offset % 10 < 5 else -1)
            
            gold_price = base_gold_price + trend_gold + gold_fluctuation
            silver_price = base_silver_price + trend_silver + silver_fluctuation
            
            record = PriceRecord(
                timestamp=current_date,
                gold_price=round(gold_price, 2),
                silver_price=round(silver_price, 2),
                source="Historical Simulation"
            )
            records.append(record)
            
            # 下一個時間點 (每4小時)
            current_date += timedelta(hours=4)
        
        # 批量寫入
        db.bulk_save_objects(records)
        db.commit()
        print(f"成功生成 {len(records)} 筆歷史數據")
        
        # 生成統計數據
        stats = StatisticsRecord(
            timestamp=datetime.now(),
            period="monthly",
            gold_avg=round(base_gold_price, 2),
            gold_max=round(base_gold_price + 200, 2),
            gold_min=round(base_gold_price - 200, 2),
            gold_std=50.5,
            silver_avg=round(base_silver_price, 2),
            silver_max=round(base_silver_price + 5, 2),
            silver_min=round(base_silver_price - 5, 2),
            silver_std=2.1
        )
        db.add(stats)
        db.commit()
        print("統計數據已生成")
        
    except Exception as e:
        print(f"生成數據失敗: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_historical_data()
