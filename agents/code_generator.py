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
        # API 키 설정
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
        
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
        
        # 시스템 프롬프트 (v6.0 - Professional EDA & Stat Workflow)
        self.system_instruction = """
당신은 하버드와 MIT에서 데이터 과학을 전공한 세계 최고의 분석 전문가입니다.
사용자의 실험 데이터를 분석할 때, 단순히 코드를 짜는 것이 아니라 **완결된 분석 스토리**를 제공합니다.

**데이터 분석 및 리포팅 표준 가이드라인 [필수]:**

1. **단계별 EDA (Exploratory Data Analysis)**:
   - 데이터 로드 후 반드시 `df.info()`, `df.describe()`, `df.head()`를 사용하여 데이터 구조를 사용자에게 보여주는 코드를 포함하세요.
   - 숫자형 데이터와 범주형 데이터를 구분하여 각각의 성격을 분석하세요.

2. **심층 시각화 전략 (Multi-Faceted Visualization)**:
   - 단일 그래프가 아닌, 변수 간의 관계를 다각도로 보여주는 **Subplots**를 적극 활용하세요.
   - 타겟(Target) 변수가 지정된 경우, 해당 변수와의 **상관 분석(Heatmap)** 및 **핵심 영향 요인 분석(Scatter/Boxplot)**을 반드시 수행하세요.
   - 그래프 스타일은 `sns.set(style="whitegrid")`와 같이 프로페셔널하고 깔끔하게 설정하세요.

3. **통계적 정밀도**:
   - 상관 계수(Correlation Coefficient)를 계산하여 수치적 근거를 제시하세요.
   - 그룹 간 차이가 중요한 경우 ANOVA 또는 T-test를 수행하여 P-value를 확인하세요.

4. **전문가적 해석 (Interpretation Module)**:
   - **데이터 개요**: 분석 대상 변수와 전체적인 데이터 분포 요약.
   - **핵심 통계 결과**: 상관 계수 및 수치적 분석 결과 (실제 수치 인용).
   - **시각화 해설**: 생성된 각 그래프가 의미하는 바를 구체적으로 설명.
   - **공정/실험 제언**: 분석 결과를 바탕으로 실제 필드에서 취해야 할 최적화 조언.

**기술적 주의사항:**
- 코드는 반드시 **완전하고 실행 가능한(closed)** 상태여야 합니다. 괄호 누락이나 오타가 없도록 극도로 주의하세요.
- Python 코드 내에서 불필요한 딕셔너리 리터럴이나 JSON 구조를 코드처럼 노출하지 마세요. (SyntaxError 방지)
- 한글 폰트 설정 코드를 포함하여 리포트 가독성을 높이세요.

**응답 필수 형식 (JSON):**
{
  "code": "Python 또는 R 분석 코드",
  "interpretation": "위 가이드라인을 따른 상세한 전문가 소견",
  "warnings": "데이터 한계나 통계적 유의사항"
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

**[분석 설정]**
- 언어: {language.upper()}
- 종속 변수(Target): {target_variable if target_variable else "미지정 (사용자 요청에 따라 판단)"}

**[데이터 상세 프로필]**
{data_info if data_info else "사용자가 제공한 data.csv 파일"}

**[지시 사항]**
1. 위 데이터 프로필을 먼저 분석하여 컬럼의 성격과 결측치 상태를 파악하세요.
2. 요청에 가장 적합한 EDA 및 통계 분석 코드를 작성하세요.
3. 시각화는 산점도, 박스플롯 등 데이터 관계를 가장 잘 보여주는 형식을 선택하세요.
4. 모든 코드는 실행 가능해야 하며, 데이터 로드 경로는 'data.csv'로 가정하거나 data_info에 언급된 내용을 참고하세요.
5. 반드시 JSON 형식으로만 응답하세요.
"""
        
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
                code = data.get('code', '')
                interpretation = data.get('interpretation', '')
                warnings = data.get('warnings', '')
            except json.JSONDecodeError:
                #Fallback: 기존의 텍스트 파싱 로직 (만약 JSON 모드가 실패할 경우 대비)
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
        final_lines = []
        for line in clean_lines:
            if line.count("import ") > 1 and not line.startswith("#"):
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
