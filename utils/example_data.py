# utils/example_data.py
"""대학생용 예제 데이터셋 및 분석 템플릿"""

import pandas as pd
import numpy as np

class ExampleDatasets:
    """교육용 예제 데이터셋"""

    @staticmethod
    def create_student_grades():
        """성적 데이터 (ANOVA, T-test 연습용)"""
        np.random.seed(42)
        n_students = 120

        data = {
            '학생ID': range(1, n_students + 1),
            '전공': np.random.choice(['생명과학', '화학', '물리학', '수학'], n_students),
            '학년': np.random.choice([1, 2, 3, 4], n_students),
            '중간고사': np.random.normal(75, 12, n_students).round(1),
            '기말고사': np.random.normal(78, 15, n_students).round(1),
            '출석률': np.random.uniform(60, 100, n_students).round(1),
            '과제점수': np.random.normal(85, 10, n_students).round(1),
        }

        df = pd.DataFrame(data)
        # 전체 점수 계산 (가중평균)
        df['총점'] = (df['중간고사'] * 0.3 + df['기말고사'] * 0.4 +
                      df['출석률'] * 0.1 + df['과제점수'] * 0.2').round(1)

        return df

    @staticmethod
    def create_experiment_measurements():
        """실험 측정 데이터 (회귀분석, 상관분석 연습용)"""
        np.random.seed(100)
        n_samples = 80

        # 농도와 흡광도 (선형 관계)
        concentration = np.linspace(0, 10, n_samples)
        absorbance = 0.15 * concentration + np.random.normal(0, 0.1, n_samples)

        data = {
            '샘플번호': range(1, n_samples + 1),
            '농도_uM': concentration.round(2),
            '흡광도': absorbance.round(4),
            '온도_C': np.random.normal(25, 2, n_samples).round(1),
            'pH': np.random.normal(7.0, 0.5, n_samples).round(2),
            '실험자': np.random.choice(['A조', 'B조', 'C조', 'D조'], n_samples),
        }

        return pd.DataFrame(data)

    @staticmethod
    def create_survey_data():
        """설문조사 데이터 (카이제곱 검정, 기술통계 연습용)"""
        np.random.seed(77)
        n_responses = 200

        data = {
            '응답자ID': range(1, n_responses + 1),
            '성별': np.random.choice(['남성', '여성'], n_responses),
            '연령대': np.random.choice(['10대', '20대', '30대', '40대 이상'],
                                      n_responses, p=[0.1, 0.5, 0.3, 0.1]),
            '만족도': np.random.choice(['매우 불만', '불만', '보통', '만족', '매우 만족'],
                                     n_responses, p=[0.05, 0.15, 0.3, 0.35, 0.15]),
            '사용시간_분': np.random.gamma(2, 15, n_responses).round(0).astype(int),
            '재구매의향': np.random.choice(['예', '아니오'], n_responses, p=[0.7, 0.3]),
        }

        return pd.DataFrame(data)

    @staticmethod
    def get_dataset_info():
        """예제 데이터셋 설명"""
        return {
            'student_grades': {
                'name': '학생 성적 데이터',
                'description': '4개 전공 120명의 성적 데이터',
                'use_cases': [
                    '전공별 성적 차이 분석 (ANOVA)',
                    '중간고사와 기말고사 상관관계',
                    '출석률과 성적의 관계',
                    '학년별 성적 분포'
                ],
                'rows': 120,
                'columns': 8
            },
            'experiment_measurements': {
                'name': '실험 측정 데이터',
                'description': '농도-흡광도 실험 데이터',
                'use_cases': [
                    'Standard Curve 작성',
                    '선형 회귀 분석',
                    '실험 조별 차이 분석',
                    '온도/pH 영향 분석'
                ],
                'rows': 80,
                'columns': 6
            },
            'survey_data': {
                'name': '설문조사 데이터',
                'description': '제품 만족도 설문 200건',
                'use_cases': [
                    '성별/연령대별 만족도 차이',
                    '카이제곱 검정 (범주형 변수)',
                    '사용시간 분포 분석',
                    '재구매의향 영향 요인'
                ],
                'rows': 200,
                'columns': 6
            }
        }


class AnalysisTemplates:
    """자주 사용하는 분석 템플릿"""

    @staticmethod
    def get_templates():
        return {
            'descriptive': {
                'name': '기술통계 분석',
                'prompt': '각 숫자형 변수의 평균, 중앙값, 표준편차를 계산하고 히스토그램으로 분포를 시각화해주세요',
                'tags': ['기초', '통계', '분포']
            },
            'comparison': {
                'name': '그룹 간 비교',
                'prompt': '그룹별로 변수를 비교하고, 통계적으로 유의한 차이가 있는지 T-test 또는 ANOVA로 검정해주세요',
                'tags': ['비교', '가설검정', 'T-test', 'ANOVA']
            },
            'correlation': {
                'name': '상관관계 분석',
                'prompt': '모든 숫자형 변수 간 상관관계를 계산하고 히트맵으로 시각화한 후, 높은 상관관계를 보이는 변수 쌍을 scatter plot으로 보여주세요',
                'tags': ['상관분석', '히트맵', '산점도']
            },
            'regression': {
                'name': '회귀 분석',
                'prompt': 'X변수로 Y변수를 예측하는 선형 회귀 모델을 만들고, R-squared와 회귀식을 보여주세요. 잔차 플롯도 그려주세요',
                'tags': ['회귀분석', '예측', 'R-squared']
            },
            'distribution': {
                'name': '분포 분석',
                'prompt': '주요 변수들의 분포를 히스토그램, 박스플롯, Q-Q plot으로 확인하고 정규분포를 따르는지 검정해주세요',
                'tags': ['분포', '정규성검정', 'Q-Q plot']
            },
            'interactive_viz': {
                'name': '인터랙티브 시각화',
                'prompt': 'Plotly를 사용해서 인터랙티브한 scatter plot과 box plot을 만들어주세요. 마우스로 줌하고 데이터를 탐색할 수 있게 해주세요',
                'tags': ['Plotly', '인터랙티브', '탐색적분석']
            }
        }
