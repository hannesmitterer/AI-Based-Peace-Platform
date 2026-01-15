"""
Blockchain Fork Detection and Consensus Validation
Scenario B: Defense against blockchain fork manipulation and sabotage
"""
import hashlib
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Block:
    """Represents a blockchain block."""
    index: int
    timestamp: float
    data: str
    previous_hash: str
    hash: str
    nonce: int = 0


class BlockchainForkDetector:
    """
    Detects and validates blockchain forks through simultaneous
    consensus checking and header continuity verification.
    """
    
    def __init__(self, difficulty: int = 4):
        """
        Initialize blockchain fork detector.
        
        Args:
            difficulty: Mining difficulty (number of leading zeros)
        """
        self.difficulty = difficulty
        self.chain: List[Block] = []
        self.forks: List[List[Block]] = []
        self.consensus_nodes: List[str] = []
        self._create_genesis_block()
        
    def _create_genesis_block(self):
        """Create the genesis (first) block."""
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            data="Genesis Block",
            previous_hash="0",
            hash="",
            nonce=0
        )
        genesis_block.hash = self._calculate_hash(genesis_block)
        self.chain.append(genesis_block)
    
    def _calculate_hash(self, block: Block) -> str:
        """
        Calculate SHA-256 hash of block.
        
        Args:
            block: Block to hash
            
        Returns:
            Hex hash string
        """
        block_string = f"{block.index}{block.timestamp}{block.data}{block.previous_hash}{block.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _mine_block(self, block: Block) -> Block:
        """
        Mine block by finding valid nonce.
        
        Args:
            block: Block to mine
            
        Returns:
            Mined block with valid nonce
        """
        target = "0" * self.difficulty
        
        while True:
            block.hash = self._calculate_hash(block)
            if block.hash[:self.difficulty] == target:
                return block
            block.nonce += 1
    
    def add_block(self, data: str) -> Block:
        """
        Add new block to the chain.
        
        Args:
            data: Block data
            
        Returns:
            New block
        """
        previous_block = self.chain[-1]
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=previous_block.hash,
            hash="",
            nonce=0
        )
        
        new_block = self._mine_block(new_block)
        self.chain.append(new_block)
        return new_block
    
    def validate_chain(self, chain: List[Block]) -> bool:
        """
        Validate entire blockchain.
        
        Args:
            chain: Chain to validate
            
        Returns:
            True if valid
        """
        if len(chain) == 0:
            return False
        
        # Check genesis block
        if chain[0].previous_hash != "0":
            return False
        
        # Validate each block
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]
            
            # Check hash continuity
            if current.previous_hash != previous.hash:
                return False
            
            # Verify hash calculation
            if current.hash != self._calculate_hash(current):
                return False
            
            # Check mining difficulty
            if not current.hash.startswith("0" * self.difficulty):
                return False
            
            # Check index continuity
            if current.index != previous.index + 1:
                return False
        
        return True
    
    def detect_fork(self, alternative_chain: List[Block]) -> Tuple[bool, Dict]:
        """
        Detect if alternative chain represents a fork.
        
        Args:
            alternative_chain: Alternative blockchain
            
        Returns:
            Tuple of (is_fork, fork_details)
        """
        # Find common ancestor
        common_ancestor_index = -1
        for i in range(min(len(self.chain), len(alternative_chain))):
            if self.chain[i].hash == alternative_chain[i].hash:
                common_ancestor_index = i
            else:
                break
        
        is_fork = common_ancestor_index < len(self.chain) - 1
        
        fork_details = {
            'detected': is_fork,
            'common_ancestor_index': common_ancestor_index,
            'main_chain_length': len(self.chain),
            'alternative_chain_length': len(alternative_chain),
            'fork_point': common_ancestor_index + 1 if is_fork else None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if is_fork:
            self.forks.append(alternative_chain)
        
        return is_fork, fork_details
    
    def consensus_validation(self, chains: List[List[Block]]) -> List[Block]:
        """
        Perform consensus validation across multiple chains.
        Uses longest valid chain rule.
        
        Args:
            chains: List of blockchain candidates
            
        Returns:
            Canonical chain selected by consensus
        """
        valid_chains = []
        
        # Validate all chains
        for chain in chains:
            if self.validate_chain(chain):
                valid_chains.append(chain)
        
        if not valid_chains:
            raise ValueError("No valid chains found")
        
        # Select longest valid chain
        canonical_chain = max(valid_chains, key=len)
        
        # Check if current chain needs to be replaced
        if len(canonical_chain) > len(self.chain) and canonical_chain != self.chain:
            print(f"⚠ Fork detected: Switching to longer chain (length {len(canonical_chain)})")
            self.chain = canonical_chain
        
        return canonical_chain
    
    def check_header_continuity(self) -> Tuple[bool, List[int]]:
        """
        Check header continuity across the chain.
        
        Returns:
            Tuple of (is_continuous, list of discontinuity indices)
        """
        discontinuities = []
        
        for i in range(1, len(self.chain)):
            if self.chain[i].previous_hash != self.chain[i-1].hash:
                discontinuities.append(i)
        
        is_continuous = len(discontinuities) == 0
        return is_continuous, discontinuities
    
    def get_fork_statistics(self) -> Dict:
        """Get fork detection statistics."""
        is_continuous, discontinuities = self.check_header_continuity()
        
        return {
            'chain_length': len(self.chain),
            'forks_detected': len(self.forks),
            'header_continuous': is_continuous,
            'discontinuity_count': len(discontinuities),
            'chain_valid': self.validate_chain(self.chain),
            'difficulty': self.difficulty
        }


class ConsensusValidator:
    """
    Validates consensus across multiple blockchain nodes.
    """
    
    def __init__(self, minimum_confirmations: int = 3):
        """
        Initialize consensus validator.
        
        Args:
            minimum_confirmations: Minimum nodes required for consensus
        """
        self.minimum_confirmations = minimum_confirmations
        self.node_responses = {}
        
    def register_node_response(self, 
                               node_id: str,
                               block_hash: str,
                               chain_length: int):
        """
        Register a node's blockchain state.
        
        Args:
            node_id: Node identifier
            block_hash: Latest block hash
            chain_length: Chain length
        """
        self.node_responses[node_id] = {
            'block_hash': block_hash,
            'chain_length': chain_length,
            'timestamp': time.time()
        }
    
    def check_consensus(self) -> Tuple[bool, Dict]:
        """
        Check if consensus exists among nodes.
        
        Returns:
            Tuple of (has_consensus, consensus_details)
        """
        if len(self.node_responses) < self.minimum_confirmations:
            return False, {
                'consensus': False,
                'reason': 'Insufficient nodes',
                'node_count': len(self.node_responses),
                'required': self.minimum_confirmations
            }
        
        # Count hash occurrences
        hash_counts = {}
        for node_id, response in self.node_responses.items():
            block_hash = response['block_hash']
            if block_hash not in hash_counts:
                hash_counts[block_hash] = []
            hash_counts[block_hash].append(node_id)
        
        # Find majority hash
        majority_hash = max(hash_counts.items(), key=lambda x: len(x[1]))
        majority_count = len(majority_hash[1])
        
        has_consensus = majority_count >= self.minimum_confirmations
        
        consensus_details = {
            'consensus': has_consensus,
            'majority_hash': majority_hash[0],
            'confirming_nodes': majority_hash[1],
            'confirmation_count': majority_count,
            'required_confirmations': self.minimum_confirmations,
            'total_nodes': len(self.node_responses)
        }
        
        return has_consensus, consensus_details


if __name__ == "__main__":
    # Demonstration
    print("=== Blockchain Fork Detection Demo ===")
    
    # Create blockchain
    detector = BlockchainForkDetector(difficulty=3)
    
    print("\nAdding blocks to main chain...")
    for i in range(5):
        block = detector.add_block(f"Transaction {i+1}")
        print(f"  Block {block.index}: {block.hash[:16]}...")
    
    # Validate chain
    is_valid = detector.validate_chain(detector.chain)
    print(f"\nMain chain valid: {is_valid}")
    
    # Check header continuity
    is_continuous, discontinuities = detector.check_header_continuity()
    print(f"Header continuity: {is_continuous}")
    
    # Simulate a fork
    print("\nSimulating fork attack...")
    forked_chain = detector.chain[:3]  # Take first 3 blocks
    
    # Add different block to create fork
    fork_block = Block(
        index=3,
        timestamp=time.time(),
        data="Malicious Transaction",
        previous_hash=forked_chain[-1].hash,
        hash="",
        nonce=0
    )
    fork_block = detector._mine_block(fork_block)
    forked_chain.append(fork_block)
    
    # Detect fork
    is_fork, fork_details = detector.detect_fork(forked_chain)
    print(f"Fork detected: {is_fork}")
    print(f"Fork point: Block {fork_details['fork_point']}")
    
    # Test consensus validation
    print("\n=== Consensus Validation Demo ===")
    validator = ConsensusValidator(minimum_confirmations=3)
    
    # Simulate node responses
    validator.register_node_response("node1", detector.chain[-1].hash, len(detector.chain))
    validator.register_node_response("node2", detector.chain[-1].hash, len(detector.chain))
    validator.register_node_response("node3", detector.chain[-1].hash, len(detector.chain))
    validator.register_node_response("node4", "different_hash", 5)
    
    has_consensus, details = validator.check_consensus()
    print(f"Consensus reached: {has_consensus}")
    print(f"Confirming nodes: {details['confirmation_count']}/{details['total_nodes']}")
    
    # Print statistics
    stats = detector.get_fork_statistics()
    print(f"\n=== Statistics ===")
    print(f"Chain length: {stats['chain_length']}")
    print(f"Forks detected: {stats['forks_detected']}")
    print(f"Chain valid: {stats['chain_valid']}")
    
    print("\n✓ Blockchain fork detection initialized")
