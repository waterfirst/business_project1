# agents/validator.py
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, List

class ExperimentValidator:
    """실험 데이터의 품질을 검증하는 클래스"""
    
    def __init__(self):
        self.contamination = 0.1
        
    def validate_standard_curve(self, df: pd.DataFrame, 
                                x_col: str, y_col: str) -> Dict:
        """
        Standard Curve의 선형성 검증
        
        Returns:
            {
                'is_valid': bool,
                'r_squared': float,
                'warnings': List[str]
            }
        """
        from scipy.stats import linregress
        
        slope, intercept, r_value, p_value, std_err = linregress(
            df[x_col], df[y_col]
        )
        
        r_squared = r_value ** 2
        warnings = []
        
        if r_squared < 0.95:
            warnings.append(
                f"⚠️ R² = {r_squared:.3f} (권장: ≥ 0.95). "
                "희석 배수를 확인하세요."
            )
        
        if p_value > 0.05:
            warnings.append(
                f"⚠️ p-value = {p_value:.3f} (유의하지 않음). "
                "측정 오류 가능성 있음."
            )
        
        return {
            'is_valid': len(warnings) == 0,
            'r_squared': r_squared,
            'p_value': p_value,
            'warnings': warnings
        }
    
    def detect_outliers(self, df: pd.DataFrame, 
                       numeric_cols: List[str]) -> pd.DataFrame:
        """Isolation Forest로 이상치 탐지"""
        model = IsolationForest(
            contamination=self.contamination,
            random_state=42
        )
        
        X = df[numeric_cols].values
        predictions = model.fit_predict(X)
        df['is_outlier'] = predictions == -1
        
        return df
    
    def check_replicate_consistency(self, df: pd.DataFrame,
                                   group_col: str,
                                   value_col: str,
                                   cv_threshold: float = 0.15) -> Dict:
        """반복 측정값의 일관성 검증"""
        results = {}
        
        for group in df[group_col].unique():
            group_data = df[df[group_col] == group][value_col]
            
            mean = group_data.mean()
            std = group_data.std()
            cv = (std / mean) * 100 if mean != 0 else np.inf
            
            results[group] = {
                'mean': mean,
                'std': std,
                'cv_percent': cv,
                'is_consistent': cv <= cv_threshold * 100
            }
        
        return results
