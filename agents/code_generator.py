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
        
        # 시스템 프롬프트
        self.system_instruction = """
당신은 생명과학 실험 데이터 분석 전문가입니다.
사용자의 자연어 설명을 **실행 가능한** R 또는 Python 코드로 변환합니다.

**핵심 분석 가이드라인:**
1. 코드는 반드시 유효한 Python/R 문법이어야 함
2. 모든 설명(예: "1. 라이브러리 임포트")은 반드시 주석(#)으로 처리하거나 코드 블록 밖에 작성
3. 한 줄에 하나의 명령문만 작성 (절대 여러 import를 한 줄에 나열하지 말 것)
4. 데이터 로드는 반드시 `df = pd.read_csv('data.csv')` 형식을 따를 것

**응답 필수 형식 (JSON):**
반드시 아래 키를 포함한 유효한 JSON 객체로만 응답하세요:
{
  "code": "실행 가능한 분석 코드 (개행 필수, 뭉치지 말 것)",
  "interpretation": "분석 결과에 대한 전문가적 해석",
  "warnings": "분석 시 주의사항"
}
JSON 외의 다른 텍스트는 절대 포함하지 마세요.
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
            # JSON 모드를 명시적으로 요청하는 프롬프트 습합
            json_prompt = prompt + "\n\nIMPORTANT: Respond strictly in JSON format."
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
            
        except Exception as e:
            raise RuntimeError(f"Gemini API 호출 및 데이터 처리 실패: {str(e)}")

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
