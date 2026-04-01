"""
IntelliChain - Helper Utilities
Common helper functions used across modules.
"""

import random
import numpy as np
from datetime import datetime


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def normalize(value: float, min_val: float, max_val: float) -> float:
    """Normalize value to [0, 1] range."""
    if max_val == min_val:
        return 0.0
    return clamp((value - min_val) / (max_val - min_val), 0.0, 1.0)


def simulate_transactions(rate: int, noise_factor: float = 0.15) -> list:
    """Generate a list of simulated transaction IDs."""
    count = max(1, int(rate + random.gauss(0, rate * noise_factor)))
    return [f"TX-{random.randint(100000, 999999)}" for _ in range(count)]


def format_timestamp(dt: datetime = None) -> str:
    """Return ISO-formatted timestamp string."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def threat_label(level: float) -> str:
    """Convert threat probability to human-readable label."""
    if level < 0.3:
        return "Low"
    elif level < 0.6:
        return "Medium"
    elif level < 0.8:
        return "High"
    else:
        return "Critical"


def congestion_label(level: float) -> str:
    """Convert congestion score to human-readable label."""
    if level < 0.33:
        return "Low"
    elif level < 0.66:
        return "Medium"
    else:
        return "High"


def efficiency_color(score: float) -> str:
    """Return hex color based on efficiency score."""
    if score >= 0.8:
        return "#00FF9C"
    elif score >= 0.6:
        return "#AAFFCC"
    elif score >= 0.4:
        return "#FFCC00"
    else:
        return "#FF4444"
