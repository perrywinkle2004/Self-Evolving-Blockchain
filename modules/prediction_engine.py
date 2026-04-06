"""
IntelliChain - AI Prediction Engine
Uses a lightweight ML model (Decision Tree / Logistic Regression)
to predict near-future network conditions based on historical data.
"""

import numpy as np
import random
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from utils.helpers import clamp, congestion_label


# ---------------------------------------------------------------------------
# Pre-built synthetic training data
# Each row: [nodes, tx_rate, latency, threat] → congestion_level label
# ---------------------------------------------------------------------------
TRAIN_X = np.array([
    [10,  50,  60,  0.05],
    [15,  80,  80,  0.10],
    [20,  120, 100, 0.20],
    [25,  150, 120, 0.25],
    [30,  180, 150, 0.30],
    [35,  220, 180, 0.40],
    [40,  260, 200, 0.50],
    [50,  300, 240, 0.60],
    [60,  350, 280, 0.70],
    [70,  400, 320, 0.80],
    [80,  450, 370, 0.85],
    [90,  500, 410, 0.90],
    [12,  60,  70,  0.08],
    [18,  90,  90,  0.15],
    [22,  110, 105, 0.22],
    [28,  160, 130, 0.28],
    [45,  270, 210, 0.55],
    [55,  330, 260, 0.65],
    [65,  380, 300, 0.75],
    [75,  420, 340, 0.82],
])

TRAIN_Y_LABELS = [
    "Low", "Low", "Low", "Low", "Medium",
    "Medium", "Medium", "High", "High", "High",
    "High", "High", "Low", "Low", "Low",
    "Medium", "Medium", "High", "High", "High",
]


class PredictionEngine:
    """Lightweight ML-based predictor for network congestion and attack risk."""

    def __init__(self):
        self._le = LabelEncoder()
        self._model = DecisionTreeClassifier(max_depth=5, random_state=42)
        self._train()

    def _train(self):
        """Fit the model on synthetic training data."""
        y_encoded = self._le.fit_transform(TRAIN_Y_LABELS)
        self._model.fit(TRAIN_X, y_encoded)

    def _traffic_spike_probability(self, tx_rate: float, history: list) -> float:
        """Estimate probability of a traffic spike."""
        if len(history) < 3:
            return round(random.uniform(0.1, 0.4), 3)
        recent_rates = [h["tx_rate"] for h in history[-5:]]
        avg = np.mean(recent_rates)
        std = np.std(recent_rates) + 1e-6
        z_score = (tx_rate - avg) / std
        prob = clamp(0.5 + z_score * 0.15, 0.0, 1.0)
        return round(prob, 3)

    def _attack_probability(self, threat: float, nodes: int, history: list) -> float:
        """Combine current threat level and anomaly detection."""
        base = threat
        if len(history) >= 3:
            recent_nodes = [h["nodes"] for h in history[-5:]]
            avg_nodes = np.mean(recent_nodes)
            if nodes > avg_nodes * 1.4:
                base = clamp(base + 0.2, 0.0, 1.0)  # Sybil spike
        noise = random.gauss(0, 0.03)
        return round(clamp(base + noise, 0.0, 1.0), 3)

    def predict(self, snapshot: dict, history: list) -> dict:
        """
        Predict traffic spike, attack risk, and congestion level
        from current snapshot and recent history.
        """
        nodes = snapshot["nodes"]
        tx_rate = snapshot["tx_rate"]
        latency = snapshot["latency"]
        threat = snapshot["threat"]

        # ML-based congestion prediction
        X = np.array([[nodes, tx_rate, latency, threat]])
        encoded = self._model.predict(X)[0]
        congestion = self._le.inverse_transform([encoded])[0]

        # Probabilistic predictions
        traffic_spike = self._traffic_spike_probability(tx_rate, history)
        attack_risk = self._attack_probability(threat, nodes, history)

        return {
            "traffic_spike_prob": traffic_spike,
            "attack_risk_prob": attack_risk,
            "congestion_level": congestion,
        }
