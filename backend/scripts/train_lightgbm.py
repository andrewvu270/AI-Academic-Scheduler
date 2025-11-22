"""Train LightGBM model from Supabase survey data.

Usage:
    python backend/scripts/train_lightgbm.py [--limit 5000] [--exclude-synthetic]

The script fetches survey responses from Supabase, engineers features, trains a
LightGBM regressor to predict `actual_hours`, and saves the trained model plus
metadata under `backend/models/`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

# Ensure project root on PYTHONPATH so we can import app modules
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import get_supabase_admin  # noqa: E402

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "lightgbm_survey_model.txt"
FEATURE_COLUMNS_PATH = MODELS_DIR / "lightgbm_feature_columns.json"
FEATURE_IMPORTANCE_PATH = MODELS_DIR / "lightgbm_feature_importance.json"

REQUIRED_COLUMNS = {
    "task_type",
    "grade_percentage",
    "estimated_hours",
    "actual_hours",
    "difficulty_level",
    "priority_rating",
    "due_date",
    "completion_date",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train LightGBM model from Supabase survey data")
    parser.add_argument("--limit", type=int, default=5000, help="Maximum number of survey rows to fetch (default: 5000)")
    parser.add_argument("--exclude-synthetic", action="store_true", help="Exclude AI-generated survey rows")
    return parser.parse_args()


def ensure_environment() -> None:
    env_path = PROJECT_ROOT / ".." / ".env"
    load_dotenv(env_path)

    if not os.environ.get("SUPABASE_URL"):
        raise EnvironmentError("SUPABASE_URL is not set. Check your .env file.")
    if not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        raise EnvironmentError("SUPABASE_SERVICE_ROLE_KEY is not set. Use a key with admin access for training.")


def fetch_survey_rows(limit: int, exclude_synthetic: bool) -> List[Dict[str, Any]]:
    supabase = get_supabase_admin()
    query = (
        supabase
        .table("survey_responses")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
    )

    if exclude_synthetic:
        query = query.eq("is_synthetic", False)

    response = query.execute()
    rows = response.data or []
    if not rows:
        raise RuntimeError("No survey rows returned from Supabase. Collect data first.")

    return rows


def build_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)

    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise RuntimeError(f"Supabase rows are missing required columns: {sorted(missing_cols)}")

    df = df[list(REQUIRED_COLUMNS)].copy()

    # Drop rows without core label/feature values
    df = df.dropna(subset=["estimated_hours", "actual_hours", "task_type"])
    df = df[df["estimated_hours"].astype(float) >= 0]
    df = df[df["actual_hours"].astype(float) >= 0]

    if df.empty:
        raise RuntimeError("All rows were filtered out — ensure estimated and actual hours are populated.")

    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
    df["completion_date"] = pd.to_datetime(df["completion_date"], errors="coerce")

    # Fill missing completion dates with due date (or due date + 0)
    df["completion_date"] = df["completion_date"].fillna(df["due_date"])

    reference_time = datetime.utcnow()
    df["days_until_due"] = (df["due_date"] - reference_time).dt.days.clip(lower=0).fillna(0)
    df["days_between_estimate_and_completion"] = (df["completion_date"] - df["due_date"]).dt.days.fillna(0)

    # One-hot encode task type
    df = pd.get_dummies(df, columns=["task_type"], prefix="task_type")

    return df


def get_feature_columns(df: pd.DataFrame) -> List[str]:
    base_cols = [
        "grade_percentage",
        "estimated_hours",
        "difficulty_level",
        "priority_rating",
        "days_until_due",
        "days_between_estimate_and_completion",
    ]

    task_type_cols = [col for col in df.columns if col.startswith("task_type_")]
    return base_cols + task_type_cols


def train_model(df: pd.DataFrame, feature_cols: List[str]) -> Dict[str, Any]:
    target = "actual_hours"
    X = df[feature_cols]
    y = df[target].astype(float)

    if len(df) < 10:
        raise ValueError(
            "Not enough survey rows to train the model (need at least 10). "
            f"Only {len(df)} row(s) available. Collect more submissions or remove --exclude-synthetic."
        )

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    train_set = lgb.Dataset(X_train, label=y_train)
    val_set = lgb.Dataset(X_val, label=y_val)

    params = {
        "objective": "regression",
        "metric": "rmse",
        "learning_rate": 0.05,
        "num_leaves": 31,
        "feature_fraction": 0.9,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
    }

    # Simple training with minimal parameters for compatibility
    model = lgb.train(
        params,
        train_set,
        num_boost_round=100,  # Reduced number of rounds
    )

    y_pred = model.predict(X_val)
    metrics = {
        "rmse": float(np.sqrt(mean_squared_error(y_val, y_pred))),
        "mae": float(mean_absolute_error(y_val, y_pred)),
        "r2": float(r2_score(y_val, y_pred)),
        "train_samples": int(len(X_train)),
        "val_samples": int(len(X_val)),
    }

    return {"model": model, "metrics": metrics}


def save_artifacts(model: lgb.Booster, feature_cols: List[str]) -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model.save_model(str(MODEL_PATH))

    with FEATURE_COLUMNS_PATH.open("w", encoding="utf-8") as f:
        json.dump(feature_cols, f, indent=2)

    feature_importance = dict(zip(feature_cols, model.feature_importance().tolist()))
    with FEATURE_IMPORTANCE_PATH.open("w", encoding="utf-8") as f:
        json.dump(feature_importance, f, indent=2)


def main() -> None:
    args = parse_args()
    ensure_environment()

    print("Fetching survey data from Supabase...")
    rows = fetch_survey_rows(limit=args.limit, exclude_synthetic=args.exclude_synthetic)
    print(f"Fetched {len(rows)} rows")

    df = build_dataframe(rows)
    feature_cols = get_feature_columns(df)
    print(f"Training with {len(feature_cols)} feature columns: {feature_cols}")

    artifacts = train_model(df, feature_cols)
    save_artifacts(artifacts["model"], feature_cols)

    print("Training metrics:")
    for key, value in artifacts["metrics"].items():
        print(f"  {key}: {value:.4f}")

    print(f"Model saved to {MODEL_PATH}")
    print(f"Feature metadata saved to {FEATURE_COLUMNS_PATH} and {FEATURE_IMPORTANCE_PATH}")


if __name__ == "__main__":
    main()
