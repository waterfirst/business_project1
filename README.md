# 🧬 Bio-Log: Gemini-Powered Bio-Data Analysis Platform

Bio-Log는 Google Gemini 2.5/2.0 Flash 모델을 활용하여 생명과학 실험 데이터를 자동으로 분석하고 전문적인 Quarto 리포트를 생성하는 웹 플랫폼입니다.

## 🚀 주요 기능 (Key Features)

- **AI 코드 생성**: 자연어 요청("그룹별 차이 분석해줘")을 R 또는 Python 분석 코드로 즉시 변환.
- **상세 데이터 프로파일링**: 업로드된 CSV의 데이터 타입, 통계치, 결측치 등을 자동으로 파악하여 AI에 전달.
- **종속 변수(Target) 기반 분석**: 특정 변수를 타겟으로 지정하여 상관 분석 및 시각화 집중 수행.
- **전문가급 리포팅**: Quarto 엔진을 사용하여 분석 코드, 시각화 결과, AI 해석이 포함된 HTML/PDF 리포트 생성.
- **강력한 데이터 검증**: Standard Curve 선형성 검정, 이상치 탐지 등 실험 데이터 품질 관리 도구 내장.

## 📁 프로젝트 구조 (Project Structure)

```text
business_project1/
├── agents/
│   ├── code_generator.py   # Gemini 기반 코드 생성 엔진
│   ├── validator.py        # 데이터 품질 검증 모듈
│   └── vision_analyzer.py  # 비전 기반 이미지 분석 (실험적)
├── utils/
│   ├── data_profiler.py    # 데이터 상세 특성 분석 도구
│   └── quarto_renderer.py  # 전문 리포트 생성 및 렌더링
├── data/                   # 샘플 데이터 보관
├── templates/              # 보고서 템플릿 및 정적 파일
├── app.py                  # Streamlit 메인 어플리케이션
└── requirements.txt        # 의존성 패키지 목록
```

## 🛠️ 시작하기 (Quick Start)

### 1. 환경 설정
Python 3.10+ 환경에서 다음을 설치합니다.

```bash
pip install -r requirements.txt
```

### 2. Quarto 설치
리포트 생성을 위해 [Quarto](https://quarto.org/docs/get-started/) 설치가 필요합니다.
PDF 출력을 원하시면 TinyTeX도 설치해 주세요:
```bash
quarto install tinytex
```

### 3. API 키 설정
`.env` 파일을 생성하고 Google AI Studio에서 발급받은 API 키를 입력합니다.
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. 앱 실행
```bash
streamlit run app.py
```

## 📝 사용 방법 (Usage)

1. **데이터 입력**: CSV 실험 데이터를 업로드합니다.
2. **분석 설정**: 사이드바에서 분석 언어(Python/R)와 종속 변수를 선택합니다.
3. **AI 요청**: "각 그룹의 생존율을 비교하고 ANOVA 분석해줘"와 같이 자연어로 입력합니다.
4. **리포트 생성**: 생성된 코드를 확인하고 '최종 리포트 생성' 탭에서 HTML/PDF로 내려받습니다.

---
*Developed with Advanced Agentic Coding by Antigravity*
