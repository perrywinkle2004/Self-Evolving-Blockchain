"""
IntelliChain - Adaptive Consensus Engine (ACE) v2
Dynamically selects the optimal consensus mechanism based on
real-time network metrics and AI predictions.

New in v2:
  - Confidence scoring per decision
  - Evolution history tracking
  - Weighted multi-factor scoring matrix
  - Consensus stability metric

Supported Consensus:
    PoW    - Proof of Work         (high trust, low speed)
    PoS    - Proof of Stake        (high throughput, moderate security)
    PBFT   - Practical BFT         (high security, Byzantine resilience)
    Hybrid - Combination mode      (balanced)
"""

from dataclasses import dataclass, field
from typing import Tuple, List
import numpy as np


@dataclass
class ConsensusResult:
    mechanism: str              # e.g. "PoS", "PBFT", "Hybrid (PoS+PBFT)"
    base_mechanisms: list       # e.g. ["PoS", "PBFT"]
    is_hybrid: bool
    reason: str
    block_time_estimate: float  # seconds
    security_score: float       # 0-1
    throughput_score: float     # 0-1
    confidence: float = 0.85    # ACE decision confidence 0-1
    rule_triggered: str = ""    # Which rule fired


# Static profiles per pure mechanism
_MECHANISM_PROFILES = {
    "PoW":  {"block_time": 10.0, "security": 0.95, "throughput": 0.30, "decentralization": 0.90},
    "PoS":  {"block_time": 3.0,  "security": 0.75, "throughput": 0.85, "decentralization": 0.70},
    "PBFT": {"block_time": 1.5,  "security": 0.90, "throughput": 0.70, "decentralization": 0.50},
}

CONSENSUS_COLORS = {
    "PoW":  "#FFB800",
    "PoS":  "#00FF9C",
    "PBFT": "#00BFFF",
}


def get_mechanism_color(mechanism: str) -> str:
    for key, color in CONSENSUS_COLORS.items():
        if key in mechanism:
            if "Hybrid" in mechanism:
                return "#C87FFF"
            return color
    return "#C87FFF"


def _hybrid_profile(mechanisms: list) -> Tuple[float, float, float]:
    """Blend profiles for a hybrid combination."""
    n   = len(mechanisms)
    bt  = sum(_MECHANISM_PROFILES[m]["block_time"]  for m in mechanisms) / n
    sec = sum(_MECHANISM_PROFILES[m]["security"]    for m in mechanisms) / n
    thr = sum(_MECHANISM_PROFILES[m]["throughput"]  for m in mechanisms) / n
    return round(bt, 2), round(sec, 3), round(thr, 3)


class AdaptiveConsensusEngine:
    """
    Selects or switches consensus mechanism based on:
    - Real-time network snapshot
    - AI-predicted conditions
    - Multi-factor weighted scoring matrix
    """

    def __init__(self):
        self.evolution_history: List[dict] = []
        self._prev_mechanism: str = ""

    def select(self, snapshot: dict, prediction: dict) -> ConsensusResult:
        """Core decision logic - priority rules + confidence scoring."""
        attack_risk   = prediction["attack_risk_prob"]
        traffic_spike = prediction["traffic_spike_prob"]
        congestion    = prediction["congestion_level"]
        threat_lbl    = snapshot["threat_label"]
        nodes         = snapshot["nodes"]
        tx_rate       = snapshot["tx_rate"]
        latency       = snapshot["latency"]

        result = self._apply_rules(
            attack_risk, traffic_spike, congestion,
            threat_lbl, nodes, tx_rate, latency
        )

        self.evolution_history.append({
            "mechanism":   result.mechanism,
            "confidence":  result.confidence,
            "rule":        result.rule_triggered,
            "attack_risk": attack_risk,
            "congestion":  congestion,
        })
        self._prev_mechanism = result.mechanism
        return result

    def _apply_rules(self, attack_risk, traffic_spike, congestion,
                     threat_lbl, nodes, tx_rate, latency) -> "ConsensusResult":

        # Rule 1: Critical attack -> pure PBFT
        if attack_risk >= 0.80 or threat_lbl == "Critical":
            return self._pure("PBFT", confidence=0.97,
                rule="R1: Critical attack — Byzantine Fault Tolerance engaged",
                reason=f"Attack risk at {attack_risk:.0%} ({threat_lbl}) — switching to PBFT for maximum Byzantine resilience")

        # Rule 2: High attack + heavy traffic -> PoS+PBFT hybrid
        if attack_risk >= 0.55 and tx_rate > 180:
            return self._hybrid(["PoS", "PBFT"], confidence=0.91,
                rule="R2: High attack + traffic — PoS+PBFT Hybrid",
                reason=f"Elevated threat ({attack_risk:.0%}) meets high throughput demand ({tx_rate} TX/s) — PoS speed + PBFT security")

        # Rule 3: High threat label but moderate traffic -> PBFT
        if threat_lbl in ("High", "Critical") and attack_risk >= 0.45:
            return self._pure("PBFT", confidence=0.88,
                rule="R3: High threat label — PBFT security mode",
                reason=f"Threat level '{threat_lbl}' with {attack_risk:.0%} attack probability — PBFT selected")

        # Rule 4: Severe congestion + spike -> PoS
        if congestion == "High" and traffic_spike >= 0.60:
            return self._pure("PoS", confidence=0.86,
                rule="R4: Severe congestion + spike — PoS throughput",
                reason=f"High congestion with {traffic_spike:.0%} spike probability — PoS maximizes throughput")

        # Rule 5: High congestion alone -> PoS
        if congestion == "High":
            return self._pure("PoS", confidence=0.80,
                rule="R5: High congestion — PoS",
                reason=f"Network congestion is High ({tx_rate} TX/s) — PoS handles load efficiently")

        # Rule 6: Very sparse network -> PoW
        if nodes < 10:
            return self._pure("PoW", confidence=0.92,
                rule="R6: Sparse network — PoW trust",
                reason=f"Only {nodes} active nodes — PoW provides strongest integrity on sparse networks")

        # Rule 7: High latency + medium threat -> PoW+PoS hybrid
        if latency > 250 and threat_lbl == "Medium":
            return self._hybrid(["PoW", "PoS"], confidence=0.78,
                rule="R7: High latency + medium threat — PoW+PoS",
                reason=f"High latency ({latency:.0f}ms) + medium threat — PoW trust layer + PoS efficiency")

        # Rule 8: Medium threat + medium congestion -> Hybrid
        if threat_lbl == "Medium" and congestion == "Medium":
            return self._hybrid(["PoW", "PoS"], confidence=0.75,
                rule="R8: Mixed conditions — PoW+PoS Hybrid",
                reason="Mixed network conditions — balancing PoW trust with PoS efficiency")

        # Rule 9: Traffic spike alone -> PoS
        if traffic_spike >= 0.65:
            return self._pure("PoS", confidence=0.82,
                rule="R9: Traffic spike predicted — PoS",
                reason=f"Traffic spike probability {traffic_spike:.0%} — PoS pre-emptively selected for throughput")

        # Rule 10: Stable low-threat -> PoS optimal default
        if congestion in ("Low", "Medium") and attack_risk < 0.30:
            return self._pure("PoS", confidence=0.89,
                rule="R10: Stable conditions — PoS optimal",
                reason=f"Stable network (threat: {attack_risk:.0%}, congestion: {congestion}) — PoS is optimal")

        # Fallback: Hybrid PoW+PoS
        return self._hybrid(["PoW", "PoS"], confidence=0.65,
            rule="FALLBACK: Uncertain state — Hybrid",
            reason="Uncertain network state — conservative hybrid mode engaged")

    def _pure(self, mechanism: str, confidence: float,
              rule: str, reason: str) -> ConsensusResult:
        p = _MECHANISM_PROFILES[mechanism]
        return ConsensusResult(
            mechanism=mechanism,
            base_mechanisms=[mechanism],
            is_hybrid=False,
            reason=reason,
            block_time_estimate=p["block_time"],
            security_score=p["security"],
            throughput_score=p["throughput"],
            confidence=confidence,
            rule_triggered=rule,
        )

    def _hybrid(self, mechanisms: list, confidence: float,
                rule: str, reason: str) -> ConsensusResult:
        label = " + ".join(mechanisms)
        bt, sec, thr = _hybrid_profile(mechanisms)
        return ConsensusResult(
            mechanism=f"Hybrid ({label})",
            base_mechanisms=mechanisms,
            is_hybrid=True,
            reason=reason,
            block_time_estimate=bt,
            security_score=sec,
            throughput_score=thr,
            confidence=confidence,
            rule_triggered=rule,
        )

    def stability_score(self) -> float:
        """Fraction of consecutive blocks with same consensus (stability)."""
        if len(self.evolution_history) < 2:
            return 1.0
        same = sum(
            1 for i in range(1, len(self.evolution_history))
            if self.evolution_history[i]["mechanism"] == self.evolution_history[i-1]["mechanism"]
        )
        return round(same / (len(self.evolution_history) - 1), 3)

    def avg_confidence(self) -> float:
        if not self.evolution_history:
            return 0.0
        return round(float(np.mean([e["confidence"] for e in self.evolution_history])), 3)

    def get_scoring_matrix(self, snapshot: dict, prediction: dict) -> dict:
        """
        Compute a multi-factor weighted score for each pure consensus.
        Returns dict[mechanism -> score_dict].
        """
        attack  = prediction["attack_risk_prob"]
        cong    = {"Low": 0.2, "Medium": 0.5, "High": 0.9}.get(prediction["congestion_level"], 0.5)
        latency = snapshot["latency"]
        nodes   = snapshot["nodes"]

        results = {}
        for mech, p in _MECHANISM_PROFILES.items():
            sec_w    = 0.25 + attack * 0.35
            thr_w    = 0.30 - attack * 0.10
            lat_pen  = max(0.0, 1.0 - latency / 400.0)
            node_fit = min(1.0, nodes / 30.0) if mech != "PoW" else min(1.0, 10.0 / max(nodes, 1))
            score = (
                sec_w * p["security"] +
                thr_w * p["throughput"] +
                0.20  * lat_pen +
                0.15  * p["decentralization"] +
                0.10  * node_fit
            )
            results[mech] = {
                "score":            round(min(score, 1.0), 3),
                "security":         p["security"],
                "throughput":       p["throughput"],
                "decentralization": p["decentralization"],
                "block_time":       p["block_time"],
            }
        return results
