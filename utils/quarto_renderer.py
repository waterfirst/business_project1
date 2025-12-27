# utils/quarto_renderer.py
import os
import subprocess
import tempfile
import shutil
import re
from pathlib import Path
from typing import Optional, List
import textwrap

class QuartoRenderer:
    """Quarto 문서 생성 및 렌더링"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_file_path = None
        
    def create_qmd_document(
        self, 
        title: str,
        author: str,
        experiment_date: str,
        code_chunks: List[dict],
        theme: str = "cosmo",
        code_fold: bool = True,
        output_path: Optional[str] = None,
        data_file_path: Optional[str] = None
    ) -> Path:
        """Quarto 문서 생성 (v3.0 - 들여쓰기 완벽 제거 버전)"""
        
        # Determine processing engine based on language
        is_r = any(chunk.get('language', '').lower() == 'r' for chunk in code_chunks)
        if is_r:
            engine_section = "engine: knitr"
        else:
            engine_section = "jupyter: python3"
        
        # Professional CSS for the report
        custom_css = textwrap.dedent("""
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code&display=swap');

            :root {
              --primary: #004e92;
              --secondary: #000428;
              --accent: #fdbb2d;
              --text: #2d3436;
              --bg: #ffffff;
            }

            body {
              font-family: 'Inter', -apple-system, system-ui, sans-serif;
              color: var(--text);
              background-color: var(--bg);
              line-height: 1.7;
            }

            .quarto-title-block .quarto-title-banner {
              background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
              padding: 5rem 0;
              margin-bottom: 3rem;
              border-radius: 0 0 30px 30px;
              box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            }

            .abstract-box {
              background: #f8faff;
              padding: 2.5rem;
              border-radius: 20px;
              border-left: 10px solid var(--primary);
              margin-bottom: 4rem;
              box-shadow: 0 15px 45px rgba(0,0,0,0.04);
            }

            h2 {
              color: var(--secondary);
              border-bottom: 4px solid var(--accent);
              display: inline-block;
              padding-bottom: 5px;
              margin-top: 4rem;
              font-weight: 700;
              letter-spacing: -0.5px;
            }

            .callout-note.callout {
              border-left-color: var(--primary) !important;
              background-color: #f1f7ff !important;
              border-radius: 12px !important;
              padding: 1.5rem !important;
            }

            pre, code {
              font-family: 'Fira Code', monospace !important;
              font-size: 0.95em !important;
            }

            .card-grid {
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 20px;
            }
        """).strip()
        
        # Write CSS to a file
        css_path = self.temp_dir / "custom_style.css"
        css_path.write_text(custom_css, encoding='utf-8-sig')
        
        # Copy data file to temp directory if provided
        if data_file_path and Path(data_file_path).exists():
            data_file_name = Path(data_file_path).name
            temp_data_path = self.temp_dir / data_file_name
            shutil.copy2(data_file_path, temp_data_path)
            self.data_file_path = str(temp_data_path)
            
            # LLM이 흔히 'data.csv'로 가정하므로, 실제 파일명이 다르더라도 복사본 생성
            if data_file_name != 'data.csv':
                try:
                    shutil.copy2(data_file_path, self.temp_dir / 'data.csv')
                except Exception:
                    pass
        elif data_file_path:
            # If path doesn't exist, try to use it as-is (might be relative)
            self.data_file_path = data_file_path

        # Assemble document line by line to guarantee zero indentation
        lines = []
        
        # YAML Header
        lines.append("---")
        # Escape quotes in YAML values (escape backslash first, then quotes)
        escaped_title = str(title).replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        escaped_author = str(author).replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        escaped_date = str(experiment_date).replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        lines.append(f'title: "{escaped_title}"')
        lines.append('subtitle: "AI-Powered Bio-Data Analysis Executive Report"')
        lines.append(f'author: "{escaped_author}"')
        lines.append(f'date: "{escaped_date}"')
        lines.append("lang: ko")
        # Set execution engine
        if is_r:
            lines.append("engine: knitr")
        else:
            # For Python, use jupyter engine
            lines.append("jupyter: python3")
        lines.append("format:")
        lines.append("  html:")
        lines.append(f"    theme: {theme}")
        lines.append("    css: custom_style.css")
        lines.append("    title-block-banner: true")
        lines.append(f"    code-fold: {'true' if code_fold else 'false'}")
        lines.append('    code-summary: "분석 소스 코드 보기"')
        lines.append("    code-tools: true")
        lines.append("    df-print: paged")
        lines.append("    toc: true")
        lines.append("    toc-location: left")
        lines.append("    number-sections: true")
        lines.append("    embed-resources: true")
        lines.append("    html-math-method: katex")
        lines.append("execute:")
        lines.append("  warning: false")
        lines.append("  message: false")
        lines.append("  echo: true")   # Show code by default (user can fold it)
        lines.append("  eval: true")   # Enable execution to show results
        lines.append("  output: true") # Show output
        lines.append("---")
        lines.append("")
        lines.append("")
        
        # Abstract Section
        lines.append(f"## 실험 요약 및 컨텍스트 {{.unnumbered}}")
        lines.append("")
        lines.append("::: {.abstract-box}")
        lines.append("")
        lines.append("::: {.grid}")
        lines.append("")
        lines.append("::: {.g-col-6}")
        lines.append(f"- **실험 프로젝트**: {title}")
        lines.append(f"- **수석 연구원**: {author}")
        lines.append(f"- **분석 일시**: {experiment_date}")
        lines.append(":::")
        lines.append("")
        lines.append("::: {.g-col-6}")
        lines.append("- **시스템 버전**: Bio-Log v3.0 Professional")
        lines.append("- **AI 엔진**: Google Gemini 2.5 Flash")
        lines.append(f"- **분석 항목**: 총 {len(code_chunks)}개의 핵심 모듈")
        lines.append(":::")
        lines.append("")
        lines.append(":::") # End Grid
        lines.append("")
        lines.append(":::") # End Abstract Box
        lines.append("")
        lines.append("---")
        lines.append("")

        # Content Blocks
        for i, chunk in enumerate(code_chunks, 1):
            lang = chunk.get('language', 'python').lower()
            code = chunk.get('code', '').strip()
            caption = chunk.get('caption', f'Analysis {i}')
            interpretation = chunk.get('interpretation', '')
            
            # Ensure code blocks start at Col 0
            lines.append(f"## 분석 {i}: {caption}")
            lines.append("")
            
            # Code Block - ensure proper formatting
            if lang == 'r':
                lines.append(f"```{{r}}")
            else:
                lines.append(f"```{{python}}")
            lines.append(f"#| label: fig-analysis-{i}")
            # Clean caption for YAML: remove quotes and special characters that cause issues
            # Remove all quotes from caption to avoid YAML parsing errors
            clean_caption = str(caption).replace('"', '').replace("'", '').strip()
            # Truncate if too long to avoid YAML issues
            if len(clean_caption) > 200:
                clean_caption = clean_caption[:197] + "..."
            # Use YAML quoted string format - escape any remaining special chars
            # If caption contains colons or other YAML special chars, wrap in quotes
            if ':' in clean_caption or clean_caption.startswith('-') or clean_caption.startswith('#'):
                # Escape backslashes and quotes if we need to quote
                safe_caption = clean_caption.replace('\\', '\\\\').replace('"', '\\"')
                lines.append(f'#| fig-cap: "{safe_caption}"')
            else:
                # Simple string without quotes (safer for YAML)
                lines.append(f'#| fig-cap: {clean_caption}')
            lines.append("#| echo: true")   # Show code (students can learn from it)
            lines.append("#| eval: true")   # Execute code to show results
            lines.append("#| output: asis") # Show output as-is (better for plots)
            lines.append("#| warning: false")
            lines.append("#| error: true")  # Show errors so we can debug
            # For Python plots to display properly
            if lang == 'python':
                lines.append("#| fig-width: 12")
                lines.append("#| fig-height: 8")
                lines.append("#| fig-dpi: 300")
                lines.append("#| fig-format: retina")  # High-res displays
            
            # Add data loading and setup if data file is provided
            if self.data_file_path:
                data_file_name = Path(self.data_file_path).name
                # Use forward slashes for cross-platform compatibility
                data_file_name = data_file_name.replace('\\', '/')
                
                if lang == 'python':
                    # Only add data loading if not already in code
                    if 'read_csv' not in code.lower() and 'pd.read_csv' not in code.lower():
                        lines.append("# 데이터 로드")
                        lines.append("import pandas as pd")
                        lines.append(f"df = pd.read_csv('{data_file_name}')")
                        lines.append("")

                    # Plotly 지원 추가 (인터랙티브 차트용)
                    if 'plotly' in code.lower() or 'px.' in code.lower():
                        if 'import plotly' not in code.lower():
                            lines.append("# Plotly 인터랙티브 시각화 설정")
                            lines.append("import plotly.express as px")
                            lines.append("import plotly.graph_objects as go")
                            lines.append("")

                    # Matplotlib/Seaborn 지원 (정적 차트용)
                    if ('matplotlib' in code.lower() or 'plt.' in code.lower() or
                        'seaborn' in code.lower() or 'sns.' in code.lower()):
                        if 'import matplotlib' not in code.lower():
                            lines.append("# Matplotlib/Seaborn 시각화 설정 (한글 폰트 지원)")
                            lines.append("import matplotlib.pyplot as plt")
                            lines.append("import seaborn as sns")
                            lines.append("sns.set_theme(style='whitegrid', palette='Set2')")
                            lines.append("import platform")
                            lines.append("if platform.system() == 'Windows':")
                            lines.append("    plt.rc('font', family='Malgun Gothic')")
                            lines.append("elif platform.system() == 'Darwin':")
                            lines.append("    plt.rc('font', family='AppleGothic')")
                            lines.append("else:")
                            lines.append("    plt.rc('font', family='NanumGothic')")
                            lines.append("plt.rcParams['axes.unicode_minus'] = False")
                            lines.append("")
                elif lang == 'r':
                    lines.append("# 한글 폰트 및 시각화 설정")
                    lines.append("if(Sys.info()['sysname'] == 'Windows') try(windowsFonts(Malgun = windowsFont('Malgun Gothic')), silent=TRUE)")
                    lines.append("if(requireNamespace('ggplot2', quietly=TRUE)) {")
                    lines.append("  if(Sys.info()['sysname'] == 'Windows') {")
                    lines.append("    try(ggplot2::theme_set(ggplot2::theme_minimal(base_family = 'Malgun')), silent=TRUE)")
                    lines.append("  } else if(Sys.info()['sysname'] == 'Darwin') {")
                    lines.append("    try(ggplot2::theme_set(ggplot2::theme_minimal(base_family = 'AppleGothic')), silent=TRUE)")
                    lines.append("  } else {")
                    lines.append("    try(ggplot2::theme_set(ggplot2::theme_minimal(base_family = 'NanumGothic')), silent=TRUE)")
                    lines.append("  }")
                    lines.append("}")
                    if 'read.csv' not in code.lower() and 'read_csv' not in code.lower():
                        lines.append("# Load data")
                        lines.append(f"df <- read.csv('{data_file_name}')")
                        lines.append("")
            
            # Add the actual code
            if code:
                # Safety check: Remove JSON wrapper if it exists (belt and suspenders)
                code = code.strip()
                if code.startswith('{') and '"code"' in code:
                    try:
                        # Try to parse as JSON and extract code field
                        import json as json_lib
                        json_obj = json_lib.loads(code)
                        if isinstance(json_obj, dict) and 'code' in json_obj:
                            code = json_obj['code']
                            if isinstance(code, list):
                                code = '\n'.join(str(item) for item in code)
                    except:
                        # If JSON parsing fails, try regex extraction
                        code_match = re.search(r'"code"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', code, re.DOTALL)
                        if code_match:
                            code = code_match.group(1)
                            # Unescape JSON strings
                            code = code.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')

                # Clean up code: ensure proper line breaks and comment handling
                code_lines = code.split('\n')
                cleaned_code_lines = []
                for line in code_lines:
                    line = line.strip()
                    if not line:
                        cleaned_code_lines.append("")
                        continue

                    # Fix: if line starts with a number and period (like "1. 데이터 로드"), make it a comment
                    if re.match(r'^\d+\.\s+', line) and not line.startswith('#'):
                        line = f"# {line}"

                    # Fix: split multiple imports on one line
                    # Check for multiple "import" keywords in the line
                    if line.startswith('import ') and line.count('import ') > 1:
                        # Split: "import pandas as pd import matplotlib.pyplot as plt" -> separate lines
                        parts = re.split(r'\s+import\s+', line)
                        for i, part in enumerate(parts):
                            if i == 0:
                                if part.startswith('import '):
                                    cleaned_code_lines.append(part)
                                else:
                                    cleaned_code_lines.append(f"import {part}")
                            else:
                                cleaned_code_lines.append(f"import {part}")
                        continue

                    cleaned_code_lines.append(line)

                cleaned_code = '\n'.join(cleaned_code_lines)
                lines.append(cleaned_code)

                # Quarto Jupyter 엔진에서는 plt.show() 대신 자동 디스플레이 사용
                # plt.show()를 제거하거나 주석 처리 (Quarto가 자동으로 출력)
                if lang == 'python' and ('plt.' in cleaned_code or 'sns.' in cleaned_code or '.plot(' in cleaned_code):
                    # Ensure tight layout for better appearance
                    if 'plt.tight_layout()' not in cleaned_code:
                        lines.append("")
                        lines.append("plt.tight_layout()  # Better spacing")
                
                # For Python: Ensure outputs are displayed
                # Find result variables BEFORE adding to code block
                if lang == 'python':
                    result_vars = []
                    
                    # Pattern: variable_name = ... (where ... is a result operation)
                    patterns = [
                        r'(\w+)\s*=\s*df\.groupby',  # groupby results
                        r'(\w+)\s*=\s*.*\.agg\(',  # aggregation results
                        r'(\w+)\s*=\s*.*anova',  # ANOVA results
                        r'(\w+summary\w*)\s*=',  # summary variables
                        r'(\w+anova\w*)\s*=',  # ANOVA variables
                        r'(\w+plot\w*)\s*=',  # plot variables
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, cleaned_code, re.IGNORECASE)
                        result_vars.extend(matches)
                    
                    # Also check for exact common variable names
                    common_vars = ['summary_cd', 'anova_summary', 'plot_cd', 'tukey_hsd_results']
                    for var in common_vars:
                        if var in cleaned_code:
                            result_vars.append(var)
                    
                    # Remove duplicates
                    result_vars = list(set(result_vars))[:6]
                    
                    # Add display statements - Quarto will show these
                    if result_vars:
                        lines.append("")
                        lines.append("# Display results (Quarto automatically shows the last expression)")
                        for var in result_vars:
                            lines.append(f"try:")
                            lines.append(f"    {var}  # Quarto will display this")
                            lines.append(f"except NameError:")
                            lines.append(f"    pass")
                    else:
                        # Fallback: try common variable names
                        lines.append("")
                        lines.append("# Try to display common result variables")
                        for var in ['summary_cd', 'anova_summary', 'plot_cd']:
                            lines.append(f"try:")
                            lines.append(f"    {var}")
                            lines.append(f"except NameError:")
                            lines.append(f"    pass")
                elif lang == 'r':
                    # R output handling: Ensure dataframes and plots are displayed
                    result_vars = []
                    # Find assignments to common result variables
                    patterns = [
                        r'(\w+)\s*(?:<-|=)\s*.*%\>%\s*summarise',
                        r'(\w+)\s*(?:<-|=)\s*.*group_by',
                        r'(\w+)\s*(?:<-|=)\s*.*aov\(',
                        r'(\w+)\s*(?:<-|=)\s*.*TukeyHSD\(',
                        r'(\w+)\s*(?:<-|=)\s*ggplot\(',
                        r'(\w+_df)\s*(?:<-|=)',
                        r'(\w+_summary)\s*(?:<-|=)',
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, cleaned_code, re.IGNORECASE)
                        result_vars.extend(matches)
                    
                    result_vars = list(set(result_vars))[:5]
                    if result_vars:
                        lines.append("")
                        lines.append("# 결과 출력 (자동 추가됨)")
                        for var in result_vars:
                            lines.append(f"if (exists('{var}')) {{")
                            lines.append(f"  if (is.data.frame({var})) {{")
                            lines.append(f"    print(knitr::kable({var}))")
                            lines.append(f"  }} else {{")
                            lines.append(f"    print({var})")
                            lines.append(f"  }}")
                            lines.append(f"}}")
            
            lines.append("```")
            lines.append("")
            
            # Interpretation - Using cleaner formatting
            if interpretation:
                lines.append("")
                lines.append("::: {.callout-note icon=false}")
                lines.append("### 🧬 분석 통찰 및 결과 해석")
                lines.append("")
                # Clean interpretation text to ensure it doesn't break Callout blocks
                clean_interp = interpretation.strip()
                # Ensure each line is part of the callout (Quarto needs triple colons to wrap content)
                lines.append(clean_interp)
                lines.append(":::")
                lines.append("")
            
            lines.append("---")
            lines.append("")

        # Footer
        lines.append(f"## 결론 및 향후 제언 {{.unnumbered}}")
        lines.append("")
        lines.append("본 리포트는 Google Gemini AI에 의해 자동 생성된 전문 분석 결과입니다.")
        lines.append("모든 통계 수치는 데이터의 품질과 실험 설계에 의존하므로 전문가의 최종 교차 검증을 권장합니다.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Bio-Log Professional v3.0 - The Next Generation Lab Notebook*")

        # Final string assembly
        content = "\n".join(lines)
        
        if output_path is None:
            output_path = self.temp_dir / "report.qmd"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # Use standard utf-8 for broadest compatibility
        output_path.write_text(content, encoding='utf-8')
        
        return output_path
    
    def _decode_output(self, output_bytes: bytes) -> str:
        """한글 윈도우(CP949)와 UTF-8 모두 대응하는 디코딩"""
        for encoding in ['utf-8', 'cp949', 'euc-kr']:
            try:
                return output_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        return output_bytes.decode('utf-8', errors='replace')

    def render_to_html(self, qmd_path: Path) -> Path:
        """Quarto 문서를 HTML로 렌더링"""
        
        # Check if Quarto is installed
        try:
            subprocess.run(['quarto', '--version'], capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError("Quarto가 설치되어 있지 않거나 PATH에 없습니다. https://quarto.org 에서 설치하세요.")
        
        # Enforce UTF-8 for subprocess
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['LANG'] = 'ko_KR.UTF-8'
        env['LC_ALL'] = 'ko_KR.UTF-8'
        
        # Ensure working directory is correct
        work_dir = str(qmd_path.parent)
        
        try:
            # Render without --quiet to get better error messages
            # Code execution is enabled (eval: true), so results will be shown
            result = subprocess.run(
                ['quarto', 'render', str(qmd_path), '--to', 'html'],
                capture_output=True,
                check=True,
                timeout=300,  # Increased timeout for code execution
                cwd=work_dir,
                env=env,
                text=False  # Keep as bytes for proper decoding
            )
            
            html_path = qmd_path.with_suffix('.html')
            
            if not html_path.exists():
                # Try alternative location
                alt_path = Path(work_dir) / html_path.name
                if alt_path.exists():
                    return alt_path
                raise FileNotFoundError(f"렌더링 완료되었으나 파일을 찾을 수 없음: {html_path}")
            
            return html_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("렌더링 시간 초과 (300초)")
        except subprocess.CalledProcessError as e:
            error_msg = f"Quarto 렌더링 실패 (exit code {e.returncode}):\n"
            error_msg += f"📄 파일 경로: {qmd_path}\n"
            error_msg += f"📁 작업 디렉토리: {work_dir}\n"
            error_msg += f"💡 QMD 파일을 확인하여 문제를 진단하세요.\n\n"
            
            stdout_text = self._decode_output(e.stdout) if e.stdout else ""
            stderr_text = self._decode_output(e.stderr) if e.stderr else ""
            
            # Show last 50 lines of stderr (most relevant error info)
            if stderr_text:
                stderr_lines = stderr_text.split('\n')
                if len(stderr_lines) > 50:
                    error_msg += f"--- STDERR (마지막 50줄) ---\n"
                    error_msg += '\n'.join(stderr_lines[-50:]) + "\n"
                else:
                    error_msg += f"--- STDERR ---\n{stderr_text}\n"
            
            if stdout_text:
                stdout_lines = stdout_text.split('\n')
                if len(stdout_lines) > 30:
                    error_msg += f"--- STDOUT (마지막 30줄) ---\n"
                    error_msg += '\n'.join(stdout_lines[-30:]) + "\n"
                else:
                    error_msg += f"--- STDOUT ---\n{stdout_text}\n"
            
            # Add helpful suggestions based on common errors
            error_lower = (stdout_text + stderr_text).lower()
            
            if "jupyter" in error_lower or "python" in error_lower or "kernel" in error_lower:
                error_msg += "\n💡 팁: Python/Jupyter 환경 문제일 수 있습니다.\n"
                error_msg += "   - Python이 설치되어 있는지 확인: python --version\n"
                error_msg += "   - Jupyter가 설치되어 있는지 확인: pip install jupyter ipykernel\n"
                error_msg += "   - 또는 코드 실행을 비활성화하려면 eval: false를 사용하세요.\n"
            
            if "knitr" in error_lower or ("r" in error_lower and "error" in error_lower):
                error_msg += "\n💡 팁: R/knitr 환경 문제일 수 있습니다.\n"
                error_msg += "   - R이 설치되어 있는지 확인: R --version\n"
                error_msg += "   - knitr 패키지 설치: install.packages('knitr')\n"
            
            if "yaml" in error_lower or "parse" in error_lower:
                error_msg += "\n💡 팁: YAML 헤더 형식 오류일 수 있습니다.\n"
                error_msg += f"   - 생성된 파일을 확인하세요: {qmd_path}\n"
            
            if "file" in error_lower and "not found" in error_lower:
                error_msg += "\n💡 팁: 파일 경로 문제일 수 있습니다.\n"
                error_msg += "   - 데이터 파일이 올바른 위치에 있는지 확인하세요.\n"
            
            # Save the generated .qmd file path for debugging
            error_msg += f"\n🔍 디버깅: 생성된 .qmd 파일을 확인하세요: {qmd_path}"
            
            raise RuntimeError(error_msg)
        except FileNotFoundError as e:
            raise RuntimeError(f"파일 오류: {str(e)}")
    
    def render_to_pdf(self, qmd_path: Path) -> Path:
        """Quarto 문서를 PDF로 렌더링"""
        
        # Check if Quarto is installed
        try:
            subprocess.run(['quarto', '--version'], capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError("Quarto가 설치되어 있지 않거나 PATH에 없습니다. https://quarto.org 에서 설치하세요.")
        
        # Enforce UTF-8 for subprocess (same as HTML rendering)
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['LANG'] = 'ko_KR.UTF-8'
        env['LC_ALL'] = 'ko_KR.UTF-8'
        
        work_dir = str(qmd_path.parent)
        
        try:
            result = subprocess.run(
                ['quarto', 'render', str(qmd_path), '--to', 'pdf', '--quiet'],
                capture_output=True,
                check=True,
                timeout=180,  # PDF takes longer
                cwd=work_dir,
                env=env,
                text=False
            )
            
            pdf_path = qmd_path.with_suffix('.pdf')
            
            if not pdf_path.exists():
                # Try alternative location
                alt_path = Path(work_dir) / pdf_path.name
                if alt_path.exists():
                    return alt_path
                raise FileNotFoundError(f"PDF 생성 실패: {pdf_path}")
            
            return pdf_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("PDF 렌더링 시간 초과 (180초)")
        except subprocess.CalledProcessError as e:
            stderr_bytes = e.stderr if e.stderr else b""
            stderr_text = self._decode_output(stderr_bytes)
            
            if b"pdflatex" in stderr_bytes or b"xelatex" in stderr_bytes or "latex" in stderr_text.lower():
                raise RuntimeError(
                    "PDF 생성에 필요한 LaTeX가 설치되어 있지 않습니다.\n"
                    "TinyTeX 설치: quarto install tinytex"
                )
            else:
                error_msg = f"PDF 렌더링 실패 (exit code {e.returncode}):\n"
                stdout_text = self._decode_output(e.stdout) if e.stdout else ""
                
                if stdout_text:
                    error_msg += f"--- STDOUT ---\n{stdout_text}\n"
                if stderr_text:
                    error_msg += f"--- STDERR ---\n{stderr_text}\n"
                raise RuntimeError(error_msg)
