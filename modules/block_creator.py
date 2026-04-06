"""
IntelliChain - Block Creation Engine
Creates new blocks based on the selected consensus mechanism,
simulating realistic block times and transaction packaging.
"""

import random
import time
from modules.blockchain import Block, Blockchain
from modules.consensus_engine import ConsensusResult
from utils.helpers import simulate_transactions, format_timestamp


# Simulated block time multipliers per consensus
_BLOCK_TIME_VARIANCE = {
    "PoW": (0.8, 1.4),
    "PoS": (0.9, 1.1),
    "PBFT": (0.85, 1.15),
    "Hybrid": (0.88, 1.2),
}


def _get_variance(consensus: str) -> tuple:
    for key in _BLOCK_TIME_VARIANCE:
        if key in consensus:
            return _BLOCK_TIME_VARIANCE[key]
    return (0.9, 1.1)


class BlockCreator:
    """Handles block assembly and addition to the blockchain."""

    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain

    def create_block(self, consensus_result: ConsensusResult,
                     tx_rate: int, latency: float) -> Block:
        """
        Create and add a new block to the blockchain.

        Args:
            consensus_result: Output from AdaptiveConsensusEngine
            tx_rate: Current transaction rate
            latency: Current network latency (ms)

        Returns:
            The newly created Block
        """
        prev = self.blockchain.latest_block
        block_id = self.blockchain.length  # next index

        # Simulate block time based on consensus
        lo, hi = _get_variance(consensus_result.mechanism)
        block_time = round(consensus_result.block_time_estimate * random.uniform(lo, hi), 3)

        # Package transactions for this block
        transactions = simulate_transactions(tx_rate)

        block = Block(
            block_id=block_id,
            previous_hash=prev.hash,
            timestamp=format_timestamp(),
            transactions=transactions,
            consensus=consensus_result.mechanism,
            block_time=block_time,
            latency=round(latency, 2),
        )

        success = self.blockchain.add_block(block)
        if not success:
            raise RuntimeError(f"Failed to add block {block_id} — chain integrity error")

        return block
