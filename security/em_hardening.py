"""
Electromagnetic Signature Hardening
Scenario A: Defense against SDR scans and electromagnetic eavesdropping
"""
import secrets
import time
import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FrequencyChannel:
    """Represents a communication frequency channel."""
    frequency: float  # MHz
    bandwidth: float  # MHz
    last_used: float
    usage_count: int = 0


class AdaptiveFrequencyHopping:
    """
    Implements adaptive frequency switching protocols to harden
    electromagnetic signatures against SDR-based attacks.
    """
    
    def __init__(self, 
                 base_frequency: float = 2400.0,
                 num_channels: int = 79,
                 hop_interval: float = 0.625):
        """
        Initialize frequency hopping system.
        
        Args:
            base_frequency: Base frequency in MHz
            num_channels: Number of frequency channels
            hop_interval: Time between hops in seconds
        """
        self.base_frequency = base_frequency
        self.num_channels = num_channels
        self.hop_interval = hop_interval
        self.channels = self._initialize_channels()
        self.current_channel_index = 0
        self.hop_sequence = []
        self.last_hop_time = time.time()
        
    def _initialize_channels(self) -> List[FrequencyChannel]:
        """Initialize frequency channels."""
        channels = []
        for i in range(self.num_channels):
            freq = self.base_frequency + (i * 1.0)  # 1 MHz spacing
            channel = FrequencyChannel(
                frequency=freq,
                bandwidth=1.0,
                last_used=0.0
            )
            channels.append(channel)
        return channels
    
    def generate_hop_sequence(self, seed: Optional[bytes] = None) -> List[int]:
        """
        Generate pseudo-random frequency hopping sequence.
        
        Args:
            seed: Optional seed for sequence generation
            
        Returns:
            List of channel indices
        """
        if seed is None:
            seed = secrets.token_bytes(32)
        
        # Use cryptographic hash for sequence generation
        sequence = []
        hash_input = seed
        
        for _ in range(100):  # Generate 100 hops
            hash_output = hashlib.sha256(hash_input).digest()
            channel_index = int.from_bytes(hash_output[:4], 'big') % self.num_channels
            sequence.append(channel_index)
            hash_input = hash_output
        
        self.hop_sequence = sequence
        return sequence
    
    def get_next_frequency(self) -> FrequencyChannel:
        """
        Get next frequency in the hopping sequence.
        
        Returns:
            Next frequency channel
        """
        current_time = time.time()
        
        # Check if it's time to hop
        if current_time - self.last_hop_time >= self.hop_interval:
            if not self.hop_sequence:
                self.generate_hop_sequence()
            
            self.current_channel_index = (self.current_channel_index + 1) % len(self.hop_sequence)
            self.last_hop_time = current_time
        
        # Get current channel
        channel_idx = self.hop_sequence[self.current_channel_index]
        channel = self.channels[channel_idx]
        
        # Update usage statistics
        channel.last_used = current_time
        channel.usage_count += 1
        
        return channel
    
    def detect_jamming(self, signal_strength: float, noise_floor: float) -> bool:
        """
        Detect potential jamming or interference.
        
        Args:
            signal_strength: Current signal strength in dBm
            noise_floor: Background noise level in dBm
            
        Returns:
            True if jamming is detected
        """
        # If noise floor is significantly elevated, jamming is likely
        threshold = -80  # dBm
        return noise_floor > threshold
    
    def get_status(self) -> Dict:
        """Get current hopping status."""
        current_channel = self.channels[self.hop_sequence[self.current_channel_index]] if self.hop_sequence else None
        
        return {
            'current_frequency': current_channel.frequency if current_channel else None,
            'current_channel_index': self.current_channel_index,
            'total_channels': self.num_channels,
            'hop_interval': self.hop_interval,
            'last_hop_time': self.last_hop_time,
            'sequence_length': len(self.hop_sequence)
        }


class FaradayProtection:
    """
    Faraday-based electromagnetic shielding simulation.
    Provides metrics for electromagnetic isolation effectiveness.
    """
    
    def __init__(self, shielding_effectiveness: float = 100.0):
        """
        Initialize Faraday protection.
        
        Args:
            shielding_effectiveness: Shielding effectiveness in dB
        """
        self.shielding_effectiveness = shielding_effectiveness
        self.monitoring_enabled = True
        self.detected_leaks = []
        
    def calculate_attenuation(self, frequency: float) -> float:
        """
        Calculate signal attenuation at given frequency.
        
        Args:
            frequency: Frequency in MHz
            
        Returns:
            Attenuation in dB
        """
        # Higher frequencies generally have better shielding
        base_attenuation = self.shielding_effectiveness
        frequency_factor = 1.0 + (frequency / 10000.0)
        return base_attenuation * frequency_factor
    
    def detect_em_leak(self, measured_signal: float, threshold: float = -90.0) -> bool:
        """
        Detect electromagnetic leakage.
        
        Args:
            measured_signal: Measured signal strength outside shield in dBm
            threshold: Detection threshold in dBm
            
        Returns:
            True if leak detected
        """
        if measured_signal > threshold:
            leak_info = {
                'timestamp': datetime.utcnow().isoformat(),
                'signal_strength': measured_signal,
                'threshold': threshold,
                'severity': 'high' if measured_signal > -70 else 'medium'
            }
            self.detected_leaks.append(leak_info)
            return True
        return False
    
    def get_protection_status(self) -> Dict:
        """Get protection status."""
        return {
            'shielding_effectiveness': self.shielding_effectiveness,
            'monitoring_enabled': self.monitoring_enabled,
            'detected_leaks': len(self.detected_leaks),
            'status': 'protected' if len(self.detected_leaks) == 0 else 'compromised'
        }


if __name__ == "__main__":
    # Demonstration
    print("=== Adaptive Frequency Hopping Demo ===")
    hopping = AdaptiveFrequencyHopping()
    
    print(f"Initializing with {hopping.num_channels} channels")
    hopping.generate_hop_sequence()
    
    print("\nFirst 10 frequency hops:")
    for i in range(10):
        channel = hopping.get_next_frequency()
        print(f"  Hop {i+1}: {channel.frequency:.2f} MHz")
    
    print("\n=== Faraday Protection Demo ===")
    faraday = FaradayProtection(shielding_effectiveness=100.0)
    
    test_freq = 2450.0  # MHz
    attenuation = faraday.calculate_attenuation(test_freq)
    print(f"Attenuation at {test_freq} MHz: {attenuation:.2f} dB")
    
    # Test leak detection
    leak_detected = faraday.detect_em_leak(-85.0)
    print(f"EM leak detected: {leak_detected}")
    
    status = faraday.get_protection_status()
    print(f"Protection status: {status['status']}")
    
    print("\n✓ Electromagnetic hardening initialized")
