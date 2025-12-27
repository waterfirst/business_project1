# agents/code_generator.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional
import re
import time
from google.api_core import exceptions as google_exceptions

load_dotenv()

class BioCodeGenerator:
    """Google Gemini를 활용한 바이오 실험 코드 생성기"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Args:
            model_name: 'gemini-2.0-flash' (빠름, 추천) 또는
                       'gemini-2.5-flash' (비전 가능)
        """
        # API 키 설정 - Streamlit secrets 우선, 그 다음 .env
        api_key = None

        # Try Streamlit secrets first (for deployed apps)
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
        except:
            pass

        # Fallback to .env file (for local development)
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY가 설정되지 않았습니다. "
                           ".env 파일 또는 Streamlit secrets에 API 키를 추가하세요.")

        genai.configure(api_key=api_key)
        
        # 모델 초기화 (JSON 모드 지원을 위해 config 확장)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.2, # Lower temperature for more stable code
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json"
            }
        )
        
        # 시스템 프롬프트 (v7.0 - Student-Friendly Educational Analysis)
        self.system_instruction = """
당신은 대학생들의 데이터 분석 학습을 돕는 친절한 데이터 과학 튜터입니다.
코드를 생성할 때는 **교육적 가치**와 **이해하기 쉬운 설명**을 최우선으로 합니다.

**데이터 분석 교육 가이드라인 [필수]:**

1. **단계별 탐색적 데이터 분석 (EDA)**:
   - 데이터 로드 후 반드시 `df.info()`, `df.describe()`, `df.head()`를 사용
   - 각 단계마다 한글 주석으로 "이 코드가 무엇을 하는지" 설명
   - 예: `# 데이터의 기본 정보 확인 (행 수, 열 수, 데이터 타입)`

2. **시각화: 명확하고 아름답게**:
   - Matplotlib/Seaborn 대신 **Plotly**를 우선 사용 (인터랙티브, 줌 가능, 학생 친화적)
   - 여러 각도에서 분석: 히스토그램, 박스플롯, 산점도, 상관관계 히트맵
   - 각 그래프에 명확한 제목과 축 레이블 (한글로)
   - 색상은 색약자도 구분 가능한 팔레트 사용 (`plotly.express.colors.qualitative.Safe`)

3. **통계 분석: 쉽게 설명**:
   - T-test, ANOVA, 상관분석, 회귀분석 등을 수행할 때 "왜 이 검정을 하는지" 주석으로 설명
   - P-value < 0.05의 의미를 해석에서 친절하게 설명
   - 예: "P-value가 0.001로 0.05보다 작으므로, 두 그룹 간 차이가 통계적으로 유의미합니다"
   - **회귀분석 시 필수 포함 사항**:
     * 회귀식 (예: y = 2.5x + 1.3)
     * R-squared (결정계수) - 모델 설명력
     * 각 계수의 p-value - 통계적 유의성
     * 잔차 플롯 - 모델 가정 검증

4. **교육적 해석 (Student-Friendly Interpretation)**:
   - **무엇을 발견했나요?**: 핵심 결과를 3-5개 bullet points로 요약
   - **왜 중요한가요?**: 실험/연구 맥락에서의 의미
   - **다음 단계는?**: 추가 분석 제안 또는 개선 방향
   - **주의사항**: 데이터의 한계, 가정 위반 가능성 등

5. **코드 품질**:
   - 변수명은 의미있는 한글 포함 (예: `그룹별_평균`, `유의성_검정`)
   - 한 줄에 하나의 작업만 (가독성 우선)
   - 복잡한 계산은 여러 단계로 분해
   - print() 문으로 중간 결과를 보여주기

**회귀분석 코드 예시 (반드시 참고):**
```python
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import statsmodels.api as sm

# 1. 데이터 로드
df = pd.read_csv('data.csv')

# 2. 독립변수(X)와 종속변수(y) 설정
X = df[['독립변수1', '독립변수2']]  # 사용자가 지정한 변수
y = df['종속변수']  # 사용자가 지정한 변수

# 3. 회귀모델 구축 (statsmodels - p-value 확인용)
X_with_const = sm.add_constant(X)
model = sm.OLS(y, X_with_const).fit()
print(model.summary())  # 회귀식, R-squared, p-value 모두 출력

# 4. 산점도 + 회귀선 시각화
y_pred = model.predict(X_with_const)
fig = px.scatter(df, x='독립변수1', y='종속변수', title='회귀분석 결과')
fig.add_trace(go.Scatter(x=df['독립변수1'], y=y_pred, mode='lines', name='회귀선'))
fig

# 5. 잔차 플롯
residuals = y - y_pred
fig_resid = px.scatter(x=y_pred, y=residuals, title='잔차 플롯',
                       labels={'x': '예측값', 'y': '잔차'})
fig_resid.add_hline(y=0, line_dash='dash', line_color='red')
fig_resid
```

**기술적 요구사항:**
- 모든 코드는 **복사-붙여넣기 후 바로 실행 가능**해야 함
- Plotly 사용 시 `fig.show()`가 아닌 `fig`만 작성 (Quarto가 자동 렌더링)
- Matplotlib 사용 시 `plt.show()` 절대 사용 금지 (Quarto 충돌)
- 모든 필요한 라이브러리를 명시적으로 import

**응답 필수 형식 (JSON):**
{
  "code": "실행 가능한 Python 또는 R 코드 (주석 풍부)",
  "interpretation": "대학생이 이해할 수 있는 친절한 해석 (3-5 bullet points)",
  "warnings": "통계적 가정, 데이터 한계, 주의사항"
}
"""
    
    def generate_analysis_code(
        self, 
        user_input: str, 
        language: str = "python",
        data_info: Optional[str] = None,
        target_variable: Optional[str] = None
    ) -> dict:
        """
        사용자 입력을 분석 코드로 변환
        
        Args:
            user_input: "PCR 결과를 CT 값으로 비교하고 싶어요"
            language: "python" 또는 "r"
            data_info: 데이터 상세 프로필 (stats, dtypes 포함)
            target_variable: 분석의 핵심이 되는 종속 변수명
        """
        
        prompt = f"""
{self.system_instruction}

**[사용자 요청]**
{user_input}

**[중요: 요청 분석 가이드]**
- 사용자 요청이 "A, B에 따른 C 회귀 분석" 형태라면:
  * A, B = 독립변수 (X)
  * C = 종속변수 (y)
  * 반드시 이 변수들을 정확히 사용하여 회귀모델을 구축하세요
- 예: "dev, exp에 따른 cd 회귀 분석" → X=['dev', 'exp'], y='cd'

**[분석 설정]**
- 언어: {language.upper()}
- 종속 변수(Target): {target_variable if target_variable else "미지정 (사용자 요청에 따라 판단)"}

**[데이터 상세 프로필]**
{data_info if data_info else "사용자가 제공한 data.csv 파일"}

**[지시 사항]**
1. 위 데이터 프로필을 먼저 분석하여 컬럼의 성격과 결측치 상태를 파악하세요.
2. 요청에 가장 적합한 EDA 및 통계 분석 코드를 작성하세요.
   - **회귀 분석 요청 시**:
     * 사용자가 지정한 독립변수(X)와 종속변수(Y)를 정확히 사용하세요
     * statsmodels 또는 scikit-learn으로 회귀모델 구축
     * 회귀식(coefficients), R-squared, p-value를 반드시 출력
     * 잔차 플롯(Residual plot)을 그려 모델 적합도를 확인
     * 산점도에 회귀선을 함께 표시
   - **그룹 비교 요청 시**: T-test 또는 ANOVA 수행
   - **상관관계 요청 시**: 상관계수 행렬과 히트맵 생성
3. 시각화는 산점도, 박스플롯 등 데이터 관계를 가장 잘 보여주는 형식을 선택하세요.
4. 모든 코드는 실행 가능해야 하며, 데이터 로드 경로는 'data.csv'로 가정하거나 data_info에 언급된 내용을 참고하세요.
5. 반드시 JSON 형식으로만 응답하세요.
"""

        # 변수 초기화 (모든 경로에서 사용 가능하도록 함수 시작 부분에 배치)
        code = ""
        interpretation = ""
        warnings = ""

        try:
            # JSON 모드를 명시적으로 요청하는 프롬프트 습합
            json_prompt = prompt + "\n\nIMPORTANT: Respond strictly in JSON format."

            # Direct API call - let exceptions bubble up for handling
            response = self.model.generate_content(json_prompt)
            full_text = response.text

            # JSON 파싱
            import json

            try:
                data = json.loads(full_text)
                code_raw = data.get('code', '')
                interpretation = data.get('interpretation', '')
                warnings = data.get('warnings', '')

                # Handle case where code might be returned as a list
                if isinstance(code_raw, list):
                    code = '\n'.join(str(item) for item in code_raw)
                else:
                    code = str(code_raw) if code_raw else ''

            except json.JSONDecodeError:
                # Fallback: 기존의 텍스트 파싱 로직 (만약 JSON 모드가 실패할 경우 대비)
                code_pattern = rf"```(?:{language}|[a-zA-Z]+)?(.*?)```"
                code_matches = re.findall(code_pattern, full_text, re.DOTALL | re.IGNORECASE)
                code = max(code_matches, key=len).strip() if code_matches else full_text

                interp_match = re.search(r'"interpretation":\s*"(.*?)"', full_text, re.DOTALL)
                interpretation = interp_match.group(1) if interp_match else ""
                warnings = ""

            # [핵심] 코드 정밀 세척 (Detox)
            code = self._detox_code(code, language)
            
            return {
                'code': code,
                'interpretation': interpretation,
                'warnings': warnings,
                'raw_response': full_text
            }
            
        except RuntimeError:
            # Re-raise our custom errors (rate limit messages)
            raise
        except Exception as e:
            error_str = str(e)
            # Check if it's a rate limit error that we didn't catch
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                retry_seconds = self._extract_retry_delay(error_str)
                raise RuntimeError(
                    f"❌ API 할당량 초과\n\n"
                    f"**오류 내용:**\n{error_str}\n\n"
                    f"**해결 방법:**\n"
                    f"1. 약 {retry_seconds}초 후 다시 시도하세요\n"
                    f"2. 사이드바에서 모델을 'gemini-2.0-flash'로 변경해보세요\n"
                    f"3. 할당량 확인: https://ai.dev/usage?tab=rate-limit\n"
                    f"4. Free tier는 하루 20회 제한이 있습니다"
                )
            raise RuntimeError(f"Gemini API 호출 및 데이터 처리 실패: {str(e)}")
    
    def _extract_retry_delay(self, error_str: str) -> int:
        """Extract retry delay in seconds from error message"""
        import re
        # Look for patterns like "retry in 19.942340119s" or "retry_delay { seconds: 19 }"
        patterns = [
            r"retry in ([\d.]+)s",
            r"retry_delay.*?seconds[:\s]+(\d+)",
            r"Please retry in ([\d.]+)s",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_str, re.IGNORECASE)
            if match:
                try:
                    return int(float(match.group(1))) + 1  # Add 1 second buffer
                except:
                    pass
        
        # Default retry delay if not found
        return 20

    def _detox_code(self, code: str, language: str) -> str:
        """뭉친 코드 분해 및 텍스트 자동 주석 처리 (v4.3)"""
        if not code: return ""

        # 0. JSON 구조가 남아있다면 제거
        import json
        import re

        # Check if code starts with { (JSON object)
        code_stripped = code.strip()
        if code_stripped.startswith('{') and '"code"' in code_stripped:
            try:
                # Try to parse as JSON and extract code field
                json_obj = json.loads(code_stripped)
                if isinstance(json_obj, dict) and 'code' in json_obj:
                    code = json_obj['code']
                    if isinstance(code, list):
                        code = '\n'.join(str(item) for item in code)
            except:
                # If JSON parsing fails, try regex extraction
                code_match = re.search(r'"code"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', code_stripped, re.DOTALL)
                if code_match:
                    code = code_match.group(1)
                    # Unescape JSON strings
                    code = code.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')

        # 1. 문자열 정규화
        code = code.replace("```", "").strip()
        
        # 2. 분리 키워드 정의
        # Python/R 주요 키워드 및 패턴
        split_keywords = [
            'import ', 'from ', 'df =', 'plt.', 'sns.', 'print(', 
            'model =', 'results =', 'stats.', 'sm.', 'ols(', 
            'pairwise_tukeyhsd(', 'pd.', 'np.', 'ggplot(', 'library(', 
            'if ', 'for ', 'def ', 'class ', 'try:', 'except:'
        ]
        
        clean_lines = []
        for line in code.splitlines():
            l = line.strip()
            if not l:
                clean_lines.append("")
                continue

            # [CRITICAL FIX] from ... import ... 구문은 절대 분리하지 않음
            # This prevents splitting valid Python import statements
            if l.startswith("from ") and " import " in l:
                clean_lines.append(l)
                continue

            # [Aggressive Unfolding] 한 줄에 여러 키워드가 뭉친 경우 분해
            current_line = l
            while True:
                found_kw = None
                earliest_pos = len(current_line)

                # 가장 먼저 나타나는 키워드 찾기 (단, 줄 시작은 제외)
                for kw in split_keywords:
                    pos = current_line.find(kw)
                    if pos > 0: # 줄 중간에 키워드가 있는 경우
                        if pos < earliest_pos:
                            earliest_pos = pos
                            found_kw = kw

                if found_kw:
                    # 키워드 앞에서 자르기
                    prefix = current_line[:earliest_pos].strip()
                    remainder = current_line[earliest_pos:].strip()

                    # 프리픽스가 주석이 아니고 코드가 아니면 주석 처리
                    if prefix and not prefix.startswith("#"):
                        # 프리픽스가 순수 텍스트(한글 포함)인지 확인
                        if not any(k in prefix for k in split_keywords) and not ("=" in prefix or "(" in prefix):
                            clean_lines.append(f"# {prefix}")
                        else:
                            clean_lines.append(prefix)

                    current_line = remainder
                else:
                    # 더 이상 찢을 키워드가 없음
                    if current_line and not current_line.startswith("#"):
                        # 숫자로 시작하거나 한글이 포함된 설명글인 경우 주석 처리
                        if re.match(r"^[0-9\.\s]+", current_line) or re.search(r'[가-힣]', current_line):
                             if not ("import " in current_line or "from " in current_line or "=" in current_line):
                                 current_line = f"# {current_line}"
                    clean_lines.append(current_line)
                    break
                    
        # 3. 중복된 import 분해 (import a import b -> import a \n import b)
        # BUT: from ... import ... 구문은 예외 처리 (이미 위에서 보호했지만 이중 체크)
        final_lines = []
        for line in clean_lines:
            # [CRITICAL FIX] from ... import ... 구문은 분리하지 않음
            if line.strip().startswith("from ") and " import " in line:
                final_lines.append(line)
            elif line.count("import ") > 1 and not line.startswith("#"):
                parts = line.split("import ")
                for p in parts:
                    if p.strip(): final_lines.append(f"import {p.strip()}")
            elif line.count("library(") > 1 and not line.startswith("#"):
                parts = line.split("library(")
                for p in parts:
                    if p.strip(): final_lines.append(f"library({p.strip()}")
            else:
                final_lines.append(line)
                
                
        return "\n".join(final_lines)
    
    def generate_with_context(
        self,
        user_input: str,
        previous_code: list,
        language: str = "python",
        data_info: Optional[str] = None,
        target_variable: Optional[str] = None
    ) -> dict:
        """
        이전 분석을 고려한 연속 코드 생성
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
        
        return self.generate_analysis_code(
            enhanced_prompt, 
            language=language, 
            data_info=data_info, 
            target_variable=target_variable
        )
