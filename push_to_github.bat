@echo off
echo ========================================
echo Bio-Log GitHub Push Script
echo ========================================
echo.

cd /d %~dp0

echo [1/6] Git 초기화...
git init
if errorlevel 1 (
    echo Git이 설치되어 있지 않습니다!
    echo https://git-scm.com/ 에서 설치하세요
    pause
    exit /b 1
)

echo.
echo [2/6] 원격 저장소 연결...
git remote remove origin 2>nul
git remote add origin https://github.com/waterfirst/business_project1.git

echo.
echo [3/6] 모든 파일 스테이징...
git add .

echo.
echo [4/6] 커밋 생성...
git commit -m "feat: Initial commit - Bio-Log v2.0 (Google Cloud Edition)

- Gemini 1.5 Flash/Pro 통합 완료
- Streamlit UI 구현
- Quarto 렌더링 엔진 완성
- 데이터 검증 모듈 추가
- Vision 이미지 분석 기능 (실험적)
- 완전한 문서화 (README, 사업계획서)"

echo.
echo [5/6] 메인 브랜치로 변경...
git branch -M main

echo.
echo [6/6] GitHub에 푸시...
git push -u origin main --force

echo.
echo ========================================
echo 푸시 완료!
echo GitHub: https://github.com/waterfirst/business_project1
echo ========================================
pause
