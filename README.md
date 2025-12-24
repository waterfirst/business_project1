# 🧬 Bio-Log

<div align="center">

![Bio-Log Logo](https://img.shields.io/badge/Bio--Log-v2.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-Gemini-red?style=for-the-badge&logo=google-cloud)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Google Gemini 기반 바이오 실험 데이터 자동 분석 및 리포팅 플랫폼**

[📖 문서](./docs) | [🐛 이슈 제보](https://github.com/waterfirst/business_project1/issues)

</div>

---

## 📌 프로젝트 개요

Bio-Log는 생명과학 연구자들이 실험 데이터를 **자연어로 분석 요청**하면, AI가 자동으로 **R/Python 코드를 생성**하고, **Quarto 엔진**으로 출판 수준의 리포트를 만들어주는 SaaS 플랫폼입니다.

### 🎯 핵심 가치 제안

| 문제 | 기존 방식 | Bio-Log 솔루션 |
|------|----------|---------------|
| 리포트 작성 시간 | 실험 1시간 + 리포트 3시간 | 실험 1시간 + AI 자동화 10분 |
| 재현성 부족 | Excel/Word 분리 관리 | 코드+데이터+결과 통합 문서 |
| 코딩 진입장벽 | Python/R 학습 필수 | 자연어로 분석 요청 |
| 데이터 검증 | 수동 확인 | AI 자동 이상치 탐지 |

---

## ✨ 주요 기능

### 1. 🤖 AI 코드 생성 (Gemini 1.5 Flash/Pro)
```
입력: "3개 그룹의 세포 생존율을 ANOVA로 비교하고, Tukey HSD로 사후검정하세요"

출력:
✅ Python/R 실행 가능 코드
✅ 통계적 가정 검증 포함
✅ Publication-quality 그래프
✅ 결과 해석 텍스트
```

### 2. 📊 자동 데이터 검증
- **Standard Curve 검증**: R² < 0.95 시 경고
- **Outlier 탐지**: Isolation Forest 알고리즘
- **반복 측정 일관성**: CV(변동계수) 자동 계산

### 3. 📄 Quarto 원클릭 리포팅
- **HTML**: 인터랙티브 그래프 (Plotly)
- **PDF**: 논문 제출용 포맷 (LaTeX)
- **재현성 보장**: 코드+데이터+결과 통합

### 4. 🖼️ Gemini Vision 이미지 분석 (실험적)
- 젤 전기영동 밴드 자동 카운팅
- 세포 배양 플레이트 confluency 평가

---

## 🚀 빠른 시작

### 사전 요구사항
- Python 3.10 이상
- [Quarto](https://quarto.org/docs/get-started/) 설치
- Google AI API 키 ([발급 방법](https://makersuite.google.com/app/apikey))

### 설치 및 실행

```bash
# 1. 레포지토리 클론
git clone https://github.com/waterfirst/business_project1.git
cd business_project1

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 GOOGLE_API_KEY 입력

# 5. 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속!

---

## 📖 사용 방법

### 1단계: 데이터 업로드
```csv
group,viability
Control,95.2
Treatment A,78.5
Treatment B,65.3
```

### 2단계: AI 분석 요청
```
"그룹 간 생존율 차이를 ANOVA로 검정하고, 결과를 box plot으로 시각화하세요"
```

### 3단계: 리포트 다운로드
- HTML 또는 PDF 선택
- 원클릭 다운로드 → 바로 제출/공유 가능!

---

## 🏗️ 기술 스택

### Backend
- **AI Engine**: Google Gemini 1.5 Flash/Pro
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Statistical Analysis**: SciPy, Statsmodels
- **Document Engine**: Quarto

### Frontend
- **UI Framework**: Streamlit
- **Visualization**: Plotly, Seaborn

### Infrastructure
- **Deployment**: Streamlit Cloud / Google Cloud Run
- **Database**: Firebase Firestore (계획 중)
- **Storage**: Google Cloud Storage

---

## 📂 프로젝트 구조

```
business_project1/
├── app.py                    # Streamlit 메인 앱
├── agents/
│   ├── code_generator.py     # Gemini AI 코드 생성
│   ├── validator.py          # 데이터 품질 검증
│   └── vision_analyzer.py    # 이미지 분석
├── utils/
│   └── quarto_renderer.py    # Quarto 문서 렌더링
├── templates/
│   └── experiment_template.qmd
└── docs/
    ├── business_plan.md      # 사업계획서
    └── architecture.md       # 시스템 아키텍처
```

---

## 🎓 사용 사례

### Case 1: 학부생 실험 리포트
- **Before**: 실험 2시간 + Word 작성 4시간 = 총 6시간
- **After**: 실험 2시간 + Bio-Log 10분 = 총 2.2시간
- **절감**: 64% 시간 단축

### Case 2: 대학원 연구 노트
- **문제**: 6개월 전 실험을 재현하려는데 파일 찾기 불가
- **해결**: Quarto 문서에 모든 코드+데이터 포함 → 원클릭 재실행

---

## 🛣️ 로드맵

### v2.0 (현재) ✅
- [x] Gemini 1.5 통합
- [x] Quarto HTML/PDF 출력
- [x] 데이터 검증 엔진
- [x] Streamlit Cloud 배포

### v2.1 (2026 Q1) 🔄
- [ ] 사용자 인증 (Firebase Auth)
- [ ] 클라우드 저장소 (팀 협업)
- [ ] 실험 템플릿 라이브러리

### v3.0 (2026 Q2) 🎯
- [ ] Gemini 2.0 Flash Thinking 모드
- [ ] 대학 B2B 라이선스 판매
- [ ] API 제공 (LIMS 연동)

---

## 🤝 기여 방법

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### 기여 가이드라인
- 코드는 Black 포맷터 사용
- Docstring은 Google Style
- 커밋 메시지는 Conventional Commits 준수

---

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](./LICENSE) 참조

---

## 👥 팀

**Team Anti-Gravity**
- 대표: OOO (Ghent University) - Tech Lead
- 공동창업자: OOO (Ghent University) - Domain Expert
- 공동창업자: OOO (University of Utah) - Product Manager

---

## 📞 연락처

- **GitHub Issues**: [이슈 제보](https://github.com/waterfirst/business_project1/issues)
- **Email**: team@bio-log.com

---

## 🙏 감사의 글

- [Google AI Studio](https://ai.google.dev/) - Gemini API 제공
- [Quarto](https://quarto.org/) - 훌륭한 문서 엔진
- [Streamlit](https://streamlit.io/) - 빠른 프로토타이핑
- IGC (Incheon Global Campus) - 초기 베타 테스터

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ by Team Anti-Gravity

</div>
