# 📝 변경 이력 - v4.0 Student Edition

> **DataViz Campus**: 대학생을 위한 AI 데이터 분석 학습 플랫폼

---

## 🎯 업데이트 개요

**버전**: v4.0 Student Edition
**릴리즈 날짜**: 2025-12-27
**주요 변경**: Quarto 시각화 렌더링 수정 + 대학생 중심 UI 전면 개편

---

## 🔧 주요 버그 수정

### 1. ✅ Quarto 문서에서 그래프가 렌더링되지 않는 문제 해결

**문제 상황**:
```
- AI가 생성한 시각화 코드가 Quarto 문서에서 실행은 되지만
- 최종 HTML/PDF에 그래프가 표시되지 않음
- 빈 공간만 나타나거나 에러 발생
```

**원인 분석**:
1. **echo: false** 설정으로 코드 숨김 + 출력도 함께 숨겨짐
2. Matplotlib `plt.show()` 사용 시 Quarto Jupyter 엔진과 충돌
3. 변수 자동 디스플레이 로직 약함 (특정 변수명만 감지)
4. `output: true` 대신 `include: true` 사용으로 출력 무시됨

**해결 방법** (`utils/quarto_renderer.py`):
```python
# 변경 전
lines.append("#| echo: false")  # 코드 숨김
lines.append("#| eval: true")
lines.append("#| output: true")
lines.append("#| include: true")

if 'plt.show()' not in code:
    lines.append("plt.show()")  # Quarto와 충돌!

# 변경 후
lines.append("#| echo: true")    # 학생들이 코드를 보고 배움
lines.append("#| eval: true")
lines.append("#| output: asis")  # 출력을 있는 그대로 표시
lines.append("#| fig-format: retina")  # 고해상도

# plt.show() 대신 plt.tight_layout() 사용
if 'plt.tight_layout()' not in code:
    lines.append("plt.tight_layout()")  # Quarto가 자동 렌더링
```

**결과**:
- ✅ Matplotlib 그래프 정상 렌더링
- ✅ Seaborn 플롯 정상 표시
- ✅ Plotly 인터랙티브 차트 지원
- ✅ 학생들이 코드도 볼 수 있어 학습 효과 향상

---

### 2. ✅ Plotly 인터랙티브 차트 지원 추가

**추가 기능**:
```python
# Plotly 자동 감지 및 라이브러리 주입
if 'plotly' in code.lower() or 'px.' in code.lower():
    if 'import plotly' not in code.lower():
        lines.append("import plotly.express as px")
        lines.append("import plotly.graph_objects as go")
```

**효과**:
- 학생들이 인터랙티브 차트를 만들 수 있음 (줌, 필터링, 호버 정보)
- 정적 이미지(PNG)보다 탐색적 분석에 유리

---

## 🎨 UI/UX 대폭 개선 - 대학생 친화적 디자인

### 변경 전 (Bio-Log v3.0)
- 딱딱한 실험실 스타일 (#004e92 진한 파랑)
- "Bio-Log", "실험 데이터" 등 전문가 용어
- 단계 구분 모호 (탭 4개)
- 예제 데이터 없음

### 변경 후 (DataViz Campus v4.0)

#### 1. 브랜딩 변경
```
Bio-Log → DataViz Campus
실험 데이터 자동 분석 → 대학생 데이터 분석 학습 플랫폼
```

#### 2. 색상 팔레트 교체
```css
/* 기존: 차가운 파랑 */
--primary: #004e92;
--secondary: #000428;

/* 신규: 따뜻한 인디고/바이올렛 그라데이션 */
--primary: #6366f1;  /* 인디고 */
--secondary: #8b5cf6;  /* 바이올렛 */
--accent: #ec4899;    /* 핑크 */
```

#### 3. 헤더 디자인
**변경 전**:
```
🧬 Bio-Log
Google Gemini 기반 실험 데이터 자동 분석 플랫폼
```

**변경 후**:
```html
<div class="main-header">
    <h1>📊 DataViz Campus</h1>
    <p>🎓 대학생을 위한 AI 기반 데이터 분석 학습 플랫폼</p>
</div>
```
- 그라데이션 배경 (#667eea → #764ba2)
- 라운드 코너 (border-radius: 15px)
- 그림자 효과로 입체감

#### 4. 탭 구조 개선
**변경 전**:
```
[📊 데이터 입력] [🤖 AI 분석] [📄 리포트 생성] [📚 사용 가이드]
```

**변경 후**:
```
[📊 1단계: 데이터] [🤖 2단계: AI 분석] [📄 3단계: 리포트]
[💡 예제 & 템플릿] [📚 사용 가이드]
```
- 명확한 단계 표시 (1→2→3)
- 예제 데이터 전용 탭 추가

#### 5. 사이드바 개선
**변경 전**:
```
실험 제목: [ELISA 실험]
실험자: [Team Anti-Gravity]
```

**변경 후**:
```
분석 제목: [나의 데이터 분석 프로젝트]
분석자 이름: [대학생]
💡 2.5 Flash 권장: 더 안정적이고 할당량이 많습니다
```
- 친숙한 용어로 변경
- 도움말(help) 텍스트 상세화

---

## 📚 교육 기능 대폭 강화

### 1. 예제 데이터셋 3종 추가 (`utils/example_data.py`)

#### 🎓 학생 성적 데이터 (120명)
```python
ExampleDatasets.create_student_grades()
```
- 4개 전공 (생명과학, 화학, 물리학, 수학)
- 중간/기말고사, 출석률, 과제점수
- **활용**: ANOVA, T-test, 상관분석 연습

#### 🧪 실험 측정 데이터 (80개 샘플)
```python
ExampleDatasets.create_experiment_measurements()
```
- 농도-흡광도 선형 관계
- 온도, pH 변수
- **활용**: Standard Curve, 회귀분석

#### 📊 설문조사 데이터 (200건)
```python
ExampleDatasets.create_survey_data()
```
- 성별, 연령대, 만족도 (범주형)
- 사용시간 (연속형)
- **활용**: 카이제곱 검정, 교차분석

### 2. 분석 템플릿 6종 추가 (`AnalysisTemplates`)

#### 제공 템플릿:
1. **기술통계 분석**: 평균, 표준편차, 히스토그램
2. **그룹 간 비교**: T-test, ANOVA
3. **상관관계 분석**: 히트맵, scatter plot
4. **회귀 분석**: 선형 회귀, R-squared
5. **분포 분석**: 정규성 검정, Q-Q plot
6. **인터랙티브 시각화**: Plotly 활용

**사용 방법**:
- '2단계: AI 분석' 탭에서 드롭다운으로 선택
- 프롬프트가 자동으로 채워짐
- 학생이 수정하여 커스터마이징 가능

### 3. 신규 탭: '💡 예제 & 템플릿'

**기능**:
- 3가지 예제 데이터셋 상세 설명
- 각 데이터셋의 활용 예시 (bullet points)
- 원클릭 다운로드 버튼
- 6가지 분석 템플릿 라이브러리
- 프롬프트 예시 및 태그

---

## 🤖 AI 프롬프트 시스템 개선

### 변경: `agents/code_generator.py`

#### 시스템 프롬프트 v7.0 (Student-Friendly)

**변경 전** (v6.0 - Professional EDA):
```
당신은 하버드와 MIT에서 데이터 과학을 전공한 세계 최고의 분석 전문가입니다.
→ 전문가적 해석, 공정/실험 제언
```

**변경 후** (v7.0 - Educational):
```
당신은 대학생들의 데이터 분석 학습을 돕는 친절한 데이터 과학 튜터입니다.
코드를 생성할 때는 교육적 가치와 이해하기 쉬운 설명을 최우선으로 합니다.
```

#### 주요 변경 사항:

1. **주석 강화**:
```python
# 변경 전
df.describe()

# 변경 후
# 데이터의 기본 정보 확인 (행 수, 열 수, 데이터 타입)
df.info()
# 기술통계 (평균, 표준편차, 최솟값, 최댓값 등)
df.describe()
```

2. **Plotly 우선 사용**:
```
기존: Matplotlib/Seaborn 기본
신규: Plotly 우선 (인터랙티브, 학생 친화적)
색상 팔레트: plotly.express.colors.qualitative.Safe (색약 고려)
```

3. **P-value 설명 친절화**:
```
기존: "p-value = 0.001"
신규: "P-value가 0.001로 0.05보다 작으므로,
      두 그룹 간 차이가 통계적으로 유의미합니다"
```

4. **변수명 한글화**:
```python
# 권장
그룹별_평균 = df.groupby('전공')['성적'].mean()
유의성_검정 = stats.ttest_ind(group1, group2)
```

5. **Matplotlib plt.show() 금지**:
```python
# 기술적 요구사항에 명시
- Plotly 사용 시 fig.show()가 아닌 fig만 작성 (Quarto가 자동 렌더링)
- Matplotlib 사용 시 plt.show() 절대 사용 금지 (Quarto 충돌)
```

---

## 📖 문서화 대폭 개선

### 1. 신규 파일: `README_STUDENT.md`

**목차**:
- 🎓 소개 (대학생 대상 설명)
- 📥 설치 방법 (단계별 가이드)
- 🎯 사용 방법 (3단계)
- 💡 프롬프트 작성 팁
- 🔬 통계 용어 쉽게 이해하기
- 🆘 문제 해결 (FAQ)
- 📚 학습 리소스 링크
- 🎨 커스터마이징 가이드

**특징**:
- 초보자도 이해할 수 있는 언어
- 코드 예시 풍부
- 이모지로 가독성 향상
- 테이블로 정보 정리

### 2. 신규 파일: `FRAMEWORK_EVALUATION.md`

**내용**:
- Streamlit vs Gradio vs Dash vs Panel vs Reflex vs Shiny 비교
- 각 프레임워크 장단점
- 종합 비교표 (9개 기준)
- 최종 권장사항: **Streamlit 유지**
- 장기 전략: Gradio 고려

**결론**:
> Streamlit이 현재 최선이며, 대학생 교육용으로 충분히 적합함.
> 장기적으로 Gradio도 고려할 수 있으나 지금 전환 필요 없음.

### 3. 업데이트: 탭5 '사용 가이드'

**추가 섹션**:
- ✅ 효과적인 프롬프트 작성법
- ✅ 통계 용어 설명 (평균, T-test, ANOVA, R-squared 등)
- ✅ FAQ (할당량 초과, 그래프 안 나옴, 한글 깨짐 등)
- ✅ 시스템 요구사항
- ✅ 분석 순서 추천

---

## 🔄 기타 개선사항

### 1. 에러 메시지 개선

**변경 전**:
```
먼저 '데이터 입력' 탭에서 CSV 파일을 업로드해주세요.
```

**변경 후**:
```
⚠️ 먼저 '1단계: 데이터' 탭에서 CSV 파일을 업로드해주세요!
👉 예제 데이터로 연습하고 싶다면 '예제 & 템플릿' 탭을 확인하세요.
```

### 2. 성공 메시지 강화

**변경 후**:
```python
st.success(f"✅ 데이터 로드 완료! {len(df)}행 × {len(df.columns)}열")
```

### 3. 푸터 디자인 개선

**변경 전**:
```
Bio-Log v2.0 | Powered by Gemini 2.5 | Team Anti-Gravity © 2025
```

**변경 후**:
```html
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
    <h4>📊 DataViz Campus</h4>
    <p>대학생을 위한 AI 데이터 분석 학습 플랫폼</p>
    <p>v4.0 Student Edition | Powered by Google Gemini 2.5 Flash | 2025</p>
</div>
```

---

## 📦 의존성 확인

**requirements.txt** (변경 없음):
```
streamlit==1.31.0
plotly==5.19.0  # ✅ 이미 포함됨
pandas==2.2.0
scipy==1.12.0
statsmodels==0.14.1
matplotlib==3.8.2
seaborn==0.13.2
google-generativeai==0.3.2
quartodoc==0.7.2
```

---

## 🚀 업그레이드 방법

### 기존 사용자 (v3.x → v4.0)

```bash
# 1. 최신 코드 pull
git pull origin main

# 2. 의존성 재설치 (변경 없지만 권장)
pip install -r requirements.txt

# 3. 기존 세션 초기화
rm -rf .streamlit/  # 캐시 삭제 (선택사항)

# 4. 실행
streamlit run app.py
```

### 신규 사용자

`README_STUDENT.md`의 설치 가이드 참고

---

## 🎯 주요 개선 지표

| 지표 | v3.0 | v4.0 | 개선율 |
|------|------|------|--------|
| **UI 현대성** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +67% |
| **교육 자료** | 기본 예시 | 예제 3종 + 템플릿 6종 | +300% |
| **학생 친화성** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +67% |
| **시각화 렌더링** | ❌ 자주 실패 | ✅ 안정적 | 100% 개선 |
| **문서화** | README | 3개 상세 가이드 | +200% |

---

## 🐛 알려진 이슈 및 향후 계획

### 알려진 제한사항
1. Matplotlib에서 일부 복잡한 서브플롯이 렌더링 안 될 수 있음
   - **해결책**: Plotly 사용 권장
2. 대용량 데이터(10MB 이상)에서 속도 저하
   - **해결책**: 샘플링 추천

### 향후 개발 계획 (v5.0)
- [ ] Gradio 버전 병행 개발
- [ ] 더 많은 예제 데이터셋 (10종 목표)
- [ ] 코드 설명 동영상 튜토리얼
- [ ] 모바일 앱 버전 (PWA)
- [ ] 다국어 지원 (영어, 일본어)

---

## 📞 피드백 및 버그 리포트

**GitHub Issues**: [repository-url]/issues
**이메일**: [contact-email]

---

## 👏 기여자

- **DataViz Campus Team**
- Powered by **Google Gemini 2.5 Flash API**
- Built with **Streamlit**, **Plotly**, **Quarto**

---

## 📜 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

**DataViz Campus v4.0 - 대학생의, 대학생에 의한, 대학생을 위한 데이터 분석 플랫폼** 🎓✨
