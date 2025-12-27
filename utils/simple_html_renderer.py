# utils/simple_html_renderer.py
"""Quarto 없이 Python만으로 간단한 HTML 리포트 생성"""

from datetime import datetime
from pathlib import Path
import base64
import io

class SimpleHTMLRenderer:
    """Quarto CLI 없이 Python만으로 HTML 생성"""

    @staticmethod
    def create_html_report(
        title: str,
        author: str,
        experiment_date: str,
        code_chunks: list,
        theme: str = "cosmo",
        include_code: bool = True
    ) -> str:
        """
        간단한 HTML 리포트 생성

        Args:
            title: 리포트 제목
            author: 작성자
            experiment_date: 실험 날짜
            code_chunks: 코드 블록 리스트 [{'code': str, 'caption': str, 'interpretation': str}]
            theme: 테마 (현재는 cosmo만 지원)
            include_code: 코드 포함 여부

        Returns:
            HTML 문자열
        """

        # HTML 템플릿
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - DataViz Campus Report</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Highlight.js for code syntax highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">

    <!-- Custom CSS -->
    <style>
        body {{
            font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
            line-height: 1.6;
            padding: 20px;
            background-color: #f8f9fa;
        }}

        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 10px;
        }}

        .report-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}

        .report-header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }}

        .report-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .meta-label {{
            font-weight: 600;
            opacity: 0.9;
        }}

        .analysis-section {{
            margin-bottom: 40px;
            padding: 25px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 8px;
        }}

        .analysis-section h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8rem;
        }}

        .code-block {{
            background: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 15px 0;
        }}

        .code-block pre {{
            margin: 0;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9rem;
        }}

        .interpretation-box {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }}

        .interpretation-box h4 {{
            color: #1976d2;
            margin-top: 0;
        }}

        .warnings-box {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }}

        .warnings-box h4 {{
            color: #f57c00;
            margin-top: 0;
        }}

        .plot-container {{
            margin: 20px 0;
            text-align: center;
        }}

        .plot-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #666;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 12px;
            background: #667eea;
            color: white;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-right: 10px;
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <!-- Report Header -->
        <div class="report-header">
            <h1>📊 {title}</h1>
            <p style="margin-top: 10px; font-size: 1.1rem;">AI 기반 데이터 분석 리포트</p>

            <div class="report-meta">
                <div class="meta-item">
                    <span class="meta-label">👤 작성자:</span>
                    <span>{author}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">📅 분석 일시:</span>
                    <span>{experiment_date}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">🔬 분석 항목:</span>
                    <span>{len(code_chunks)}개</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">🤖 AI 엔진:</span>
                    <span>Google Gemini 2.5 Flash</span>
                </div>
            </div>
        </div>

        <!-- Table of Contents -->
        <div class="toc-box" style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px;">
            <h3>📑 목차</h3>
            <ol>
"""

        # Add TOC items
        for i, chunk in enumerate(code_chunks, 1):
            caption = chunk.get('caption', f'분석 {i}')
            html += f'                <li><a href="#analysis-{i}">{caption}</a></li>\n'

        html += """            </ol>
        </div>

        <!-- Analysis Sections -->
"""

        # Add each analysis section
        for i, chunk in enumerate(code_chunks, 1):
            caption = chunk.get('caption', f'분석 {i}')
            code = chunk.get('code', '')
            interpretation = chunk.get('interpretation', '')
            language = chunk.get('language', 'python')

            html += f"""
        <div class="analysis-section" id="analysis-{i}">
            <h2>{i}. {caption}</h2>
            <span class="badge">Python</span>
            <span class="badge">분석 #{i}</span>
"""

            if include_code and code:
                # Escape HTML in code
                code_escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html += f"""
            <div class="code-block">
                <pre><code class="language-{language}">{code_escaped}</code></pre>
            </div>
"""

            if interpretation:
                html += f"""
            <div class="interpretation-box">
                <h4>💡 분석 결과</h4>
                <p>{interpretation.replace(chr(10), '<br>')}</p>
            </div>
"""

            html += """
        </div>
"""

        # Footer
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html += f"""
        <div class="footer">
            <p><strong>📊 DataViz Campus</strong> - 대학생을 위한 AI 데이터 분석 플랫폼</p>
            <p>v4.0 Student Edition | Powered by Google Gemini 2.5 Flash</p>
            <p style="font-size: 0.9rem; color: #999;">Generated: {current_time}</p>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Highlight.js for code syntax highlighting -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/r.min.js"></script>
    <script>
        // Apply syntax highlighting
        hljs.highlightAll();
    </script>
</body>
</html>
"""

        return html
