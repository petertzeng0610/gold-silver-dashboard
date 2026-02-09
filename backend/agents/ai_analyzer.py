"""
AI分析Agent - 使用Gemini 3進行綜合分析
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import google.generativeai as genai
from sqlalchemy.orm import Session

from config.settings import settings
from models.database import AIAnalysisRecord

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class AIAnalyzerAgent:
    """AI分析Agent - 使用Gemini 3進行市場分析和預測"""
    
    def __init__(self):
        self.name = "AIAnalyzerAgent"
        self.model_name = settings.gemini_model
        
        # 配置Gemini API
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"[{self.name}] Gemini模型已初始化: {self.model_name}")
        else:
            self.model = None
            logger.warning(f"[{self.name}] Gemini API Key未設置，將使用模擬分析")
    
    def create_analysis_prompt(
        self, 
        current_data: Dict[str, Any], 
        statistics: Dict[str, Any],
        trend: Dict[str, Any]
    ) -> str:
        """創建分析提示詞"""
        
        prompt = f"""
你是一位專業的貴金屬市場分析師，專精於台灣金銀市場分析。請根據以下數據進行深入分析：

## 當前價格數據
- 當前金價：{current_data.get('gold_price', 'N/A')} TWD/錢
- 當前銀價：{current_data.get('silver_price', 'N/A')} TWD/錢
- 數據時間：{current_data.get('timestamp', 'N/A')}

## 月度統計數據
### 金價統計（過去30天）
- 平均價格：{statistics['gold']['avg']} TWD/錢
- 最高價格：{statistics['gold']['max']} TWD/錢
- 最低價格：{statistics['gold']['min']} TWD/錢
- 標準差：{statistics['gold']['std']}
- 中位數：{statistics['gold']['median']} TWD/錢

### 銀價統計（過去30天）
- 平均價格：{statistics['silver']['avg']} TWD/錢
- 最高價格：{statistics['silver']['max']} TWD/錢
- 最低價格：{statistics['silver']['min']} TWD/錢
- 標準差：{statistics['silver']['std']}
- 中位數：{statistics['silver']['median']} TWD/錢

## 趨勢分析
- 金價趨勢：{trend['gold_trend']}（變化 {trend.get('gold_change_percent', 0)}%）
- 銀價趨勢：{trend['silver_trend']}（變化 {trend.get('silver_change_percent', 0)}%）

請提供以下四個部分的專業分析：

1. **市場分析**：分析當前金銀價格相對於月平均的位置，評估市場狀況（超買/超賣/合理區間）

2. **趨勢預測**：基於歷史數據和當前趨勢，預測未來3-7天的價格走勢

3. **投資建議**：針對不同類型的投資者（保守型/穩健型/積極型）提供具體的買賣建議

4. **風險提示**：指出當前市場的主要風險因素和需要關注的事項

請用繁體中文回答，語氣專業但易懂，適合一般投資者閱讀。
"""
        return prompt
    
    async def analyze_with_gemini(
        self, 
        current_data: Dict[str, Any], 
        statistics: Dict[str, Any],
        trend: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """使用Gemini進行AI分析"""
        
        if not self.model:
            logger.warning("Gemini模型未初始化，使用模擬分析")
            return self._mock_analysis(current_data, statistics, trend)
        
        try:
            prompt = self.create_analysis_prompt(current_data, statistics, trend)
            
            logger.info(f"[{self.name}] 發送分析請求到Gemini...")
            response = self.model.generate_content(prompt)
            
            # 解析回應
            analysis_text = response.text
            
            # 嘗試分段解析（基於標題）
            sections = self._parse_analysis_sections(analysis_text)
            
            logger.info(f"[{self.name}] Gemini分析完成")
            return sections
            
        except Exception as e:
            logger.error(f"Gemini分析失敗: {str(e)}")
            return self._mock_analysis(current_data, statistics, trend)
    
    def _parse_analysis_sections(self, text: str) -> Dict[str, str]:
        """解析AI分析結果的各個部分"""
        sections = {
            "market_analysis": "",
            "trend_prediction": "",
            "investment_advice": "",
            "risk_warning": ""
        }
        
        # 簡單的分段邏輯
        keywords = {
            "market_analysis": ["市場分析", "1.", "**1."],
            "trend_prediction": ["趨勢預測", "2.", "**2."],
            "investment_advice": ["投資建議", "3.", "**3."],
            "risk_warning": ["風險提示", "4.", "**4."]
        }
        
        current_section = None
        lines = text.split('\n')
        
        for line in lines:
            # 檢查是否是新章節
            for section, keys in keywords.items():
                if any(key in line for key in keys):
                    current_section = section
                    break
            
            # 添加內容到當前章節
            if current_section and line.strip():
                sections[current_section] += line + "\n"
        
        # 如果解析失敗，把全部內容放到市場分析
        if not any(sections.values()):
            sections["market_analysis"] = text
        
        return sections
    
    def _mock_analysis(
        self, 
        current_data: Dict[str, Any], 
        statistics: Dict[str, Any],
        trend: Dict[str, Any]
    ) -> Dict[str, str]:
        """模擬AI分析（當Gemini不可用時）"""
        
        gold_price = current_data.get('gold_price', 0)
        gold_avg = statistics['gold']['avg']
        gold_trend = trend['gold_trend']
        
        silver_price = current_data.get('silver_price', 0)
        silver_avg = statistics['silver']['avg']
        silver_trend = trend['silver_trend']
        
        return {
            "market_analysis": f"""
當前金價為 {gold_price} TWD/錢，{'高於' if gold_price > gold_avg else '低於'}月平均 {gold_avg} TWD/錢。
當前銀價為 {silver_price} TWD/錢，{'高於' if silver_price > silver_avg else '低於'}月平均 {silver_avg} TWD/錢。
市場整體呈現{'偏多' if gold_trend == '上升' else '偏空' if gold_trend == '下降' else '震盪'}格局。
""",
            "trend_prediction": f"""
基於過去30天的數據分析，金價呈現{gold_trend}趨勢，銀價呈現{silver_trend}趨勢。
預計短期內金價將在 {statistics['gold']['min']}-{statistics['gold']['max']} 區間波動。
銀價則可能在 {statistics['silver']['min']}-{statistics['silver']['max']} 範圍內整理。
""",
            "investment_advice": f"""
保守型投資者：建議觀望為主，等待價格回落至月平均以下再考慮分批買入。
穩健型投資者：可在當前價位小量建倉，並設定止損點。
積極型投資者：可根據短期趨勢進行波段操作，但需控制倉位。
""",
            "risk_warning": f"""
1. 國際金價波動可能影響台灣市場
2. 匯率變動風險需要關注
3. 當前價格波動標準差為 {statistics['gold']['std']}，屬於{'高波動' if statistics['gold']['std'] > 200 else '正常波動'}
4. 建議分散投資，不要過度集中於單一貴金屬
"""
        }
    
    def save_analysis(self, analysis: Dict[str, str], db: Session) -> Optional[AIAnalysisRecord]:
        """保存AI分析結果到數據庫"""
        try:
            record = AIAnalysisRecord(
                timestamp=datetime.now(),
                analysis_type="comprehensive",
                market_analysis=analysis["market_analysis"],
                trend_prediction=analysis["trend_prediction"],
                investment_advice=analysis["investment_advice"],
                risk_warning=analysis["risk_warning"],
                model_name=self.model_name,
                confidence_score=0.85  # 可以根據模型輸出調整
            )
            
            db.add(record)
            db.commit()
            db.refresh(record)
            
            logger.info(f"[{self.name}] AI分析已保存, ID={record.id}")
            return record
            
        except Exception as e:
            logger.error(f"保存AI分析失敗: {str(e)}")
            db.rollback()
            return None
    
    async def run(
        self, 
        current_data: Dict[str, Any], 
        statistics: Dict[str, Any],
        trend: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """執行完整的AI分析流程"""
        logger.info(f"[{self.name}] 開始AI分析...")
        
        # 1. 使用Gemini進行分析
        analysis = await self.analyze_with_gemini(current_data, statistics, trend)
        
        if not analysis:
            logger.error("AI分析失敗")
            return {}
        
        # 2. 保存分析結果
        record = self.save_analysis(analysis, db)
        
        result = {
            "analysis_id": record.id if record else None,
            **analysis
        }
        
        logger.info(f"[{self.name}] AI分析完成")
        return result


# 創建全域實例
ai_analyzer = AIAnalyzerAgent()
