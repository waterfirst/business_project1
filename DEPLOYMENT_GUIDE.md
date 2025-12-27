# 🚀 Streamlit Community Cloud 배포 가이드

DataViz Campus를 무료로 온라인에 배포하는 완벽 가이드입니다.

---

## 📋 배포 전 체크리스트

### ✅ 필수 파일 확인
- [x] `app.py` - 메인 애플리케이션
- [x] `requirements.txt` - 의존성 패키지
- [x] `.gitignore` - secrets.toml 제외 설정
- [x] `.streamlit/secrets.toml.example` - 시크릿 템플릿

---

## 1️⃣ GitHub 저장소 준비

### 사용할 GitHub 주소:
```
https://github.com/waterfirst/business_project1
```

### 배포할 브랜치:
```
upbeat-kirch
```

### 파일 확인:
```bash
git status
git log --oneline -5
```

---

## 2️⃣ Streamlit Community Cloud 계정 생성

### 1. Streamlit Cloud 접속
👉 https://share.streamlit.io/

### 2. GitHub 계정으로 로그인
- "Sign up" 또는 "Continue with GitHub" 클릭
- GitHub 권한 승인

### 3. 저장소 접근 권한 부여
- Streamlit이 GitHub 저장소에 접근할 수 있도록 허용

---

## 3️⃣ 앱 배포하기

### Step 1: New app 생성
1. 대시보드에서 **"New app"** 버튼 클릭

### Step 2: 저장소 선택
```
Repository: waterfirst/business_project1
Branch: upbeat-kirch
Main file path: app.py
```

### Step 3: 앱 URL 설정 (선택사항)
```
App URL: dataviz-campus (또는 원하는 이름)
최종 URL: https://dataviz-campus.streamlit.app
```

### Step 4: Advanced settings

**Python version**: `3.11` (권장)

**Secrets**: 여기에 API 키 입력!
```toml
GOOGLE_API_KEY = "여기에_발급받은_API_키_입력"
```

⚠️ **중요**: `.env` 파일의 API 키를 그대로 복사하세요!

---

## 4️⃣ API 키 설정 (필수!)

### Google Gemini API 키 발급

1. **Google AI Studio 접속**
   👉 https://ai.google.dev/

2. **API 키 생성**
   - "Get API Key" 클릭
   - 새 프로젝트 생성 또는 기존 프로젝트 선택
   - API 키 복사

3. **Streamlit Secrets에 추가**
   - Streamlit Cloud 대시보드에서 앱 선택
   - ⚙️ Settings → Secrets
   - 다음 형식으로 입력:
   ```toml
   GOOGLE_API_KEY = "AIzaSy..."
   ```

---

## 5️⃣ 배포 완료!

### 자동 배포 프로세스
```
1. Requirements 설치 중... ⏳
2. 앱 실행 중... ⏳
3. 배포 완료! ✅
```

### 앱 접속
배포가 완료되면 다음 URL로 접속 가능합니다:
```
https://[your-app-name].streamlit.app
```

---

## 6️⃣ 배포 후 관리

### 🔄 자동 재배포
- `upbeat-kirch` 브랜치에 push하면 **자동으로 재배포**됩니다
- 수정 사항이 즉시 반영됩니다

### 📊 리소스 모니터링
- Streamlit Cloud 대시보드에서 확인:
  - CPU 사용량
  - 메모리 사용량
  - 활성 사용자 수

### 🔐 Secrets 업데이트
1. Settings → Secrets
2. 기존 내용 수정
3. Save 클릭
4. 앱 자동 재시작

---

## 7️⃣ 문제 해결 (Troubleshooting)

### ❌ "ModuleNotFoundError" 에러
**원인**: `requirements.txt`에 패키지 누락

**해결**:
```bash
# requirements.txt에 추가
pip freeze | grep [패키지명] >> requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push origin upbeat-kirch
```

### ❌ "API 키 없음" 에러
**원인**: Secrets 설정 안 됨

**해결**:
1. Settings → Secrets
2. `GOOGLE_API_KEY` 추가
3. Reboot app

### ❌ Quarto 렌더링 실패
**원인**: Streamlit Cloud에 Quarto CLI 미설치

**해결방법 1**: `packages.txt` 파일 생성
```bash
echo "quarto" > packages.txt
git add packages.txt
git commit -m "Add Quarto CLI"
git push origin upbeat-kirch
```

**해결방법 2**: 시스템 패키지 설치
`.streamlit/packages.txt` 생성:
```
wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.4.550/quarto-1.4.550-linux-amd64.deb
```

⚠️ **주의**: Streamlit Cloud의 제약으로 Quarto 설치가 어려울 수 있습니다.
→ **대안**: QMD 파일만 다운로드하도록 안내

### ❌ 메모리 초과 에러
**원인**: 무료 플랜 리소스 제한 (1GB RAM)

**해결**:
- 대용량 데이터 처리 시 샘플링
- 캐싱 활용 (`@st.cache_data`)
- 불필요한 라이브러리 제거

---

## 8️⃣ 무료 플랜 제약사항

### Streamlit Community Cloud 무료 플랜
| 항목 | 제한 |
|------|------|
| **앱 개수** | 무제한 (public) |
| **RAM** | 1GB |
| **CPU** | 공유 |
| **저장공간** | 1GB |
| **동시 사용자** | 무제한 |
| **가동시간** | 수동 슬립 (7일 미사용 시) |

### 💡 Tip
- 앱이 7일간 사용되지 않으면 슬립 모드 진입
- 첫 방문 시 웨이크업에 1-2분 소요
- 주기적으로 접속하여 활성 상태 유지

---

## 9️⃣ 배포 URL 공유

### 공식 URL 형식
```
https://[app-name]-[username].streamlit.app
```

### 예시
```
https://dataviz-campus-waterfirst.streamlit.app
```

### 커스텀 도메인 (유료 플랜)
Streamlit Teams 플랜에서 가능

---

## 🔟 대안: Quarto 제한 대응

### 문제
Streamlit Cloud에서 Quarto CLI 설치 어려움

### 해결책 1: 로컬 전용 기능으로 안내
```python
# app.py에 추가
if st.session_state.get('cloud_mode', False):
    st.warning("☁️ 클라우드 버전에서는 QMD 파일 다운로드만 가능합니다. "
               "로컬 환경에서 'quarto render'로 변환하세요.")
```

### 해결책 2: Docker 이미지 사용
`Dockerfile` 생성 후 Render.com 또는 Railway.app 사용

---

## 📚 추가 리소스

### 공식 문서
- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [배포 가이드](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

### 도움말
- [커뮤니티 포럼](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)

---

## ✅ 배포 체크리스트

### 배포 전
- [ ] GitHub 저장소 public 설정
- [ ] `requirements.txt` 최신 상태 확인
- [ ] `.gitignore`에 `secrets.toml` 포함 확인
- [ ] 로컬에서 앱 정상 작동 테스트
- [ ] Google API 키 발급 완료

### 배포 중
- [ ] Streamlit Cloud 계정 생성
- [ ] 저장소 연결
- [ ] Secrets에 API 키 입력
- [ ] Python 버전 설정 (3.11)
- [ ] Deploy 클릭

### 배포 후
- [ ] 앱 URL 접속 확인
- [ ] 예제 데이터로 테스트
- [ ] AI 코드 생성 테스트
- [ ] 에러 로그 확인
- [ ] 사용자 피드백 수집

---

## 🎉 축하합니다!

DataViz Campus가 전 세계 누구나 사용할 수 있는 웹 앱이 되었습니다!

**공유하기**:
```
📊 DataViz Campus - 대학생을 위한 AI 데이터 분석 플랫폼
👉 https://[your-app-url].streamlit.app

무료로 사용해보세요! 🎓✨
```

---

## 📞 문의

배포 관련 질문이나 이슈는 GitHub Issues로 남겨주세요:
https://github.com/waterfirst/business_project1/issues
