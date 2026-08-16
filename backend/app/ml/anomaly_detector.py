from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    """
    Detect anomalous service activity using Isolation Forest.

    The model can be trained on a baseline dataset, saved to disk,
    and later loaded to detect anomalies in newly uploaded logs.
    """

    MODEL_PATH = Path(
        "backend/models/anomaly_detector.joblib"
    )

    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        self.is_trained = False

    def prepare_features(self, feature_windows):
        """
        Convert LogFeatures objects into a numerical matrix
        for the Isolation Forest model.
        """

        X = []

        for feature in feature_windows:
            X.append([
                feature.total_events,
                feature.error_count,
                feature.warning_count,
                feature.info_count,
                feature.debug_count,
                feature.critical_count,
                feature.error_rate,
                feature.avg_response_time_ms,
                feature.max_response_time_ms,
                feature.min_response_time_ms,
                feature.timeout_count,
                feature.server_error_count
            ])

        return np.array(
            X,
            dtype=float
        )

    def train(self, feature_windows):
        """
        Train Isolation Forest using feature windows.
        """

        X = self.prepare_features(feature_windows)

        if len(X) == 0:
            return False

        self.model.fit(X)

        self.is_trained = True

        return True

    def save_model(self, model_path=None):
        """
        Save the trained Isolation Forest model to disk.
        """

        if not self.is_trained:
            raise ValueError(
                "Cannot save an untrained model."
            )

        if model_path is None:
            model_path = self.MODEL_PATH

        model_path = Path(model_path)

        # Create backend/models if it does not exist
        model_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(
            self.model,
            model_path
        )

        return model_path

    def load_model(self, model_path=None):
        """
        Load a previously trained Isolation Forest model
        from disk.
        """

        if model_path is None:
            model_path = self.MODEL_PATH

        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Trained model not found: "
                f"{model_path.resolve()}"
            )

        self.model = joblib.load(
            model_path
        )

        self.is_trained = True

        return True

    def predict(self, feature_windows):
        """
        Predict anomalies.

        Isolation Forest predictions:
            1  = Normal
           -1  = Anomaly
        """

        if not self.is_trained:
            raise ValueError(
                "Model has not been trained or loaded yet."
            )

        X = self.prepare_features(feature_windows)

        if len(X) == 0:
            return []

        predictions = self.model.predict(X)

        scores = self.model.decision_function(X)

        results = []

        for feature, prediction, score in zip(
            feature_windows,
            predictions,
            scores
        ):
            results.append(
                {
                    "window_start": feature.window_start,
                    "window_end": feature.window_end,
                    "service": feature.service,
                    "total_events": feature.total_events,
                    "is_anomaly": bool(
                        prediction == -1
                    ),
                    "anomaly_score": float(score)
                }
            )

        return results