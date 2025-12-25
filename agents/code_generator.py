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

**핵심 분석 가이드라인:**
1. 코드는 반드시 유효한 Python/R 문법이어야 함
2. 모든 설명(예: "1. 라이브러리 임포트")은 반드시 주석(#)으로 처리하거나 코드 블록 밖에 작성
3. 한 줄에 하나의 명령문만 작성 (절대 여러 import를 한 줄에 나열하지 말 것)
4. 데이터 로드는 반드시 `df = pd.read_csv('data.csv')` 형식을 따를 것

**응답 필수 형식 (Few-Shot):**
1. **코드:**
```{언어}
# 1. 라이브러리 로드
import pandas as pd
import seaborn as sns

# 2. 데이터 분석
df = pd.read_csv('data.csv')
print(df.describe())
```

2. **해석:**
분석 결과에 대한 전문가적 견해
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
            
            # [단계 1] 마크다운 코드 블록 추출
            code_pattern = rf"```(?:{language}|[a-zA-Z]+)?(.*?)```"
            code_matches = re.findall(code_pattern, full_text, re.DOTALL | re.IGNORECASE)
            code = max(code_matches, key=len).strip() if code_matches else full_text
            
            # [단계 2] 불필요한 마커 제거
            code = re.sub(r"```[a-zA-Z]*", "", code)
            code = code.replace("```", "").strip()
            
            # [단계 3] Mash-Unfolder: 한 줄에 뭉친 코드 분리 및 텍스트 주석 처리
            clean_lines = []
            for line in code.splitlines():
                l = line.strip()
                if not l:
                    clean_lines.append("")
                    continue
                
                # 1. "1. 제목 import ..." 패턴 처리: 제목과 코드를 강제 분리
                # 'import', 'from', 'df =', 'plt.' 등의 키워드 앞에서 줄바꿈 시도
                split_keywords = ['import ', 'from ', 'df =', 'plt.', 'sns.', 'print(', 'model =', 'results =']
                for kw in split_keywords:
                    if kw in l and not l.startswith(kw) and not l.startswith("#"):
                        # 키워드 앞에서 자름
                        parts = l.split(kw, 1)
                        header = parts[0].strip()
                        body = kw + parts[1]
                        
                        # 헤더가 있고 주석이 아니면 주석처리
                        if header and not header.startswith("#"):
                            clean_lines.append(f"# {header}")
                        l = body # 남은 부분으로 계속 처리
                
                # 2. 숫자형 리스트(1. 2. ...) 및 설명 텍스트 주석 처리
                if re.match(r"^\d+\.", l) and not l.startswith("#"):
                    l = f"# {l}"
                
                # 3. 한 줄에 여러 import가 붙어 있는 경우 (결정적 해결)
                # 'import pandas as pd import numpy as np' -> 분리
                if "import " in l and l.count("import ") > 1:
                    sub_parts = l.split("import ")
                    for p in sub_parts:
                        if p.strip():
                            clean_lines.append(f"import {p.strip()}")
                    continue

                clean_lines.append(l)
            
            final_code = "\n".join(clean_lines)
            
            # [단계 4] 결과 해석 추출
            interp_match = re.search(r"\*\*해석:\*\*(.*?)(?:\*\*주의사항:\*\*|$)", full_text, re.DOTALL | re.IGNORECASE)
            interpretation = interp_match.group(1).strip() if interp_match else ""
            
            warn_match = re.search(r"\*\*주의사항:\*\*(.*?)$", full_text, re.DOTALL | re.IGNORECASE)
            warnings = warn_match.group(1).strip() if warn_match else ""
            
            return {
                'code': final_code,
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
