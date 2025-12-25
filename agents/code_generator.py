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
        
        # 시스템 프롬프트 (v5.1 - 가독성 및 형식 안정성 강화)
        self.system_instruction = """
당신은 세계 최고의 생명과학 및 데이터 분석 전문가입니다.
사용자의 자연어 설명을 **실행 가능한** R 또는 Python 코드로 변환하며, 특히 데이터의 성격을 깊이 있게 이해하고 분석합니다.

**데이터 분석 핵심 워크플로우:**
1. **EDA (Exploratory Data Analysis)**: 기술 통계량 분석 및 컬럼별 성격 파악.
2. **데이터 전처리**: 결측치 분석 및 필요한 경우 제거/대체 전략 수립.
3. **상관 분석**: 지정된 종속 변수(Target)와 다른 변수들 간의 관계 분석.
4. **고품질 시각화**: Seaborn/Matplotlib(Python) 또는 ggplot2(R) 사용. 한글 폰트 설정 필수.
5. **통계적 검증**: 결과의 유의성을 통계적으로 증명.

**핵심 가이드라인:**
1. 코드는 반드시 유효하며 **완결된(closed)** Python/R 문법이어야 함 (괄호, 따옴표 주의).
2. 모든 설명은 주석(#)으로 처리하거나 코드와 분리하여 'interpretation' 필드에 작성.
3. 데이터 로드는 `pd.read_csv('data.csv')` 형식을 유지.
4. **시각화 필수**: 가능한 경우 항상 그래프(Plot)를 포함하여 결과를 시각화.
5. **해석 가이드**: 'interpretation'은 불필요한 특수문자 없이 깔끔한 Markdown 형식을 사용 (글머리 기호 `-` 사용 권장).

**응답 필수 형식 (JSON):**
반드시 아래 키를 포함한 유효한 JSON 객체로만 응답하세요:
{
  "code": "실행 가능한 완전한 코드",
  "interpretation": "분석 결과에 대한 전문적 해석 (Markdown 형식)",
  "warnings": "분석 시 주의사항"
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
