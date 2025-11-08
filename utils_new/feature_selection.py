import pandas as pd
from typing import List

def select_features_for_model(df: pd.DataFrame, candidate_features: List[str], model_feature_names: list=None) -> list:
    if model_feature_names:
        inter = [f for f in model_feature_names if f in df.columns]
        if len(inter) > 0:
            return inter
    return [f for f in candidate_features if f in df.columns]