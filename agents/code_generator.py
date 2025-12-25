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
1. 코드는 Quarto 문서(.qmd)에서 실행되므로 반드시 유효한 구문만 포함
2. 통계 검정 시 반드시 가정 검증 단계 포함 (정규성, 등분산성)
3. 시각화는 publication-quality로 (가독성 높은 폰트와 레이블)
4. 모든 코드는 반드시 주석(#)을 포함하여 줄바꿈을 지키며 작성
5. 데이터 파일명은 'data.csv'로 가정
6. 다른 설명 텍스트는 절대 코드 블록 안에 넣지 말 것

**응답 형식:**
반드시 아래 형식의 마크다운 블록으로 응답하세요:

1. **코드:**
```{언어}
# 여기에 순수 코드만 작성 (설명 텍스트 포함 금지)
```

2. **해석:**
결과 분석 요약
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
            
            # [단계 1] 백틱 블록 추출 (가장 우선)
            code_pattern = rf"```(?:{language}|[a-zA-Z]+)?(.*?)```"
            code_matches = re.findall(code_pattern, full_text, re.DOTALL | re.IGNORECASE)
            
            if code_matches:
                # 가장 긴 블록을 코드로 선택 (가장 완전할 가능성이 높음)
                code = max(code_matches, key=len).strip()
            else:
                # [단계 2] 백틱이 없는 경우 "코드:" 섹션 이후부터 "해석:" 이전까지 추출
                sect_pattern = r"\*\*코드:\*\*(.*?)(?:\*\*해석:\*\*|$)"
                sect_match = re.search(sect_pattern, full_text, re.DOTALL | re.IGNORECASE)
                if sect_match:
                    code = sect_match.group(1).strip()
                else:
                    # [단계 3] 최후의 수단: 전체 텍스트
                    code = full_text.strip()
            
            # [단계 4] 코드 정제 (남은 마커 제거 및 개행 복구)
            # 모든 유형의 백틱/언어 마커 제거
            code = re.sub(r"```[a-zA-Z]*", "", code)
            code = code.replace("```", "").strip()
            
            # [결정적 해결] 플랫폼 독립적 개행 및 공백 처리
            # 1. 모든 개행문자를 \n으로 통합
            # 2. mashed lines 방지를 위해 각 라인을 개별 처리
            clean_lines = []
            for line in code.splitlines():
                l = line.strip()
                if l:
                    # "1. 라이브러리 임포트" 같은 텍스트가 코드 줄에 섞여 있는 경우 주석 처리 감지
                    # 만약 줄이 숫자로 시작하고 코드가 아닌 것 같으면 주석 처리
                    if re.match(r"^\d+\.", l) and not ("import " in l or "=" in l or "(" in l):
                        l = f"# {l}"
                    clean_lines.append(l)
                else:
                    clean_lines.append("")
            
            code = "\n".join(clean_lines)
            
            # [단계 5] 해석/주의사항 추출
            interpretation = ""
            interp_match = re.search(r"\*\*해석:\*\*(.*?)(?:\*\*주의사항:\*\*|$)", full_text, re.DOTALL | re.IGNORECASE)
            if interp_match:
                interpretation = interp_match.group(1).strip()
            
            warnings = ""
            warn_match = re.search(r"\*\*주의사항:\*\*(.*?)$", full_text, re.DOTALL | re.IGNORECASE)
            if warn_match:
                warnings = warn_match.group(1).strip()
            
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
