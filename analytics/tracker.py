"""
IntelliChain - Analytics Tracker
Stores block metadata, performance metrics, consensus switching events,
and threat detection logs for the analytics dashboard.
"""

import json
import os
from datetime import datetime
from collections import Counter
from utils.helpers import format_timestamp

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "blockchain_data.json")


class AnalyticsTracker:
    """Persists and queries analytics metadata about the blockchain session."""

    def __init__(self):
        self.records: list[dict] = []
        self.switching_events: list[dict] = []
        self.threat_events: list[dict] = []
        self._last_consensus: str = ""

    def record_block(self, block_dict: dict, snapshot: dict,
                     prediction: dict, efficiency: float,
                     consensus_result=None):
        """Store metadata for a newly created block."""
        record = {
            "block_id": block_dict["block_id"],
            "consensus": block_dict["consensus"],
            "timestamp": block_dict["timestamp"],
            "tx_count": block_dict["tx_count"],
            "block_time": block_dict["block_time"],
            "latency": block_dict["latency"],
            "nodes": snapshot["nodes"],
            "tx_rate": snapshot["tx_rate"],
            "threat": snapshot["threat"],
            "attack_risk": prediction["attack_risk_prob"],
            "traffic_spike": prediction["traffic_spike_prob"],
            "congestion": prediction["congestion_level"],
            "efficiency": round(efficiency, 4),
            "confidence": getattr(consensus_result, "confidence", 0.8) if consensus_result else 0.8,
            "rule_triggered": getattr(consensus_result, "rule_triggered", "") if consensus_result else "",
        }
        self.records.append(record)

        # Track consensus switches
        current = block_dict["consensus"]
        if self._last_consensus and current != self._last_consensus:
            self.switching_events.append({
                "block_id": block_dict["block_id"],
                "from": self._last_consensus,
                "to": current,
                "timestamp": block_dict["timestamp"],
            })
        self._last_consensus = current

        # Track threat events
        if snapshot["threat_label"] in ("High", "Critical"):
            self.threat_events.append({
                "block_id": block_dict["block_id"],
                "threat_level": snapshot["threat_label"],
                "threat_score": snapshot["threat"],
                "attack_risk": prediction["attack_risk_prob"],
                "consensus_chosen": current,
                "timestamp": block_dict["timestamp"],
            })

    def consensus_distribution(self) -> dict:
        """Return count of each consensus used."""
        counts = Counter(r["consensus"] for r in self.records)
        return dict(counts)

    def performance_series(self) -> dict:
        """Return time-series performance data."""
        if not self.records:
            return {}
        return {
            "block_ids": [r["block_id"] for r in self.records],
            "latencies": [r["latency"] for r in self.records],
            "tx_rates": [r["tx_rate"] for r in self.records],
            "block_times": [r["block_time"] for r in self.records],
            "efficiencies": [r["efficiency"] for r in self.records],
            "threats": [r["threat"] for r in self.records],
        }

    def compute_efficiency(self, consensus_result, snapshot: dict) -> float:
        """
        Compute a consensus efficiency score (0–1) based on:
        - Throughput score
        - Security score
        - Latency penalty
        - Attack risk
        """
        latency = snapshot["latency"]
        threat = snapshot["threat"]

        throughput = consensus_result.throughput_score
        security = consensus_result.security_score

        # Penalize for high latency (normalized, 500ms = max penalty)
        latency_score = max(0.0, 1.0 - (latency / 500.0))

        # Reward security when threat is high
        threat_weight = 0.3 + threat * 0.2
        perf_weight = 1.0 - threat_weight

        efficiency = (
            perf_weight * (0.5 * throughput + 0.3 * latency_score) +
            threat_weight * security
        )
        return round(min(1.0, max(0.0, efficiency)), 4)

    def save_to_disk(self):
        """Persist analytics data to JSON file."""
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        payload = {
            "records": self.records,
            "switching_events": self.switching_events,
            "threat_events": self.threat_events,
            "saved_at": format_timestamp(),
        }
        with open(DATA_PATH, "w") as f:
            json.dump(payload, f, indent=2)

    def load_from_disk(self) -> bool:
        """Load existing analytics from disk if available."""
        if not os.path.exists(DATA_PATH):
            return False
        try:
            with open(DATA_PATH, "r") as f:
                data = json.load(f)
            self.records = data.get("records", [])
            self.switching_events = data.get("switching_events", [])
            self.threat_events = data.get("threat_events", [])
            if self.records:
                self._last_consensus = self.records[-1]["consensus"]
            return True
        except Exception:
            return False
