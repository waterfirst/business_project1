# 📊 DataViz Campus

> 대학생을 위한 AI 기반 데이터 분석 학습 플랫폼

![Version](https://img.shields.io/badge/version-4.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🎓 소개

**DataViz Campus**는 통계나 프로그래밍을 처음 배우는 대학생들도 쉽게 데이터 분석을 할 수 있도록 설계된 교육용 플랫폼입니다.

### ✨ 이런 분들에게 추천합니다

- 📚 데이터 분석 수업을 듣는 학부생
- 🔬 실험 데이터를 분석해야 하는 연구실 학생
- 📊 과제나 프로젝트에서 통계 분석이 필요한 학생
- 💡 Python을 배우고 싶지만 어디서부터 시작할지 모르는 학생

### 🚀 주요 기능

| 기능 | 설명 | 장점 |
|------|------|------|
| 🤖 **AI 코드 생성** | 자연어로 요청하면 Python 코드 자동 생성 | 프로그래밍 몰라도 OK |
| 📊 **인터랙티브 시각화** | Plotly로 줌/확대 가능한 그래프 | 탐색적 분석 가능 |
| 📄 **자동 리포트** | HTML/PDF 전문 보고서 생성 | 과제 제출용으로 완벽 |
| 🎓 **교육적 설명** | 통계 용어를 쉽게 해석 | 학습하면서 분석 |
| 💾 **예제 데이터** | 3가지 연습용 데이터셋 제공 | 바로 시작 가능 |

---

## 📥 설치 방법

### 1. 필수 프로그램 설치

#### Python 3.8 이상
```bash
# Windows: python.org에서 다운로드
# Mac:
brew install python

# 설치 확인
python --version
```

#### Quarto CLI
```bash
# Windows: https://quarto.org/docs/get-started/ 에서 다운로드

# Mac
brew install quarto

# Linux
sudo curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb
sudo apt-get install ./quarto-linux-amd64.deb

# 설치 확인
quarto --version
```

### 2. 프로젝트 클론 및 의존성 설치

```bash
# 1. 프로젝트 다운로드
git clone <repository-url>
cd upbeat-kirch

# 2. 가상환경 생성 (권장)
python -m venv venv

# 3. 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. 필요한 패키지 설치
pip install -r requirements.txt
```

### 3. Google API 키 설정 ⚠️ 중요!

1. [Google AI Studio](https://ai.google.dev/)에 접속
2. "Get API Key" 클릭하여 무료 API 키 발급
3. 프로젝트 루트에 `.env` 파일 생성:

```bash
# .env.example 파일을 복사하여 .env로 만들기
# Windows:
copy .env.example .env
# Mac/Linux:
cp .env.example .env
```

4. `.env` 파일을 열어서 발급받은 API 키 입력:
```bash
# .env 파일 내용
GOOGLE_API_KEY=AIzaSy...여기에_발급받은_API_키_전체_붙여넣기
```

**주의**: `.env` 파일은 절대 Git에 커밋하지 마세요! (이미 .gitignore에 포함됨)

### 4. 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱이 실행됩니다!

---

## 🎯 사용 방법

### Step 1: 데이터 준비

#### 옵션 A - 예제 데이터로 연습 (추천)
1. **'예제 & 템플릿'** 탭 클릭
2. 원하는 데이터셋 다운로드:
   - 🎓 학생 성적 데이터 (120명)
   - 🧪 실험 측정 데이터 (80개 샘플)
   - 📊 설문조사 데이터 (200건)
3. 다운로드한 CSV를 **'1단계: 데이터'** 탭에서 업로드

#### 옵션 B - 본인 데이터 사용
1. Excel에서 데이터를 CSV 형식으로 저장
2. **'1단계: 데이터'** 탭에서 업로드

### Step 2: AI에게 분석 요청

1. **'2단계: AI 분석'** 탭으로 이동
2. 템플릿 선택 또는 직접 입력:

```
좋은 예시:
"전공별 중간고사 평균을 비교하고, ANOVA로 유의한 차이가 있는지 검정해주세요"

나쁜 예시:
"분석해줘" ❌ (무엇을 분석할지 불명확)
```

3. **🚀 AI 코드 생성** 버튼 클릭
4. 생성된 코드 확인 및 해석 읽기

### Step 3: 리포트 생성

1. **'3단계: 리포트'** 탭으로 이동
2. 출력 형식 선택:
   - **HTML** (추천): 인터랙티브, 브라우저에서 바로 확인
   - **PDF**: 인쇄용, 제출용
3. 테마 선택 (cosmo, flatly 추천)
4. **📄 최종 리포트 생성** 버튼 클릭
5. 다운로드!

---

## 💡 프롬프트 작성 팁

### ✅ 효과적인 프롬프트

**구체적으로**
```
❌ "그래프 그려줘"
✅ "농도와 흡광도를 scatter plot으로 그리고, 회귀식을 포함해줘"
```

**단계별로**
```
1차 요청: "각 변수의 기술통계를 계산하고 히스토그램을 그려줘"
2차 요청: "이제 그룹별로 ANOVA 검정을 해줘"
```

**시각화 명시**
```
✅ "Plotly로 인터랙티브한 박스플롯을 만들어줘"
✅ "상관관계 히트맵을 그려줘"
```

### 📝 프롬프트 템플릿 모음

#### 기술통계
```
"각 숫자형 변수의 평균, 중앙값, 표준편차를 계산하고 히스토그램으로 분포를 보여줘"
```

#### 그룹 비교
```
"[그룹변수]별로 [측정변수]를 비교하고, 박스플롯으로 시각화한 후 ANOVA로 유의성을 검정해줘"
```

#### 상관분석
```
"모든 숫자형 변수 간 상관관계를 계산하고 히트맵으로 보여줘. 상관계수가 0.5 이상인 변수 쌍을 scatter plot으로 그려줘"
```

#### 회귀분석
```
"[X변수]로 [Y변수]를 예측하는 선형 회귀 모델을 만들고, R-squared와 p-value를 보여줘. 잔차 플롯도 그려줘"
```

---

## 🔬 통계 용어 쉽게 이해하기

### 📊 기술통계

| 용어 | 의미 | 예시 |
|------|------|------|
| **평균** | 모든 값의 합 ÷ 개수 | [70, 80, 90] → 평균 = 80 |
| **중앙값** | 크기 순 정렬 시 가운데 값 | [70, 80, 90] → 중앙값 = 80 |
| **표준편차** | 데이터가 평균에서 얼마나 퍼졌는지 | 작을수록 데이터가 밀집 |
| **분산** | 표준편차의 제곱 | 표준편차 = 10 → 분산 = 100 |

### 🧪 가설검정

#### T-test (두 그룹 비교)
```
질문: "남학생과 여학생의 평균 성적이 다른가?"
결과: p-value = 0.03 < 0.05
해석: 통계적으로 유의한 차이가 있다!
```

#### ANOVA (3개 이상 그룹 비교)
```
질문: "A반, B반, C반의 평균 성적이 다른가?"
결과: p-value = 0.001 < 0.05
해석: 적어도 한 반은 다른 반과 유의하게 다르다
→ 사후검정(Tukey HSD)으로 어느 반이 다른지 확인
```

#### P-value 해석 가이드
- **p < 0.001**: 매우 강한 증거 (***로 표시)
- **p < 0.01**: 강한 증거 (**)
- **p < 0.05**: 유의미한 증거 (*)
- **p ≥ 0.05**: 증거 부족 (n.s. - not significant)

### 📈 회귀분석

| 지표 | 의미 | 좋은 값 |
|------|------|---------|
| **R-squared** | 모델의 설명력 (0~1) | 0.7 이상이면 우수 |
| **회귀식** | Y = aX + b | a = 기울기, b = 절편 |
| **잔차** | 실제값 - 예측값 | 0 주변에 랜덤하게 분포해야 함 |

---

## 🆘 문제 해결 (Troubleshooting)

### ❓ 자주 묻는 질문

#### Q1. "API 할당량 초과" 오류가 나요
```
원인: Google 무료 API는 하루 20회 제한

해결:
1. 사이드바에서 모델을 'gemini-2.0-flash'로 변경
2. 5분 정도 기다린 후 재시도
3. 또는 새 API 키 발급
```

#### Q2. 그래프가 리포트에 안 나타나요
```
원인: Quarto 렌더링 설정 문제

해결:
1. Quarto CLI가 설치되었는지 확인: quarto --version
2. Python 가상환경이 활성화되었는지 확인
3. 에러 메시지에서 "jupyter" 언급 시:
   pip install jupyter ipykernel
```

#### Q3. 한글이 깨져서 나와요
```
원인: 한글 폰트 미설치

해결:
- Windows: 맑은 고딕 (기본 설치됨)
- Mac:
  brew install font-nanum
- Linux:
  sudo apt-get install fonts-nanum
```

#### Q4. CSV 업로드가 안 돼요
```
해결:
1. 파일이 .csv 확장자인지 확인
2. Excel에서 "다른 이름으로 저장" → "CSV UTF-8"로 저장
3. 파일 크기가 200MB 이하인지 확인
```

#### Q5. 어떤 분석부터 시작하면 좋을까요?
```
추천 순서:
1. 기술통계 (평균, 표준편차, 히스토그램)
2. 시각화 (박스플롯, scatter plot)
3. 그룹 비교 (T-test, ANOVA)
4. 상관분석 (히트맵)
5. 회귀분석 (예측 모델)
```

### 🐛 에러 메시지별 해결법

| 에러 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError: No module named 'plotly'` | Plotly 미설치 | `pip install plotly` |
| `Quarto not found` | Quarto CLI 미설치 | [quarto.org](https://quarto.org) 설치 |
| `GOOGLE_API_KEY not found` | .env 파일 없음 | `.env` 파일 생성 후 API 키 입력 |
| `UnicodeDecodeError` | 인코딩 문제 | CSV를 UTF-8로 다시 저장 |

---

## 📚 학습 리소스

### 통계 기초 학습
- [Khan Academy 통계학](https://ko.khanacademy.org/math/statistics-probability)
- [생활코딩 통계](https://opentutorials.org/course/3635)

### Python 기초
- [점프 투 파이썬](https://wikidocs.net/book/1)
- [왕초보를 위한 Python](https://wikidocs.net/book/2)

### 데이터 시각화
- [Plotly 공식 문서](https://plotly.com/python/)
- [Seaborn 튜토리얼](https://seaborn.pydata.org/tutorial.html)

### Quarto 보고서 작성
- [Quarto 공식 가이드](https://quarto.org/docs/guide/)

---

## 🎨 커스터마이징

### 테마 변경
사이드바에서 다양한 테마 선택 가능:
- **cosmo**: 깔끔하고 모던한 디자인 (기본)
- **flatly**: 플랫 디자인
- **darkly**: 다크 모드
- **journal**: 논문 스타일
- **sketchy**: 손글씨 느낌

### 리포트 언어 설정
현재 한글 기본 지원. `utils/quarto_renderer.py`에서 변경 가능.

---

## 🔒 데이터 보안 및 개인정보

### 데이터는 어디로 가나요?
- **로컬 저장**: 업로드한 CSV는 컴퓨터의 임시 폴더에만 저장
- **API 전송**: 데이터 요약 정보만 Google Gemini API로 전송
- **삭제**: 앱 종료 시 임시 파일 자동 삭제

### 민감 데이터 주의
- 개인정보(주민번호, 이름 등)는 제거 후 사용
- 연구 윤리 위원회(IRB) 승인 필요 시 사전 확인

---

## 🤝 기여 및 피드백

### 버그 리포트
GitHub Issues에 다음 정보와 함께 제보해주세요:
- 운영체제 (Windows/Mac/Linux)
- Python 버전
- 에러 메시지 전문
- 재현 방법

### 기능 제안
"이런 기능이 있으면 좋겠어요!" 언제든지 환영합니다.

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## ❤️ 만든 사람들

**DataViz Campus Team**
- 대학생 데이터 분석 교육을 위해 만들었습니다
- Powered by Google Gemini 2.5 Flash

---

## 🚀 다음 단계

1. **예제로 연습**: '예제 & 템플릿' 탭에서 3가지 데이터셋 다운로드
2. **간단한 분석부터**: 기술통계 → 시각화 → 가설검정 순서로
3. **프롬프트 개선**: 구체적으로 요청할수록 좋은 결과
4. **리포트 제출**: HTML/PDF로 바로 과제 제출 가능

**Happy Data Analysis!** 📊✨
