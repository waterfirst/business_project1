# utils/quarto_renderer.py
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List
import textwrap

class QuartoRenderer:
    """Quarto 문서 생성 및 렌더링"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def create_qmd_document(
        self, 
        title: str,
        author: str,
        experiment_date: str,
        code_chunks: List[dict],
        theme: str = "cosmo",
        code_fold: bool = True,
        output_path: Optional[str] = None
    ) -> Path:
        """Quarto 문서 생성 (v3.0 - 들여쓰기 완벽 제거 버전)"""
        
        # Determine processing engine based on language
        is_r = any(chunk.get('language', '').lower() == 'r' for chunk in code_chunks)
        engine_section = "engine: knitr" if is_r else "jupyter: python3"
        
        # Professional CSS for the report
        custom_css = textwrap.dedent("""
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono&display=swap');

            body {
              font-family: 'Inter', system-ui, -apple-system, sans-serif;
              line-height: 1.6;
              color: #2c3e50;
            }

            .quarto-title-block .quarto-title-banner {
              background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
              padding: 4rem 0;
              color: white;
              margin-bottom: 2rem;
              border-radius: 0 0 20px 20px;
            }

            .abstract-box {
              background: #f8f9fa;
              padding: 2rem;
              border-radius: 15px;
              border-left: 8px solid #3498db;
              margin-bottom: 3rem;
              box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            }

            h2 {
              color: #1a2a6c;
              border-bottom: 3px solid #fdbb2d;
              padding-bottom: 0.5rem;
              margin-top: 3rem;
              font-weight: 600;
            }

            .callout {
              border-radius: 15px !important;
              border: none !important;
              box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            }
        """).strip()
        
        # Write CSS to a file
        css_path = self.temp_dir / "custom_style.css"
        css_path.write_text(custom_css, encoding='utf-8-sig')

        # Assemble document line by line to guarantee zero indentation
        lines = []
        
        # YAML Header
        lines.append("---")
        lines.append(f'title: "{title}"')
        lines.append('subtitle: "AI-Powered Bio-Data Analysis Executive Report"')
        lines.append(f'author: "{author}"')
        lines.append(f'date: "{experiment_date}"')
        lines.append("lang: ko")
        lines.append(engine_section)
        lines.append("format:")
        lines.append("  html:")
        lines.append("    theme: flatly")
        lines.append("    css: custom_style.css")
        lines.append("    title-block-banner: true")
        lines.append("    code-fold: true")
        lines.append('    code-summary: "분석 소스 코드 보기"')
        lines.append("    toc: true")
        lines.append("    toc-location: left")
        lines.append("    number-sections: true")
        lines.append("    embed-resources: true")
        lines.append("    html-math-method: katex")
        lines.append("execute:")
        lines.append("  warning: false")
        lines.append("  message: false")
        lines.append("  echo: true")
        lines.append("---")
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
            lang = chunk.get('language', 'python')
            code = chunk.get('code', '')
            caption = chunk.get('caption', f'Analysis {i}')
            interpretation = chunk.get('interpretation', '')
            
            lines.append(f"## 분석 {i}: {caption}")
            lines.append("")
            
            # Code Block
            lines.append(f"```{{{lang}}}")
            lines.append(f"#| label: fig-analysis-{i}")
            lines.append(f'#| fig-cap: "{caption}"')
            lines.append("")
            lines.append(code)
            lines.append("```")
            lines.append("")
            
            # Interpretation
            if interpretation:
                lines.append('::: {.callout-note appearance="simple"}')
                lines.append("### 💡 결과 해석 및 임상적 의미")
                lines.append("")
                lines.append(interpretation)
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
        output_path.write_text(content, encoding='utf-8-sig')
        
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
        
        try:
            result = subprocess.run(
                ['quarto', 'render', str(qmd_path), '--to', 'html'],
                capture_output=True,
                check=True,
                timeout=60,
                cwd=str(qmd_path.parent)
            )
            
            html_path = qmd_path.with_suffix('.html')
            
            if not html_path.exists():
                raise FileNotFoundError(f"렌더링 완료되었으나 파일을 찾을 수 없음: {html_path}")
            
            return html_path
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("렌더링 시간 초과 (60초)")
        except subprocess.CalledProcessError as e:
            error_msg = f"Quarto 렌더링 실패 (exit code {e.returncode}):\n"
            stdout_text = self._decode_output(e.stdout) if e.stdout else ""
            stderr_text = self._decode_output(e.stderr) if e.stderr else ""
            
            if stdout_text:
                error_msg += f"--- STDOUT ---\n{stdout_text}\n"
            if stderr_text:
                error_msg += f"--- STDERR ---\n{stderr_text}\n"
            raise RuntimeError(error_msg)
        except FileNotFoundError:
            raise RuntimeError("Quarto가 설치되어 있지 않습니다. https://quarto.org 에서 설치하세요.")
    
    def render_to_pdf(self, qmd_path: Path) -> Path:
        """Quarto 문서를 PDF로 렌더링"""
        
        try:
            result = subprocess.run(
                ['quarto', 'render', str(qmd_path), '--to', 'pdf'],
                capture_output=True,
                check=True,
                timeout=120,
                cwd=str(qmd_path.parent)
            )
            
            pdf_path = qmd_path.with_suffix('.pdf')
            
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF 생성 실패: {pdf_path}")
            
            return pdf_path
            
        except subprocess.CalledProcessError as e:
            if e.stderr and (b"pdflatex" in e.stderr or b"xelatex" in e.stderr):
                raise RuntimeError(
                    "PDF 생성에 필요한 LaTeX가 설치되어 있지 않습니다.\n"
                    "TinyTeX 설치: quarto install tinytex"
                )
            else:
                error_msg = f"PDF 렌더링 실패 (exit code {e.returncode}):\n"
                stdout_text = self._decode_output(e.stdout) if e.stdout else ""
                stderr_text = self._decode_output(e.stderr) if e.stderr else ""
                
                if stdout_text:
                    error_msg += f"--- STDOUT ---\n{stdout_text}\n"
                if stderr_text:
                    error_msg += f"--- STDERR ---\n{stderr_text}\n"
                raise RuntimeError(error_msg)
