# agents/vision_analyzer.py
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiVisionAnalyzer:
    """Gemini Vision으로 실험 이미지 분석"""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_gel_electrophoresis(self, image_path: str) -> dict:
        """젤 전기영동 이미지 분석"""
        
        image = Image.open(image_path)
        
        prompt = """
이 젤 전기영동(Gel Electrophoresis) 이미지를 분석하세요.

다음 내용을 포함하세요:
1. 관찰되는 밴드(band) 수
2. 각 레인(lane)별 밴드 위치와 선명도
3. 양성/음성 대조군 확인
4. 실험 품질 평가 (Good/Fair/Poor)
5. 개선 제안사항

형식:
**밴드 분석:**
- Lane 1: ...
- Lane 2: ...

**품질 평가:** Good/Fair/Poor

**제안사항:**
- ...
"""
        
        response = self.model.generate_content([prompt, image])
        
        return {
            'raw_analysis': response.text,
            'image_path': image_path
        }
    
    def analyze_cell_plate(self, image_path: str) -> dict:
        """세포 배양 플레이트 이미지 분석"""
        
        image = Image.open(image_path)
        
        prompt = """
이 세포 배양 플레이트 이미지를 분석하세요.

다음을 확인하세요:
1. 웰(well) 개수 및 레이아웃
2. 세포 밀도 (confluency) - 각 웰별
3. 오염 징후 (contamination) 유무
4. 세포 형태 이상 여부
5. 권장 계대 배양 시기

형식:
**레이아웃:** 96-well plate / 24-well plate 등

**세포 밀도:**
- Well A1: 80% confluent
- Well A2: ...

**오염 여부:** 확인됨/없음

**권장사항:** ...
"""
        
        response = self.model.generate_content([prompt, image])
        
        return {
            'raw_analysis': response.text,
            'image_path': image_path
        }
