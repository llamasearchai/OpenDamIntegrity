"""Machine Learning models for predicting failure risk using sensor trends.
Uses scikit-learn MLP by default; XGBoost if available via extras.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

try:
    from xgboost import XGBClassifier  # type: ignore

    XGB_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    XGB_AVAILABLE = False


def _build_features(sensor_series: dict[str, np.ndarray]) -> np.ndarray:
    # Simple features: last value, mean, std, slope
    feats = []
    for _name, arr in sensor_series.items():
        arr = np.asarray(arr, dtype=float)
        if arr.size == 0:
            feats.extend([0, 0, 0, 0])
            continue
        x = np.arange(arr.size)
        slope = float(np.polyfit(x, arr, 1)[0]) if arr.size > 1 else 0.0
        feats.extend(
            [
                float(arr[-1]),
                float(arr.mean()),
                float(arr.std(ddof=1) if arr.size > 1 else 0.0),
                slope,
            ]
        )
    return np.asarray(feats, dtype=float)


def train_risk_model(
    sensor_series_list: dict[str, np.ndarray], labels: np.ndarray, model_dir: str | Path = "models"
) -> tuple[Path, str]:
    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    X = np.vstack([_build_features(s) for s in sensor_series_list])
    y = np.asarray(labels, dtype=int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    if XGB_AVAILABLE:
        model = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1, subsample=0.8)
    else:
        model = MLPClassifier(
            hidden_layer_sizes=(32, 16), activation="relu", max_iter=300, random_state=42
        )

    model.fit(X_train, y_train)
    report = classification_report(y_test, model.predict(X_test))

    # Save using numpy's savez since we avoid extra deps; store weights via pickle
    import pickle

    model_path = model_dir / "risk_model.pkl"
    with model_path.open("wb") as f:
        pickle.dump(model, f)

    return model_path, report


def predict_risk(sensor_series: dict[str, np.ndarray], model_path: str | Path) -> int:
    import pickle

    with Path(model_path).open("rb") as f:
        model = pickle.load(f)
    X = _build_features(sensor_series).reshape(1, -1)
    pred = model.predict(X)
    return int(pred[0])
