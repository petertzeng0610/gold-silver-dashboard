"""
應用程式配置模組
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """應用程式設定"""
    
    def __init__(self):
        # Database
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./gold_silver.db")
        
        # Redis
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # Gemini AI
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Price API
        self.taiwan_bank_api_url = os.getenv(
            "TAIWAN_BANK_API_URL",
            "https://rate.bot.com.tw/xrt/quote/l6m/TWD"
        )
        self.price_api_timeout = int(os.getenv("PRICE_API_TIMEOUT", "30"))
        
        # Application
        self.refresh_interval = int(os.getenv("REFRESH_INTERVAL", "120"))  # 2分鐘
        self.timezone = os.getenv("TIMEZONE", "Asia/Taipei")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.admin_api_key = os.getenv("ADMIN_API_KEY", "your-secret-api-key")  # API保護金鑰

        # Server
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        # CORS
        origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
        self.allowed_origins = [origin.strip() for origin in origins_str.split(",")]


# 全域設定實例
settings = Settings()
