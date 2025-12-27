# app.py
import streamlit as st
import pandas as pd
from agents.code_generator import BioCodeGenerator
from agents.validator import ExperimentValidator
from utils.quarto_renderer import QuartoRenderer
from utils.simple_html_renderer import SimpleHTMLRenderer
from utils.data_profiler import get_data_profile
from utils.example_data import ExampleDatasets, AnalysisTemplates
from utils.code_executor import CodeExecutor
import tempfile
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="DataViz Campus - AI 데이터 분석 학습 플랫폼",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - 대학생 친화적 디자인
st.markdown("""
<style>
    /* 메인 색상: 모던하고 밝은 파스텔 톤 */
    :root {
        --primary-color: #6366f1;  /* 인디고 */
        --secondary-color: #8b5cf6;  /* 바이올렛 */
        --accent-color: #ec4899;  /* 핑크 */
        --success-color: #10b981;  /* 그린 */
        --warning-color: #f59e0b;  /* 앰버 */
    }

    /* 헤더 스타일링 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }

    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }

    /* 카드 스타일 */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }

    .info-card h3 {
        color: #667eea;
        margin-top: 0;
    }

    /* 버튼 스타일 */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* 성공 메시지 스타일 */
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    /* 탭 스타일 개선 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }

    /* 메트릭 카드 */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

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

if 'executor' not in st.session_state:
    # Create temp directory for execution results
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix='dataviz_')
    st.session_state.executor = CodeExecutor(temp_dir=temp_dir)
    st.session_state.temp_dir = temp_dir

if 'code_history' not in st.session_state:
    st.session_state.code_history = []

if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

# 헤더 - 대학생 친화적
st.markdown("""
<div class="main-header">
    <h1>📊 DataViz Campus</h1>
    <p>🎓 대학생을 위한 AI 기반 데이터 분석 학습 플랫폼 | Powered by Google Gemini 2.5 Flash</p>
</div>
""", unsafe_allow_html=True)

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

# 사이드바 - 학생 친화적 디자인
with st.sidebar:
    st.markdown("### 📚 프로젝트 설정")

    exp_title = st.text_input(
        "분석 제목",
        "나의 데이터 분석 프로젝트",
        help="리포트 상단에 표시될 제목입니다"
    )
    exp_author = st.text_input(
        "분석자 이름",
        "대학생",
        help="본인의 이름 또는 팀명을 입력하세요"
    )
    exp_date = st.date_input(
        "분석 날짜",
        datetime.now(),
        help="분석을 수행한 날짜"
    )

    st.divider()

    st.markdown("### 🤖 AI 모델 설정")
    model_choice = st.selectbox(
        "Gemini 모델",
        ["gemini-2.5-flash (추천)", "gemini-2.0-flash"],
        help="💡 2.5 Flash 권장: 더 안정적이고 할당량이 많습니다",
        key="model_selector"
    )
    
    # Extract model name from selection
    selected_model = "gemini-2.5-flash" if "2.5" in model_choice else "gemini-2.0-flash"
    
    # Reinitialize generator if model changed
    if 'current_model' not in st.session_state:
        st.session_state.current_model = selected_model
    
    if st.session_state.get('current_model') != selected_model:
        try:
            st.session_state.generator = BioCodeGenerator(model_name=selected_model)
            st.session_state.current_model = selected_model
            st.success(f"✅ 모델이 {selected_model}로 변경되었습니다")
        except Exception as e:
            st.error(f"모델 변경 실패: {str(e)}")
    
    language = st.selectbox("분석 언어", ["Python", "R"])
    
    st.divider()
    st.metric("생성된 분석 수", len(st.session_state.code_history))
    
    if st.button("🗑️ 전체 초기화"):
        st.session_state.code_history = []
        st.session_state.uploaded_data = None
        st.rerun()

# 메인 영역 - 탭에 더 명확한 설명 추가
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 1단계: 데이터",
    "🤖 2단계: AI 분석",
    "📄 3단계: 리포트",
    "💡 예제 & 템플릿",
    "📚 사용 가이드"
])

# TAB 1: 데이터 입력
with tab1:
    st.markdown("### 📊 데이터 준비하기")
    st.info("💡 **시작하기**: 분석할 CSV 파일을 업로드하거나, 아래 '예제 & 템플릿' 탭에서 연습용 데이터를 사용해보세요!")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "📁 CSV 파일 선택",
            type=['csv'],
            help="쉼표로 구분된 데이터 파일 (.csv)을 업로드하세요"
        )

    with col2:
        st.markdown("#### 💾 예제 데이터 다운로드")
        if st.button("📥 학생 성적 데이터", use_container_width=True):
            example_df = ExampleDatasets.create_student_grades()
            csv = example_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "⬇️ 다운로드 (student_grades.csv)",
                csv,
                "student_grades.csv",
                "text/csv",
                use_container_width=True
            )
        if st.button("📥 실험 측정 데이터", use_container_width=True):
            example_df = ExampleDatasets.create_experiment_measurements()
            csv = example_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "⬇️ 다운로드 (experiment_data.csv)",
                csv,
                "experiment_data.csv",
                "text/csv",
                use_container_width=True
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
    st.markdown("### 🤖 AI와 함께 데이터 분석하기")

    if st.session_state.uploaded_data is None:
        st.warning("⚠️ 먼저 **'1단계: 데이터'** 탭에서 CSV 파일을 업로드해주세요!")
        st.info("👉 예제 데이터로 연습하고 싶다면 '예제 & 템플릿' 탭을 확인하세요.")
    else:
        df = st.session_state.uploaded_data

        st.success(f"✅ 데이터 로드 완료! {len(df)}행 × {len(df.columns)}열")

        # Show existing analyses first
        if st.session_state.code_history:
            st.markdown(f"### 📝 생성된 분석 ({len(st.session_state.code_history)}개)")
            for idx, item in enumerate(st.session_state.code_history, 1):
                with st.expander(f"분석 #{idx}: {item['caption']}", expanded=False):
                    st.code(item['code'], language=item['language'])
                    if item.get('interpretation'):
                        st.info(f"💡 {item['interpretation']}")
                    st.caption(f"생성 시간: {item['timestamp']}")

        with st.sidebar:
            st.divider()
            st.markdown("### 🎯 분석 초점")
            target_var = st.selectbox(
                "종속 변수 (Target)",
                ["없음 - 일반 탐색"] + df.columns.tolist(),
                help="📌 특정 변수를 예측하거나 분석하고 싶다면 선택하세요. AI가 해당 변수 중심으로 분석합니다."
            )
            target_variable = None if target_var == "없음 - 일반 탐색" else target_var

        data_info = get_data_profile(df)

        # 템플릿 선택 추가
        st.markdown("#### 🎨 분석 템플릿 (선택사항)")
        templates = AnalysisTemplates.get_templates()
        template_options = ["직접 입력"] + [f"{v['name']}" for k, v in templates.items()]

        selected_template = st.selectbox(
            "자주 사용하는 분석 유형 선택",
            template_options,
            help="템플릿을 선택하면 프롬프트가 자동으로 채워집니다"
        )

        # 템플릿 선택 시 프롬프트 자동 입력
        default_prompt = ""
        if selected_template != "직접 입력":
            template_key = [k for k, v in templates.items() if v['name'] == selected_template][0]
            default_prompt = templates[template_key]['prompt']
            st.info(f"📝 선택한 템플릿: **{selected_template}**")

        with st.expander("💡 프롬프트 예시 더 보기", expanded=False):
            st.markdown("""
            **🔢 기술통계:**
            - "각 변수의 평균, 중앙값, 표준편차를 계산하고 히스토그램으로 분포를 보여주세요"
            - "그룹별 요약 통계를 표로 만들고 박스플롯으로 비교해주세요"

            **📊 시각화:**
            - "Plotly로 인터랙티브한 scatter plot을 만들어주세요"
            - "변수 간 상관관계를 히트맵으로 보여주세요"

            **📈 가설 검정:**
            - "두 그룹 간 평균 차이가 유의한지 T-test로 검정해주세요"
            - "3개 그룹 간 차이를 ANOVA로 검정하고 사후검정도 수행해주세요"

            **🔍 회귀 분석:**
            - "X 변수로 Y 변수를 예측하는 회귀 모델을 만들고 R-squared를 계산해주세요"
            """)
        
        user_request = st.text_area(
            "🗣️ AI에게 요청할 분석 내용",
            value=default_prompt,
            placeholder="예: 전공별로 성적을 비교하고, 통계적으로 유의한 차이가 있는지 ANOVA로 검정해주세요",
            height=120,
            help="평소에 말하듯이 편하게 적어주세요! AI가 이해하고 코드를 생성합니다."
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
                                language=language.lower(),
                                data_info=data_info,
                                target_variable=target_variable
                            )
                        else:
                            result = st.session_state.generator.generate_analysis_code(
                                user_input=user_request,
                                language=language.lower(),
                                data_info=data_info,
                                target_variable=target_variable
                            )
                        
                        st.success("✅ 코드 생성 완료!")

                        st.subheader("📝 생성된 코드")
                        st.code(result['code'], language=language.lower())

                        # 코드 실행 및 결과 캡처 (Python만 지원)
                        execution_result = None
                        auto_fix_attempted = False

                        if language.lower() == 'python':
                            with st.spinner("🔄 코드 실행 중..."):
                                try:
                                    # 데이터 파일 경로 준비
                                    data_path = None
                                    if st.session_state.uploaded_data is not None:
                                        # Save to temp file
                                        import tempfile
                                        temp_data = tempfile.NamedTemporaryFile(
                                            mode='w',
                                            suffix='.csv',
                                            delete=False,
                                            encoding='utf-8',
                                            dir=st.session_state.temp_dir
                                        )
                                        st.session_state.uploaded_data.to_csv(temp_data.name, index=False, encoding='utf-8')
                                        data_path = temp_data.name
                                        temp_data.close()

                                    # 코드 실행
                                    execution_result = st.session_state.executor.execute_python_code(
                                        code=result['code'],
                                        data_path=data_path
                                    )

                                    if execution_result['success']:
                                        st.success("✅ 코드 실행 성공!")

                                        # 출력 결과 표시
                                        if execution_result['stdout']:
                                            st.subheader("📊 실행 결과")
                                            st.text(execution_result['stdout'])

                                        # 그래프 표시
                                        if execution_result['figure_data']:
                                            st.subheader("📈 생성된 그래프")
                                            for i, fig_data in enumerate(execution_result['figure_data'], 1):
                                                if fig_data.startswith('<'):  # HTML (Plotly)
                                                    st.components.v1.html(fig_data, height=600)
                                                else:  # base64 이미지
                                                    st.image(f"data:image/png;base64,{fig_data}")
                                    else:
                                        # 에러 발생 시 자동 수정 시도
                                        st.error("❌ 코드 실행 실패")
                                        st.error(execution_result['error'])

                                        # Gemini에게 수정 요청
                                        if st.button("🔧 AI로 자동 수정 시도", key="auto_fix_btn"):
                                            with st.spinner("🤖 Gemini가 코드를 수정하는 중..."):
                                                try:
                                                    fixed_result = st.session_state.generator.fix_code_error(
                                                        broken_code=result['code'],
                                                        error_message=execution_result['error'],
                                                        language=language.lower(),
                                                        data_info=data_info
                                                    )

                                                    st.success("✅ 코드 수정 완료!")
                                                    st.subheader("🔧 수정된 코드")
                                                    st.code(fixed_result['code'], language=language.lower())

                                                    if fixed_result['interpretation']:
                                                        st.info(f"💡 수정 내용: {fixed_result['interpretation']}")

                                                    # 수정된 코드 재실행
                                                    with st.spinner("🔄 수정된 코드 실행 중..."):
                                                        execution_result = st.session_state.executor.execute_python_code(
                                                            code=fixed_result['code'],
                                                            data_path=data_path
                                                        )

                                                        if execution_result['success']:
                                                            st.success("🎉 수정된 코드 실행 성공!")

                                                            # 출력 결과 표시
                                                            if execution_result['stdout']:
                                                                st.subheader("📊 실행 결과")
                                                                st.text(execution_result['stdout'])

                                                            # 그래프 표시
                                                            if execution_result['figure_data']:
                                                                st.subheader("📈 생성된 그래프")
                                                                for i, fig_data in enumerate(execution_result['figure_data'], 1):
                                                                    if fig_data.startswith('<'):
                                                                        st.components.v1.html(fig_data, height=600)
                                                                    else:
                                                                        st.image(f"data:image/png;base64,{fig_data}")

                                                            # 수정된 코드를 result에 반영
                                                            result = fixed_result
                                                            auto_fix_attempted = True
                                                        else:
                                                            st.error("❌ 수정된 코드도 실행 실패")
                                                            st.error(execution_result['error'])
                                                            st.warning("💡 수동으로 코드를 수정하거나, 다른 방식으로 요청해주세요.")

                                                except Exception as fix_error:
                                                    st.error(f"❌ 자동 수정 실패: {str(fix_error)}")
                                                    st.info("💡 리포트 생성 시 Quarto가 다시 실행을 시도합니다.")

                                except Exception as exec_error:
                                    st.warning(f"⚠️ 코드 실행 중 오류: {str(exec_error)}")
                                    st.info("💡 리포트 생성 시 Quarto가 다시 실행을 시도합니다.")

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
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'execution_result': execution_result  # 실행 결과 저장
                        })

                        # 성공 시 자동으로 Tab 3으로 안내
                        if execution_result and execution_result['success']:
                            st.success(f"🎉 분석 완료! (총 {len(st.session_state.code_history)}개)")
                            st.info("👉 **3단계: 리포트 생성** 탭으로 이동하여 최종 리포트를 만들어보세요!")

                            # Auto-scroll suggestion
                            st.markdown("""
                            <script>
                                // Scroll to top to see tabs
                                window.parent.document.querySelector('[data-testid="stVerticalBlock"]').scrollIntoView();
                            </script>
                            """, unsafe_allow_html=True)
                        else:
                            st.success(f"✅ 코드 저장 완료! (총 {len(st.session_state.code_history)}개 분석)")
                            if not execution_result or not execution_result['success']:
                                st.warning("⚠️ 코드 실행은 실패했지만 저장되었습니다. '3단계: 리포트 생성' 탭에서 Quarto가 다시 실행을 시도합니다.")
                        
                    except Exception as e:
                        error_msg = str(e)
                        
                        # Check if it's a rate limit error
                        if "할당량" in error_msg or "429" in error_msg or "quota" in error_msg:
                            st.error("⚠️ API 할당량 초과")
                            st.warning(error_msg)
                            
                            # Show helpful suggestions
                            with st.expander("💡 해결 방법", expanded=True):
                                st.markdown("""
                                **즉시 해결:**
                                1. 사이드바에서 모델을 **'gemini-2.0-flash'**로 변경 후 다시 시도
                                2. 몇 분 후 다시 시도 (Free tier는 하루 20회 제한)
                                
                                **장기 해결:**
                                - [할당량 확인](https://ai.dev/usage?tab=rate-limit)
                                - [유료 플랜 업그레이드](https://ai.google.dev/pricing)
                                - 여러 API 키를 번갈아 사용
                                """)
                        else:
                            st.error(f"코드 생성 실패: {error_msg}")

# TAB 3: 리포트 생성
with tab3:
    st.header("📄 리포트 생성")

    if not st.session_state.code_history:
        st.warning("'AI 분석' 탭에서 먼저 코드를 생성해주세요.")
    else:
        st.info(f"✅ 현재 **{len(st.session_state.code_history)}개의 분석**이 준비되었습니다.")

        st.info("📌 **Quarto 방식**: 코드를 실제로 실행하여 그래프, 표, 통계 분석 결과를 리포트에 포함합니다")

        col1, col2 = st.columns(2)
        with col1:
            output_format = st.selectbox(
                "출력 형식",
                ["HTML (웹 브라우저용)", "PDF (인쇄용)", "HTML + PDF"]
            )
        with col2:
            include_code = st.checkbox("코드 표시", value=False,
                                     help="체크 해제: 결과만 표시 (추천) | 체크: 코드도 함께 표시")

        theme = st.selectbox(
            "문서 테마",
            ["cosmo", "flatly", "darkly", "journal", "sketchy"]
        )

        if st.button("📄 최종 리포트 생성", type="primary", use_container_width=True):
            with st.spinner("📝 Quarto 문서 렌더링 중..."):
                try:
                    # Prepare data file path if data is uploaded
                    data_file_path = None
                    if st.session_state.uploaded_data is not None:
                        # Save uploaded data to temp file
                        import tempfile
                        temp_data = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
                        st.session_state.uploaded_data.to_csv(temp_data.name, index=False, encoding='utf-8')
                        data_file_path = temp_data.name
                        temp_data.close()

                    # Step 1: Create QMD file
                    qmd_path = st.session_state.renderer.create_qmd_document(
                        title=exp_title,
                        author=exp_author,
                        experiment_date=str(exp_date),
                        code_chunks=st.session_state.code_history,
                        theme=theme,
                        code_fold=not include_code,
                        data_file_path=data_file_path
                    )

                    st.success(f"✅ QMD 파일 생성 완료: `{qmd_path.name}`")

                    # Read QMD content for download
                    with open(qmd_path, 'r', encoding='utf-8') as f:
                        qmd_content = f.read()

                    # Step 2: Render to HTML and/or PDF first, collect all downloads
                    html_content = None
                    pdf_content = None

                    if "HTML" in output_format:
                        with st.spinner("🔄 Quarto로 HTML 렌더링 중..."):
                            try:
                                html_path = st.session_state.renderer.render_to_html(qmd_path)
                                with open(html_path, 'r', encoding='utf-8') as f:
                                    html_content = f.read()
                                st.success("🎉 HTML 리포트 생성 완료!")
                            except Exception as render_error:
                                st.error(f"❌ HTML 렌더링 실패: {str(render_error)}")

                    if "PDF" in output_format:
                        with st.spinner("🔄 Quarto로 PDF 렌더링 중..."):
                            try:
                                pdf_path = st.session_state.renderer.render_to_pdf(qmd_path)
                                with open(pdf_path, 'rb') as f:
                                    pdf_content = f.read()
                                st.success("🎉 PDF 리포트 생성 완료!")
                            except Exception as pdf_error:
                                st.error(f"❌ PDF 렌더링 실패: {str(pdf_error)}")
                                st.info("💡 PDF 생성에는 LaTeX(TinyTeX 등) 설치가 필요합니다. 'quarto install tinytex' 명령어를 실행해보세요.")

                    # Step 3: Show all download buttons together
                    st.markdown("### 📥 다운로드")

                    download_cols = []
                    if html_content:
                        download_cols.append("HTML")
                    if pdf_content:
                        download_cols.append("PDF")
                    download_cols.append("QMD")

                    cols = st.columns(len(download_cols))

                    col_idx = 0
                    if html_content:
                        with cols[col_idx]:
                            st.download_button(
                                label="📥 HTML 리포트",
                                data=html_content,
                                file_name=f"{exp_title}_{exp_date}.html",
                                mime="text/html",
                                key="dl_html",
                                use_container_width=True
                            )
                        col_idx += 1

                    if pdf_content:
                        with cols[col_idx]:
                            st.download_button(
                                label="📥 PDF 리포트",
                                data=pdf_content,
                                file_name=f"{exp_title}_{exp_date}.pdf",
                                mime="application/pdf",
                                key="dl_pdf",
                                use_container_width=True
                            )
                        col_idx += 1

                    # QMD download always available
                    with cols[col_idx]:
                        st.download_button(
                            label="📄 QMD 파일",
                            data=qmd_content,
                            file_name=f"{exp_title}_{exp_date}.qmd",
                            mime="text/plain",
                            key="dl_qmd",
                            use_container_width=True,
                            help="디버깅용 원본 파일"
                        )

                    if not html_content and not pdf_content:
                        st.info("💡 QMD 파일을 다운로드하여 수동으로 렌더링할 수 있습니다.")

                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")

# TAB 4: 예제 & 템플릿
with tab4:
    st.markdown("### 💡 예제 데이터 & 분석 템플릿")
    st.info("🎓 **학습 팁**: 예제 데이터로 먼저 연습해보세요! 다양한 분석 방법을 배울 수 있습니다.")

    # 예제 데이터셋 소개
    st.markdown("#### 📦 제공되는 예제 데이터셋")

    datasets_info = ExampleDatasets.get_dataset_info()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### 🎓 학생 성적 데이터")
        info = datasets_info['student_grades']
        st.write(f"**{info['description']}**")
        st.write(f"📏 크기: {info['rows']}행 × {info['columns']}열")
        st.write("**활용 예시:**")
        for use_case in info['use_cases']:
            st.write(f"- {use_case}")

        if st.button("📥 성적 데이터 다운로드", key="dl_grades", use_container_width=True):
            df = ExampleDatasets.create_student_grades()
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "⬇️ student_grades.csv",
                csv,
                "student_grades.csv",
                "text/csv",
                key="dl_grades_btn",
                use_container_width=True
            )

    with col2:
        st.markdown("##### 🧪 실험 측정 데이터")
        info = datasets_info['experiment_measurements']
        st.write(f"**{info['description']}**")
        st.write(f"📏 크기: {info['rows']}행 × {info['columns']}열")
        st.write("**활용 예시:**")
        for use_case in info['use_cases']:
            st.write(f"- {use_case}")

        if st.button("📥 실험 데이터 다운로드", key="dl_exp", use_container_width=True):
            df = ExampleDatasets.create_experiment_measurements()
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "⬇️ experiment_data.csv",
                csv,
                "experiment_data.csv",
                "text/csv",
                key="dl_exp_btn",
                use_container_width=True
            )

    with col3:
        st.markdown("##### 📊 설문조사 데이터")
        info = datasets_info['survey_data']
        st.write(f"**{info['description']}**")
        st.write(f"📏 크기: {info['rows']}행 × {info['columns']}열")
        st.write("**활용 예시:**")
        for use_case in info['use_cases']:
            st.write(f"- {use_case}")

        if st.button("📥 설문 데이터 다운로드", key="dl_survey", use_container_width=True):
            df = ExampleDatasets.create_survey_data()
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "⬇️ survey_data.csv",
                csv,
                "survey_data.csv",
                "text/csv",
                key="dl_survey_btn",
                use_container_width=True
            )

    st.divider()

    # 분석 템플릿 소개
    st.markdown("#### 🎨 분석 템플릿 라이브러리")
    st.write("자주 사용하는 분석 유형의 프롬프트 템플릿입니다. **'2단계: AI 분석'** 탭에서 선택할 수 있습니다.")

    templates = AnalysisTemplates.get_templates()

    for key, template in templates.items():
        with st.expander(f"📌 {template['name']}", expanded=False):
            st.markdown(f"**프롬프트 예시:**")
            st.code(template['prompt'], language='text')
            st.markdown(f"**태그:** {', '.join([f'`{tag}`' for tag in template['tags']])}")

# TAB 5: 사용 가이드
with tab5:
    st.markdown("### 📚 DataViz Campus 사용 가이드")

    st.markdown("""
    ## 🎯 이 플랫폼은 무엇인가요?

    **DataViz Campus**는 대학생들이 데이터 분석을 쉽게 배우고 실습할 수 있도록 만든 AI 기반 학습 플랫폼입니다.

    ### ✨ 주요 기능
    - 🤖 **AI 코드 생성**: 자연어로 요청하면 Python 분석 코드 자동 생성
    - 📊 **인터랙티브 시각화**: Plotly를 활용한 줌 가능한 그래프
    - 📄 **자동 리포트**: HTML/PDF 형식의 전문적인 분석 보고서
    - 🎓 **교육적 설명**: 통계 용어와 결과를 학생 눈높이로 해석
    - 💾 **예제 데이터**: 연습용 데이터셋 3종 제공

    ---

    ## 🚀 3단계로 시작하기

    ### 1️⃣ 데이터 준비
    - **본인 데이터**: CSV 파일을 '1단계: 데이터' 탭에서 업로드
    - **예제 데이터**: '예제 & 템플릿' 탭에서 다운로드하여 연습

    ### 2️⃣ AI에게 분석 요청
    - '2단계: AI 분석' 탭으로 이동
    - 템플릿 선택 또는 직접 입력
    - 예: *"전공별로 성적을 비교하고 통계적 차이를 검정해주세요"*
    - 🚀 버튼 클릭!

    ### 3️⃣ 리포트 생성
    - '3단계: 리포트' 탭으로 이동
    - 원하는 형식 선택 (HTML 추천 - 인터랙티브!)
    - 테마 선택 (cosmo, flatly 등)
    - 📄 버튼 클릭하여 다운로드

    ---

    ## 💡 효과적인 프롬프트 작성법

    ### ✅ 좋은 프롬프트 예시
    - "전공별 중간고사 평균을 비교하고, ANOVA로 유의한 차이가 있는지 검정해주세요"
    - "농도와 흡광도의 상관관계를 scatter plot으로 그리고 회귀식을 구해주세요"
    - "Plotly로 성별과 연령대에 따른 만족도 분포를 인터랙티브하게 보여주세요"

    ### ❌ 모호한 프롬프트 예시
    - "분석해주세요" (무엇을?)
    - "그래프 그려주세요" (어떤 변수를?)
    - "통계 내주세요" (어떤 검정을?)

    ### 🔑 팁
    1. **구체적으로**: 어떤 변수를, 어떤 방법으로, 어떻게 시각화할지 명시
    2. **한 번에 하나씩**: 복잡한 분석은 단계별로 나눠서 요청
    3. **이전 분석 참고**: "이전 분석 참고" 체크박스 활용

    ---

    ## 🔬 통계 용어 설명

    ### 📊 기술통계
    - **평균 (Mean)**: 모든 값을 더한 후 개수로 나눈 값
    - **중앙값 (Median)**: 크기 순으로 정렬했을 때 가운데 값
    - **표준편차 (Std)**: 데이터가 평균에서 얼마나 퍼져있는지

    ### 🧪 가설검정
    - **T-test**: 두 그룹의 평균이 다른지 검정
    - **ANOVA**: 3개 이상 그룹의 평균이 다른지 검정
    - **P-value**: 0.05보다 작으면 "통계적으로 유의함"

    ### 📈 회귀분석
    - **R-squared**: 모델의 설명력 (1에 가까울수록 좋음)
    - **회귀식**: Y = aX + b 형태의 예측 공식

    ---

    ## ⚙️ 시스템 요구사항

    ### 필수 소프트웨어
    - ✅ Python 3.8 이상
    - ✅ Quarto CLI ([quarto.org](https://quarto.org) 에서 설치)
    - ✅ Google API 키 (무료: [ai.google.dev](https://ai.google.dev))

    ### 선택사항 (PDF 생성 시)
    - LaTeX (TinyTeX): `quarto install tinytex` 명령어로 설치

    ---

    ## 🆘 자주 묻는 질문 (FAQ)

    **Q1. "API 할당량 초과" 오류가 나요**
    - 무료 API는 하루 20회 제한이 있습니다
    - 사이드바에서 다른 모델(2.0 Flash)로 변경해보세요
    - 또는 몇 분 후 다시 시도

    **Q2. 그래프가 리포트에 안 나와요**
    - 최신 버전은 Plotly를 우선 사용합니다 (자동 렌더링)
    - Matplotlib는 `plt.show()` 제거됨 (Quarto가 자동 처리)

    **Q3. 한글이 깨져요**
    - Windows: 맑은 고딕 자동 설정
    - Mac: AppleGothic 자동 설정
    - 시스템 폰트가 없으면 설치 필요

    **Q4. 어떤 분석부터 시작하면 좋나요?**
    1. 기술통계 (평균, 표준편차)
    2. 시각화 (히스토그램, 박스플롯)
    3. 가설검정 (T-test, ANOVA)
    4. 회귀분석 (관계 파악)

    ---

    ## 📞 문의 & 피드백

    버그 리포트나 기능 제안은 GitHub Issues로 남겨주세요!
    """)

# 푸터 - 학생 친화적
st.divider()
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
    <h4 style='margin: 0;'>📊 DataViz Campus</h4>
    <p style='margin: 0.5rem 0; opacity: 0.9;'>대학생을 위한 AI 데이터 분석 학습 플랫폼</p>
    <p style='margin: 0; font-size: 0.9rem;'>v4.0 Student Edition | Powered by Google Gemini 2.5 Flash | 2025</p>
</div>
""", unsafe_allow_html=True)
