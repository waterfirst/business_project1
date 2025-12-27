# utils/code_executor.py
"""Python 코드를 실행하고 결과(출력, 그래프)를 캡처"""

import io
import sys
import base64
import traceback
from pathlib import Path
import matplotlib.pyplot as plt
import plotly.graph_objects as go


class CodeExecutor:
    """Python 코드 실행 및 결과 캡처"""

    def __init__(self, temp_dir=None):
        self.temp_dir = Path(temp_dir) if temp_dir else Path.cwd()
        self.temp_dir.mkdir(exist_ok=True, parents=True)

    def execute_python_code(self, code: str, data_path: str = None) -> dict:
        """
        Python 코드를 실행하고 결과를 캡처

        Args:
            code: 실행할 Python 코드
            data_path: 데이터 파일 경로 (선택사항)

        Returns:
            {
                'success': bool,
                'stdout': str,  # print() 출력
                'stderr': str,  # 에러 메시지
                'figures': list,  # 저장된 그래프 파일 경로들
                'figure_data': list,  # base64 인코딩된 그래프 데이터
                'error': str  # 실행 실패 시 에러 메시지
            }
        """
        result = {
            'success': False,
            'stdout': '',
            'stderr': '',
            'figures': [],
            'figure_data': [],
            'error': ''
        }

        # stdout, stderr 캡처 준비
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            # 실행 환경 준비
            exec_globals = {
                '__builtins__': __builtins__,
                'plt': plt,
                'go': go,
            }

            # 데이터 파일이 있으면 경로 설정
            if data_path:
                import pandas as pd
                exec_globals['pd'] = pd
                # data.csv로 접근할 수 있도록 심볼릭 링크 또는 변수 설정
                exec_globals['DATA_PATH'] = data_path

                # 코드에 data.csv 경로 자동 치환
                code = code.replace("'data.csv'", f"'{data_path}'")
                code = code.replace('"data.csv"', f'"{data_path}"')

            # 코드 실행
            exec(code, exec_globals)

            # stdout, stderr 캡처
            result['stdout'] = sys.stdout.getvalue()
            result['stderr'] = sys.stderr.getvalue()

            # Matplotlib 그래프 캡처
            if plt.get_fignums():  # 활성화된 figure가 있는지 확인
                for i, fig_num in enumerate(plt.get_fignums()):
                    fig = plt.figure(fig_num)

                    # 파일로 저장
                    fig_path = self.temp_dir / f"figure_{i+1}.png"
                    fig.savefig(fig_path, dpi=300, bbox_inches='tight')
                    result['figures'].append(str(fig_path))

                    # base64 인코딩 (HTML 삽입용)
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                    buf.seek(0)
                    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                    result['figure_data'].append(img_base64)
                    buf.close()

                plt.close('all')  # 모든 figure 닫기

            # Plotly 그래프 캡처 (exec_globals에서 찾기)
            plotly_figs = []
            for name, obj in exec_globals.items():
                if isinstance(obj, (go.Figure, go.FigureWidget)):
                    plotly_figs.append(obj)

            for i, fig in enumerate(plotly_figs, start=len(result['figures']) + 1):
                # HTML로 저장
                fig_path = self.temp_dir / f"plotly_figure_{i}.html"
                fig.write_html(str(fig_path))
                result['figures'].append(str(fig_path))

                # 또는 이미지로 변환 (kaleido 필요)
                try:
                    img_bytes = fig.to_image(format="png", width=1200, height=800)
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    result['figure_data'].append(img_base64)
                except:
                    # kaleido 없으면 HTML을 base64로
                    html_str = fig.to_html(include_plotlyjs='cdn')
                    result['figure_data'].append(html_str)

            result['success'] = True

        except Exception as e:
            result['success'] = False
            result['error'] = traceback.format_exc()
            result['stderr'] += f"\nExecution Error: {str(e)}\n{traceback.format_exc()}"

        finally:
            # stdout, stderr 복원
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return result

    def execute_and_save_results(self, code: str, output_path: str, data_path: str = None) -> dict:
        """
        코드를 실행하고 결과를 JSON 파일로 저장

        Args:
            code: 실행할 코드
            output_path: 결과를 저장할 JSON 파일 경로
            data_path: 데이터 파일 경로

        Returns:
            실행 결과 dict
        """
        import json

        result = self.execute_python_code(code, data_path)

        # 결과를 JSON으로 저장
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result
