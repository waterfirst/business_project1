# agents/code_generator.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional
import re

load_dotenv()

class BioCodeGenerator:
    """Google Gemini를 활용한 바이오 실험 코드 생성기"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Args:
            model_name: 'gemini-2.0-flash' (빠름, 추천) 또는 
                       'gemini-2.5-flash' (비전 가능)
        """
        # API 키 설정
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
        
        genai.configure(api_key=api_key)
        
        # 모델 초기화
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        # 시스템 프롬프트
        self.system_instruction = """
당신은 생명과학 실험 데이터 분석 전문가입니다.
사용자의 자연어 설명을 **실행 가능한** R 또는 Python 코드로 변환합니다.

**핵심 규칙:**
1. 코드는 Quarto 문서(.qmd)에서 실행되므로 청크 형식 준수
2. 통계 검정 시 반드시 가정 검증 단계 포함 (정규성, 등분산성)
3. 시각화는 publication-quality로:
   - Python: plotly 또는 seaborn
   - R: ggplot2 + theme_bw()
4. 주석은 한글로 상세히 작성
5. 데이터 파일명은 'data.csv'로 가정
6. 결과 해석 텍스트도 함께 제공

**응답 형식:**
```{언어}
# 코드 내용
```

**해석:**
통계 결과에 대한 간단한 설명
"""
    
    def generate_analysis_code(
        self, 
        user_input: str, 
        language: str = "python",
        data_info: Optional[str] = None
    ) -> dict:
        """
        사용자 입력을 분석 코드로 변환
        
        Args:
            user_input: "PCR 결과를 CT 값으로 비교하고 싶어요"
            language: "python" 또는 "r"
            data_info: 데이터 구조 정보
        
        Returns:
            {
                'code': '생성된 코드',
                'interpretation': '결과 해석',
                'warnings': '주의사항'
            }
        """
        
        prompt = f"""
{self.system_instruction}

**사용자 요청:**
{user_input}

**분석 언어:** {language.upper()}

**데이터 정보:** {data_info if data_info else "사용자가 제공한 data.csv 파일"}

다음 형식으로 응답하세요:

1. **코드:**
```{language}
# 여기에 완전한 코드
```

2. **해석:**
생성된 분석의 의미와 결과 해석 방법

3. **주의사항:**
실험자가 알아야 할 통계적 가정이나 제약사항
"""
        
        try:
            response = self.model.generate_content(prompt)
            full_text = response.text
            
            # 코드 블록 추출 (v3.0 - 가장 견고한 추출 로직)
            # 1. ```언어 ... ``` 패턴 시도
            code_pattern = rf"```(?:{language}|[a-zA-Z]+)?(.*?)```"
            code_match = re.search(code_pattern, full_text, re.DOTALL | re.IGNORECASE)
            
            if code_match:
                code = code_match.group(1).strip()
            else:
                # 2. 백틱이 하나만 있거나 아예 없는 경우 텍스트 클리닝
                code = full_text.strip()
            
            # [중요] 코드 내부의 중복된 백틱이나 랭귀지 마커를 완전히 제거하여 SyntaxError 원천 차단
            # QuartoRenderer가 다시 감싸기 때문에 여기서는 순수 코드만 남겨야 함
            code = re.sub(rf"```(?:{language}|[a-zA-Z]+)?", "", code)
            code = code.replace("```", "").strip()
            
            # 행 시작부분의 공백 제거 (Quarto 렌더링 안정성)
            code = "\n".join([line.lstrip() for line in code.split("\n")])
            
            # 해석 부분 추출
            interpretation_pattern = r"\*\*해석:\*\*(.*?)(?:\*\*주의사항:\*\*|$)"
            interp_match = re.search(interpretation_pattern, full_text, re.DOTALL)
            interpretation = interp_match.group(1).strip() if interp_match else ""
            
            # 주의사항 추출
            warning_pattern = r"\*\*주의사항:\*\*(.*?)$"
            warn_match = re.search(warning_pattern, full_text, re.DOTALL)
            warnings = warn_match.group(1).strip() if warn_match else ""
            
            return {
                'code': code,
                'interpretation': interpretation,
                'warnings': warnings,
                'raw_response': full_text
            }
            
        except Exception as e:
            raise RuntimeError(f"Gemini API 호출 실패: {str(e)}")
    
    def generate_with_context(
        self,
        user_input: str,
        previous_code: list,
        language: str = "python"
    ) -> dict:
        """
        이전 분석을 고려한 연속 코드 생성
        
        Args:
            previous_code: [{'code': '...', 'caption': '...'}, ...]
        """
        
        context = "\n\n".join([
            f"# 이전 분석 {i+1}: {item['caption']}\n{item['code']}"
            for i, item in enumerate(previous_code[-3:])  # 최근 3개만
        ])
        
        enhanced_prompt = f"""
**이전 분석 내역:**
{context}

**새로운 요청:**
{user_input}

위 분석을 기반으로 다음 단계를 진행하세요.
"""
        
        return self.generate_analysis_code(enhanced_prompt, language)
