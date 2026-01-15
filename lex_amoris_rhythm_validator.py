"""
Lex Amoris Rhythm Validator
Dynamic Blacklist and Rhythm Validation Module

This module implements behavioral security control through frequency/vibration validation.
Packets are validated based on their rhythmic signature, independent of IP origin.
"""

import hashlib
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class RhythmSignature:
    """Represents a rhythmic signature for validation"""
    frequency: float  # Hz - expected frequency
    amplitude: float  # Normalized amplitude (0-1)
    phase: float  # Phase offset in radians
    timestamp: datetime
    
    def is_valid(self) -> bool:
        """Check if signature is within valid parameters"""
        return (0.1 <= self.frequency <= 1000.0 and 
                0.0 <= self.amplitude <= 1.0 and
                0.0 <= self.phase <= 6.28318)  # 2*pi


class RhythmValidator:
    """
    Validates data packets based on rhythmic frequency vibration.
    Implements dynamic blacklist independent of IP origin.
    """
    
    def __init__(self, 
                 base_frequency: float = 432.0,  # Hz - Lex Amoris harmony frequency
                 tolerance: float = 0.05,  # 5% tolerance
                 blacklist_duration: int = 3600):  # 1 hour in seconds
        self.base_frequency = base_frequency
        self.tolerance = tolerance
        self.blacklist_duration = blacklist_duration
        self.dynamic_blacklist: Dict[str, datetime] = {}
        self.validation_history: List[Dict[str, Any]] = []
        
    def calculate_packet_rhythm(self, packet_data: Dict[str, Any]) -> RhythmSignature:
        """
        Calculate rhythmic signature from packet data.
        Uses hash-based frequency derivation for deterministic validation.
        """
        # Serialize packet data
        packet_json = json.dumps(packet_data, sort_keys=True)
        packet_hash = hashlib.sha256(packet_json.encode()).hexdigest()
        
        # Derive rhythm parameters from hash
        # Use different parts of hash for different parameters
        frequency_seed = int(packet_hash[:16], 16)
        amplitude_seed = int(packet_hash[16:32], 16)
        phase_seed = int(packet_hash[32:48], 16)
        
        # Normalize to valid ranges
        frequency = self.base_frequency * (1 + (frequency_seed % 1000) / 10000.0)
        amplitude = (amplitude_seed % 1000) / 1000.0
        phase = (phase_seed % 628) / 100.0  # 0 to 2*pi
        
        return RhythmSignature(
            frequency=frequency,
            amplitude=amplitude,
            phase=phase,
            timestamp=datetime.utcnow()
        )
    
    def vibrates_correctly(self, signature: RhythmSignature) -> bool:
        """
        Check if signature vibrates at the correct frequency.
        Returns True if within tolerance of base frequency.
        """
        if not signature.is_valid():
            return False
            
        freq_min = self.base_frequency * (1 - self.tolerance)
        freq_max = self.base_frequency * (1 + self.tolerance)
        
        return freq_min <= signature.frequency <= freq_max
    
    def get_packet_id(self, packet_data: Dict[str, Any]) -> str:
        """Generate unique identifier for packet"""
        packet_json = json.dumps(packet_data, sort_keys=True)
        return hashlib.sha256(packet_json.encode()).hexdigest()[:16]
    
    def is_blacklisted(self, packet_id: str) -> bool:
        """Check if packet ID is currently blacklisted"""
        if packet_id in self.dynamic_blacklist:
            blacklist_time = self.dynamic_blacklist[packet_id]
            if datetime.utcnow() - blacklist_time < timedelta(seconds=self.blacklist_duration):
                return True
            else:
                # Remove expired blacklist entry
                del self.dynamic_blacklist[packet_id]
        return False
    
    def add_to_blacklist(self, packet_id: str):
        """Add packet ID to dynamic blacklist"""
        self.dynamic_blacklist[packet_id] = datetime.utcnow()
    
    def validate_packet(self, packet_data: Dict[str, Any], 
                       origin_ip: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate packet based on rhythm, independent of IP origin.
        
        Args:
            packet_data: The data packet to validate
            origin_ip: IP origin (logged but not used for validation)
            
        Returns:
            Dict with validation result and details
        """
        packet_id = self.get_packet_id(packet_data)
        
        # Check blacklist first
        if self.is_blacklisted(packet_id):
            result = {
                "valid": False,
                "reason": "blacklisted",
                "packet_id": packet_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "origin_ip": origin_ip
            }
            self.validation_history.append(result)
            return result
        
        # Calculate and check rhythm
        signature = self.calculate_packet_rhythm(packet_data)
        vibrates_ok = self.vibrates_correctly(signature)
        
        if not vibrates_ok:
            # Add to blacklist if rhythm is incorrect
            self.add_to_blacklist(packet_id)
            result = {
                "valid": False,
                "reason": "incorrect_rhythm",
                "packet_id": packet_id,
                "signature": {
                    "frequency": signature.frequency,
                    "amplitude": signature.amplitude,
                    "phase": signature.phase,
                    "expected_frequency": self.base_frequency,
                    "tolerance": self.tolerance
                },
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "origin_ip": origin_ip
            }
        else:
            result = {
                "valid": True,
                "reason": "rhythm_validated",
                "packet_id": packet_id,
                "signature": {
                    "frequency": signature.frequency,
                    "amplitude": signature.amplitude,
                    "phase": signature.phase
                },
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "origin_ip": origin_ip
            }
        
        self.validation_history.append(result)
        return result
    
    def get_blacklist_status(self) -> Dict[str, Any]:
        """Get current blacklist statistics"""
        active_blacklist = {
            pid: time for pid, time in self.dynamic_blacklist.items()
            if datetime.utcnow() - time < timedelta(seconds=self.blacklist_duration)
        }
        
        return {
            "total_blacklisted": len(active_blacklist),
            "blacklist_duration_seconds": self.blacklist_duration,
            "base_frequency_hz": self.base_frequency,
            "tolerance": self.tolerance,
            "blacklisted_packets": list(active_blacklist.keys()),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def clear_blacklist(self):
        """Clear all blacklist entries (admin operation)"""
        cleared_count = len(self.dynamic_blacklist)
        self.dynamic_blacklist.clear()
        return {
            "cleared": cleared_count,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
