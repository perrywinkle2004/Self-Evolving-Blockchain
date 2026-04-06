"""
IntelliChain - Hashing Utilities
SHA-256 based hashing for block creation and verification.
"""

import hashlib
import json
from datetime import datetime


def compute_hash(data: dict) -> str:
    """Compute SHA-256 hash of a dictionary."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


def compute_block_hash(block_id: int, previous_hash: str, timestamp: str,
                       transactions: list, consensus: str) -> str:
    """Compute hash for a block using its core fields."""
    block_data = {
        "block_id": block_id,
        "previous_hash": previous_hash,
        "timestamp": timestamp,
        "transactions": transactions,
        "consensus": consensus,
    }
    return compute_hash(block_data)


def genesis_hash() -> str:
    """Return genesis block hash."""
    return "0" * 64


def verify_hash(block: dict) -> bool:
    """Verify that a block's stored hash matches computed hash."""
    stored_hash = block.get("hash", "")
    computed = compute_block_hash(
        block["block_id"],
        block["previous_hash"],
        block["timestamp"],
        block["transactions"],
        block["consensus"],
    )
    return stored_hash == computed
