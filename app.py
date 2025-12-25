# app.py
import streamlit as st
import pandas as pd
from agents.code_generator import BioCodeGenerator
from agents.validator import ExperimentValidator
from utils.quarto_renderer import QuartoRenderer
import tempfile
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Bio-Log - Google Cloud Edition",
    page_icon="🧬",
    layout="wide"
)

# 세션 상태 초기화
if 'generator' not in st.session_state:
    try:
        st.session_state.generator = BioCodeGenerator(model_name="gemini-2.5-flash")
        st.session_state.model_loaded = True
    except Exception as e:
        st.session_state.model_loaded = False
        st.session_state.error_msg = str(e)

if 'validator' not in st.session_state:
    st.session_state.validator = ExperimentValidator()
    
if 'renderer' not in st.session_state:
    st.session_state.renderer = QuartoRenderer()

if 'code_history' not in st.session_state:
    st.session_state.code_history = []

if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

# 헤더
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🧬 Bio-Log")
    st.subheader("Google Gemini 기반 실험 데이터 자동 분석 플랫폼")
with col2:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg", width=100)

# API 키 체크
if not st.session_state.model_loaded:
    st.error(f"⚠️ Google API 키 설정이 필요합니다: {st.session_state.error_msg}")
    st.info("""
    **설정 방법:**
    1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키 발급
    2. `.env` 파일에 `GOOGLE_API_KEY=your_key` 추가
    3. 앱 재시작
    """)
    st.stop()

# 사이드바
with st.sidebar:
    st.header("📋 실험 정보")
    exp_title = st.text_input("실험 제목", "ELISA 실험")
    exp_author = st.text_input("실험자", "Team Anti-Gravity")
    exp_date = st.date_input("실험 날짜", datetime.now())
    
    st.divider()
    
    model_choice = st.selectbox(
        "Gemini 모델",
        ["gemini-2.5-flash (추천)", "gemini-2.0-flash"],
        help="2.5 Flash: 비전 및 일반 작업 최적화 / 2.0 Flash: 최신 모델 (할당량 주의)"
    )
    
    language = st.selectbox("분석 언어", ["Python", "R"])
    
    st.divider()
    st.metric("생성된 분석 수", len(st.session_state.code_history))
    
    if st.button("🗑️ 전체 초기화"):
        st.session_state.code_history = []
        st.session_state.uploaded_data = None
        st.rerun()

# 메인 영역
tab1, tab2, tab3, tab4 = st.tabs(["📊 데이터 입력", "🤖 AI 분석", "📄 리포트 생성", "📚 사용 가이드"])

# TAB 1: 데이터 입력
with tab1:
    st.header("데이터 업로드 및 검증")
    
    uploaded_file = st.file_uploader(
        "CSV 파일을 업로드하세요",
        type=['csv'],
        help="실험 데이터가 포함된 CSV 파일"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.uploaded_data = df
            
            st.success(f"✅ 데이터 로드 완료 ({len(df)}행 × {len(df.columns)}열)")
            
            with st.expander("📊 데이터 미리보기", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 행 수", len(df))
            with col2:
                st.metric("총 열 수", len(df.columns))
            with col3:
                numeric_count = len(df.select_dtypes(include=['number']).columns)
                st.metric("숫자형 열", numeric_count)
            
            st.subheader("🔍 데이터 품질 검증")
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X축 변수", numeric_cols, key="x_var")
                with col2:
                    y_col = st.selectbox(
                        "Y축 변수", 
                        numeric_cols, 
                        index=min(1, len(numeric_cols)-1),
                        key="y_var"
                    )
                
                if st.button("🔬 Standard Curve 검증", type="primary"):
                    with st.spinner("검증 중..."):
                        validation = st.session_state.validator.validate_standard_curve(
                            df, x_col, y_col
                        )
                        
                        if validation['is_valid']:
                            st.success(f"""
                            ✅ **데이터 품질 양호**
                            - R² = {validation['r_squared']:.4f}
                            - p-value = {validation['p_value']:.4e}
                            """)
                        else:
                            st.warning("⚠️ 데이터 품질 주의 필요")
                            for warning in validation['warnings']:
                                st.warning(warning)
            else:
                st.info("숫자형 열이 2개 이상 필요합니다.")
                
        except Exception as e:
            st.error(f"파일 로드 실패: {str(e)}")

# TAB 2: AI 분석
with tab2:
    st.header("🤖 Gemini AI 코드 생성")
    
    if st.session_state.uploaded_data is None:
        st.warning("먼저 '데이터 입력' 탭에서 CSV 파일을 업로드해주세요.")
    else:
        df = st.session_state.uploaded_data
        data_info = f"컬럼: {', '.join(df.columns.tolist())}"
        
        with st.expander("💡 프롬프트 예시 보기"):
            st.markdown("""
            **기초 통계:**
            - "각 그룹별 평균과 표준편차를 계산하고 막대그래프로 시각화하세요"
            
            **가설 검정:**
            - "3개 그룹 간 차이를 ANOVA로 검정하고, Tukey HSD 사후검정을 수행하세요"
            """)
        
        user_request = st.text_area(
            "원하는 분석을 자연어로 입력하세요",
            placeholder="예: CT 값을 그룹별로 비교하고, 통계적으로 유의한지 검정해주세요",
            height=120
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            generate_btn = st.button("🚀 AI 코드 생성", type="primary", use_container_width=True)
        with col2:
            use_context = st.checkbox("이전 분석 참고", value=True)
        
        if generate_btn:
            if not user_request:
                st.error("분석 요청사항을 입력해주세요")
            else:
                with st.spinner("🧠 Gemini가 코드를 생성하는 중..."):
                    try:
                        if use_context and st.session_state.code_history:
                            result = st.session_state.generator.generate_with_context(
                                user_input=user_request,
                                previous_code=st.session_state.code_history,
                                language=language.lower()
                            )
                        else:
                            result = st.session_state.generator.generate_analysis_code(
                                user_input=user_request,
                                language=language.lower(),
                                data_info=data_info
                            )
                        
                        st.success("✅ 코드 생성 완료!")
                        
                        st.subheader("📝 생성된 코드")
                        st.code(result['code'], language=language.lower())
                        
                        if result['interpretation']:
                            st.subheader("💡 결과 해석")
                            st.info(result['interpretation'])
                        
                        if result['warnings']:
                            st.subheader("⚠️ 주의사항")
                            st.warning(result['warnings'])
                        
                        st.session_state.code_history.append({
                            'language': language.lower(),
                            'code': result['code'],
                            'caption': user_request[:50] + "...",
                            'interpretation': result['interpretation'],
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                        st.success(f"✅ 리포트 생성 탭으로 이동하세요! (총 {len(st.session_state.code_history)}개 분석)")
                        
                    except Exception as e:
                        st.error(f"코드 생성 실패: {str(e)}")

# TAB 3: 리포트 생성
with tab3:
    st.header("📄 Quarto 리포트 생성")
    
    if not st.session_state.code_history:
        st.warning("'AI 분석' 탭에서 먼저 코드를 생성해주세요.")
    else:
        st.info(f"✅ 현재 **{len(st.session_state.code_history)}개의 분석**이 준비되었습니다.")
        
        col1, col2 = st.columns(2)
        with col1:
            output_format = st.selectbox(
                "출력 형식",
                ["HTML (웹 브라우저용)", "PDF (인쇄용)", "HTML + PDF"]
            )
        with col2:
            include_code = st.checkbox("코드 포함", value=True)
        
        theme = st.selectbox(
            "문서 테마",
            ["cosmo", "flatly", "darkly", "journal", "sketchy"]
        )
        
        if st.button("📄 최종 리포트 생성", type="primary", use_container_width=True):
            with st.spinner("📝 Quarto 문서 렌더링 중..."):
                try:
                    qmd_path = st.session_state.renderer.create_qmd_document(
                        title=exp_title,
                        author=exp_author,
                        experiment_date=str(exp_date),
                        code_chunks=st.session_state.code_history,
                        theme=theme,
                        code_fold=not include_code
                    )
                    
                    if "HTML" in output_format:
                        html_path = st.session_state.renderer.render_to_html(qmd_path)
                        
                        with open(html_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        st.download_button(
                            label="📥 HTML 리포트 다운로드",
                            data=html_content,
                            file_name=f"{exp_title}_{exp_date}.html",
                            mime="text/html",
                            use_container_width=True
                        )
                    
                    st.success("🎉 리포트 생성 완료!")
                    
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")

# TAB 4: 사용 가이드
with tab4:
    st.header("📚 Bio-Log 사용 가이드")
    st.markdown("""
    ## 🚀 빠른 시작
    
    1. **데이터 업로드**: CSV 파일 준비
    2. **AI 분석 요청**: 자연어로 분석 설명
    3. **리포트 다운로드**: HTML/PDF 선택
    
    ## 💡 팁
    - 구체적인 프롬프트 작성
    - 여러 분석을 순차적으로 수행
    - 결과를 항상 검토
    """)

# 푸터
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Bio-Log v2.0 (Google Cloud Edition)")
with col2:
    st.caption("Powered by Google Gemini 2.5")
with col3:
    st.caption("Team Anti-Gravity © 2025")
