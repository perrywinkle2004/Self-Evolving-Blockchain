"""
IntelliChain - Network Monitoring Engine
Tracks real-time simulated network conditions including node count,
transaction throughput, latency, and threat signals.
"""

import random
import numpy as np
from utils.helpers import clamp, threat_label


class NetworkMonitor:
    """Simulates and tracks network state metrics in real time."""

    def __init__(self, base_nodes: int = 25, base_tx_rate: int = 150,
                 attack_mode: bool = False):
        self.base_nodes = base_nodes
        self.base_tx_rate = base_tx_rate
        self.attack_mode = attack_mode
        self.history: list[dict] = []

    def _simulate_latency(self, nodes: int, tx_rate: int) -> float:
        """Compute simulated network latency in milliseconds."""
        # More nodes and higher tx rate increase latency
        base_latency = 50 + (nodes * 1.5) + (tx_rate * 0.3)
        noise = random.gauss(0, 10)
        return clamp(base_latency + noise, 20.0, 500.0)

    def _simulate_threat(self) -> float:
        """Return a threat probability signal between 0 and 1."""
        if self.attack_mode:
            return clamp(random.uniform(0.55, 0.95), 0.0, 1.0)
        return clamp(random.uniform(0.0, 0.35), 0.0, 1.0)

    def _simulate_node_count(self) -> int:
        """Return current simulated node count with variance."""
        if self.attack_mode:
            # Simulate sudden node spike (Sybil-like attack)
            spike = random.randint(10, 40)
            return self.base_nodes + spike
        noise = random.randint(-3, 3)
        return max(5, self.base_nodes + noise)

    def _simulate_tx_rate(self) -> int:
        """Return current simulated transaction rate."""
        noise = random.gauss(0, self.base_tx_rate * 0.1)
        if self.attack_mode:
            # Abnormal transaction burst
            noise += self.base_tx_rate * 0.5
        return max(1, int(self.base_tx_rate + noise))

    def sample(self) -> dict:
        """Take a full network snapshot and store it in history."""
        nodes = self._simulate_node_count()
        tx_rate = self._simulate_tx_rate()
        latency = self._simulate_latency(nodes, tx_rate)
        threat = self._simulate_threat()

        snapshot = {
            "nodes": nodes,
            "tx_rate": tx_rate,
            "latency": round(latency, 2),
            "threat": round(threat, 4),
            "threat_label": threat_label(threat),
        }
        self.history.append(snapshot)
        return snapshot

    def get_recent(self, n: int = 10) -> list[dict]:
        """Return the last n network snapshots."""
        return self.history[-n:]

    def get_averages(self) -> dict:
        """Compute average metrics across all history."""
        if not self.history:
            return {"nodes": 0, "tx_rate": 0, "latency": 0, "threat": 0}
        keys = ["nodes", "tx_rate", "latency", "threat"]
        return {k: round(np.mean([s[k] for s in self.history]), 3) for k in keys}
