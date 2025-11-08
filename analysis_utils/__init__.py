"""Analysis utilities for the Summary tab.

This subpackage wraps and exposes functions copied from the
user‑provided PD‑monotonic‑constraints repository.  The goal is to
provide a self‑contained set of helpers for cleaning raw financial
data, engineering predictive features, selecting a subset of those
features for model inference, loading the LightGBM model and
associated thresholds, and visualising default risk statistics.

The public API re‑exports the most frequently used functions so
that the Summary tab can call them without needing to import from
individual modules directly.  For example::

    from analysis_utils import (clean_and_log_transform,
                                preprocess_and_create_features,
                                select_features_for_model,
                                load_lgbm_model,
                                model_feature_names,
                                predict_pd,
                                load_thresholds,
                                thresholds_for_sector,
                                classify_pd,
                                default_distribution_by_year,
                                default_distribution_by_sector)

All functions behave identically to their counterparts in the
original project, but have been namespaced under ``analysis_utils``
to avoid clashes with the main ``utils`` package.
"""

from .data_cleaning import clean_and_log_transform  # noqa: F401
from .feature_engineering import preprocess_and_create_features, default_financial_feature_list  # noqa: F401
from .feature_selection import select_features_for_model  # noqa: F401
from .model_scoring import (load_lgbm_model, model_feature_names,
                             predict_pd, explain_shap, run_stress_test, align_features_to_model)  # noqa: F401
from .policy import load_thresholds, thresholds_for_sector, classify_pd  # noqa: F401
from .visualization import (default_distribution_by_year,
                            default_distribution_by_sector)  # noqa: F401