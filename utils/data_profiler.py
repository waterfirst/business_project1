import pandas as pd
import numpy as np
from typing import Dict, Any

def get_data_profile(df: pd.DataFrame) -> str:
    """
    Pandas DataFrame의 상세 정보를 텍스트 요약으로 변환합니다.
    """
    if df is None:
        return "데이터가 없습니다."

    summary = []
    summary.append(f"### [데이터 기본 정보]")
    summary.append(f"- 크기: {df.shape[0]} 행 x {df.shape[1]} 열")
    summary.append(f"- 컬럼 목록: {', '.join(df.columns.tolist())}")
    
    summary.append(f"\n### [컬럼별 상세 정보]")
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100
        
        col_info = f"- **{col}**: 타입={dtype}, 결측치={null_count}({null_pct:.1f}%)"
        
        if pd.api.types.is_numeric_dtype(df[col]):
            mean = df[col].mean()
            std = df[col].std()
            min_val = df[col].min()
            max_val = df[col].max()
            col_info += f", 통계=[평균:{mean:.2f}, 표준편차:{std:.2f}, 범위:{min_val}~{max_val}]"
        else:
            unique_count = df[col].nunique()
            top_values = df[col].value_counts().head(3).index.tolist()
            col_info += f", 고유값 수={unique_count}, 상위 항목={top_values}"
            
        summary.append(col_info)

    summary.append(f"\n### [데이터 샘플 (상위 5행)]")
    summary.append(df.head(5).to_markdown())

    return "\n".join(summary)
