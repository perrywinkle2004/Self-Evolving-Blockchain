"""
IntelliChain - Blockchain Core
Block and Blockchain classes with SHA-256 hashing,
consensus tracking, and chain integrity verification.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from utils.hashing import compute_block_hash, genesis_hash, verify_hash
from utils.helpers import format_timestamp, simulate_transactions


@dataclass
class Block:
    """Represents a single block in the IntelliChain blockchain."""
    block_id: int
    previous_hash: str
    timestamp: str
    transactions: list
    consensus: str
    hash: str = field(default="", init=False)
    block_time: float = 0.0      # seconds taken to mine/validate
    latency: float = 0.0         # network latency at creation time
    tx_count: int = field(init=False)

    def __post_init__(self):
        self.tx_count = len(self.transactions)
        self.hash = compute_block_hash(
            self.block_id,
            self.previous_hash,
            self.timestamp,
            self.transactions,
            self.consensus,
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    def is_valid(self) -> bool:
        return verify_hash(self.to_dict())


class Blockchain:
    """Maintains the full chain of blocks and provides integrity checking."""

    def __init__(self):
        self.chain: list[Block] = []
        self._create_genesis()

    def _create_genesis(self):
        """Create the immutable genesis block."""
        genesis = Block(
            block_id=0,
            previous_hash=genesis_hash(),
            timestamp=format_timestamp(),
            transactions=["GENESIS"],
            consensus="N/A",
            block_time=0.0,
            latency=0.0,
        )
        self.chain.append(genesis)

    @property
    def latest_block(self) -> Block:
        return self.chain[-1]

    @property
    def length(self) -> int:
        return len(self.chain)

    def add_block(self, block: Block) -> bool:
        """Append a validated block to the chain."""
        if block.previous_hash != self.latest_block.hash:
            return False  # Chain integrity violation
        self.chain.append(block)
        return True

    def is_chain_valid(self) -> bool:
        """Verify integrity of the entire chain."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if not current.is_valid():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def get_blocks_as_dicts(self) -> list[dict]:
        """Return all blocks serialized as dictionaries."""
        return [b.to_dict() for b in self.chain]

    def get_consensus_history(self) -> list[str]:
        """Return list of consensus used per block (excluding genesis)."""
        return [b.consensus for b in self.chain[1:]]

    def get_performance_series(self) -> dict:
        """Return time-series performance data for analytics."""
        blocks = self.chain[1:]  # Skip genesis
        return {
            "block_ids": [b.block_id for b in blocks],
            "block_times": [b.block_time for b in blocks],
            "latencies": [b.latency for b in blocks],
            "tx_counts": [b.tx_count for b in blocks],
        }
