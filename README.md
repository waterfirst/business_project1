# Quarto R & Python Integration Project

이 저장소는 Quarto를 사용하여 R과 Python을 하나의 문서에서 활용하는 데이터 분석 예제를 담고 있습니다. 인공지능 코딩 어시스턴트 Antigravity를 통해 생성 및 구성되었습니다.

## 주요 기능 (Features)
- **다중 언어 통합**: R(ggplot2)과 Python(Seaborn)의 시각화 도구를 하나의 HTML 리포트에서 구현.
- **데이터 상호운용성 (Interoperability)**:
  - R에서 가공한 데이터를 Python에서 사용 (`r.object`)
  - Python 결과값을 R에서 활용 (`py$object`)
- **자동화된 환경 설정**: `reticulate` 패키지를 통한 Python 경로 명시적 지정 예제 포함.

## 파일 구성 (Project Structure)
- `analysis_example.qmd`: 메인 Quarto 소스 파일.
- `analysis_example.html`: 렌더링된 최종 리포트 파일.
- `test.r` / `test.qmd`: 기초 테스트용 스크립트.

## 사전 준비 (Prerequisites)
이 문서를 렌더링하거나 수정하려면 다음 환경이 필요합니다.

### 1. Quarto 설치
[quarto.org](https://quarto.org)에서 운영체제에 맞는 버전을 설치합니다.

### 2. R 및 관련 패키지
R 콘솔에서 다음 명령어를 실행하여 필요한 패키지를 설치합니다.
```r
install.packages(c("ggplot2", "dplyr", "reticulate"))
```

### 3. Python 및 관련 패키지
터미널에서 데이터 분석 패키지를 설치합니다.
```bash
pip install pandas seaborn matplotlib
```

### 4. LaTeX (수식 및 PDF 출력을 위함)
Quarto는 가벼운 LaTeX 배포판인 TinyTeX을 권장합니다. 터미널에서 다음 명령어를 실행하여 설치할 수 있습니다:
```bash
quarto install tinytex
```
이미 설치되어 있다면 이 단계는 건너뛰어도 좋습니다.

## 사용 방법 (Usage)
터미널에서 다음 명령어를 입력하면 HTML 문서가 생성됩니다.
```bash
quarto render analysis_example.qmd --to html
```

---
*Generated and managed by Antigravity*
