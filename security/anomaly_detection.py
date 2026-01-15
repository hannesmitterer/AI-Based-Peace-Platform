"""
TensorFlow-based Early Warning System
Scenario A: Detection of protocol and frequency anomalies
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class NetworkEvent:
    """Represents a network event for anomaly detection."""
    timestamp: float
    frequency: float
    protocol_id: int
    signal_strength: float
    packet_size: int
    source_ip: str


class AnomalyDetector:
    """
    TensorFlow-inspired early warning system for detecting
    protocol and frequency anomalies.
    
    Note: This is a lightweight implementation using numpy.
    For production, integrate actual TensorFlow models.
    """
    
    def __init__(self, 
                 threshold: float = 0.7,
                 window_size: int = 100):
        """
        Initialize anomaly detector.
        
        Args:
            threshold: Anomaly detection threshold (0-1)
            window_size: Number of events to analyze
        """
        self.threshold = threshold
        self.window_size = window_size
        self.event_history = []
        self.baseline_stats = None
        self.detected_anomalies = []
        
    def _extract_features(self, event: NetworkEvent) -> np.ndarray:
        """
        Extract features from network event.
        
        Args:
            event: Network event
            
        Returns:
            Feature vector
        """
        features = np.array([
            event.frequency / 3000.0,  # Normalize frequency
            event.signal_strength / 100.0,  # Normalize signal strength
            event.packet_size / 1500.0,  # Normalize packet size
            event.protocol_id / 256.0,  # Normalize protocol ID
        ])
        return features
    
    def train_baseline(self, events: List[NetworkEvent]):
        """
        Train baseline model from normal network events.
        
        Args:
            events: List of normal network events
        """
        if len(events) < 10:
            raise ValueError("Need at least 10 events for baseline training")
        
        # Extract features from all events
        features = np.array([self._extract_features(event) for event in events])
        
        # Calculate baseline statistics
        self.baseline_stats = {
            'mean': np.mean(features, axis=0),
            'std': np.std(features, axis=0),
            'min': np.min(features, axis=0),
            'max': np.max(features, axis=0)
        }
        
        print(f"✓ Baseline trained with {len(events)} events")
    
    def _calculate_anomaly_score(self, event: NetworkEvent) -> float:
        """
        Calculate anomaly score for an event.
        
        Args:
            event: Network event to analyze
            
        Returns:
            Anomaly score (0-1, higher = more anomalous)
        """
        if self.baseline_stats is None:
            raise ValueError("Baseline model not trained")
        
        features = self._extract_features(event)
        mean = self.baseline_stats['mean']
        std = self.baseline_stats['std']
        
        # Calculate z-scores
        z_scores = np.abs((features - mean) / (std + 1e-6))
        
        # Aggregate anomaly score using max z-score
        anomaly_score = np.tanh(np.max(z_scores) / 3.0)  # Normalize to 0-1
        
        return float(anomaly_score)
    
    def detect_anomaly(self, event: NetworkEvent) -> Tuple[bool, float, Dict]:
        """
        Detect if event is anomalous.
        
        Args:
            event: Network event to analyze
            
        Returns:
            Tuple of (is_anomaly, score, details)
        """
        score = self._calculate_anomaly_score(event)
        is_anomaly = score >= self.threshold
        
        details = {
            'timestamp': event.timestamp,
            'score': score,
            'threshold': self.threshold,
            'frequency': event.frequency,
            'protocol_id': event.protocol_id,
            'source_ip': event.source_ip
        }
        
        if is_anomaly:
            self.detected_anomalies.append(details)
        
        # Update event history
        self.event_history.append(event)
        if len(self.event_history) > self.window_size:
            self.event_history.pop(0)
        
        return is_anomaly, score, details
    
    def detect_frequency_deviation(self, 
                                   frequency: float,
                                   expected_range: Tuple[float, float]) -> bool:
        """
        Detect frequency deviations from expected range.
        
        Args:
            frequency: Observed frequency in MHz
            expected_range: Tuple of (min_freq, max_freq)
            
        Returns:
            True if deviation detected
        """
        min_freq, max_freq = expected_range
        return frequency < min_freq or frequency > max_freq
    
    def detect_protocol_anomaly(self, 
                                protocol_sequence: List[int],
                                expected_protocol: int) -> bool:
        """
        Detect protocol anomalies in communication sequence.
        
        Args:
            protocol_sequence: Sequence of protocol IDs
            expected_protocol: Expected protocol ID
            
        Returns:
            True if anomaly detected
        """
        if not protocol_sequence:
            return False
        
        # Check for unexpected protocol switches
        unexpected_count = sum(1 for p in protocol_sequence if p != expected_protocol)
        anomaly_ratio = unexpected_count / len(protocol_sequence)
        
        return anomaly_ratio > 0.2  # More than 20% unexpected protocols
    
    def get_statistics(self) -> Dict:
        """Get detector statistics."""
        return {
            'total_events_processed': len(self.event_history),
            'anomalies_detected': len(self.detected_anomalies),
            'detection_rate': len(self.detected_anomalies) / max(len(self.event_history), 1),
            'threshold': self.threshold,
            'baseline_trained': self.baseline_stats is not None
        }
    
    def export_anomalies(self, filepath: str):
        """Export detected anomalies to file."""
        with open(filepath, 'w') as f:
            json.dump(self.detected_anomalies, f, indent=2)
        print(f"✓ Exported {len(self.detected_anomalies)} anomalies to {filepath}")


class ProtocolValidator:
    """Validates network protocol compliance."""
    
    def __init__(self):
        self.valid_protocols = {
            1: 'ICMP',
            6: 'TCP',
            17: 'UDP',
            47: 'GRE',
            50: 'ESP',
            51: 'AH'
        }
        self.validation_history = []
    
    def validate_protocol(self, protocol_id: int) -> bool:
        """
        Validate if protocol ID is recognized.
        
        Args:
            protocol_id: Protocol number
            
        Returns:
            True if valid
        """
        is_valid = protocol_id in self.valid_protocols
        self.validation_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'protocol_id': protocol_id,
            'valid': is_valid,
            'protocol_name': self.valid_protocols.get(protocol_id, 'UNKNOWN')
        })
        return is_valid
    
    def get_validation_stats(self) -> Dict:
        """Get validation statistics."""
        total = len(self.validation_history)
        if total == 0:
            return {'valid_count': 0, 'invalid_count': 0, 'validation_rate': 0.0}
        
        valid_count = sum(1 for v in self.validation_history if v['valid'])
        return {
            'valid_count': valid_count,
            'invalid_count': total - valid_count,
            'validation_rate': valid_count / total
        }


if __name__ == "__main__":
    # Demonstration
    print("=== Early Warning System Demo ===")
    
    # Create detector
    detector = AnomalyDetector(threshold=0.7)
    
    # Generate baseline training data (normal events)
    print("\nGenerating baseline data...")
    baseline_events = []
    for i in range(50):
        event = NetworkEvent(
            timestamp=i * 1.0,
            frequency=2400.0 + np.random.normal(0, 5),
            protocol_id=6,  # TCP
            signal_strength=-70.0 + np.random.normal(0, 5),
            packet_size=1000 + int(np.random.normal(0, 100)),
            source_ip=f"192.168.1.{i % 255}"
        )
        baseline_events.append(event)
    
    # Train baseline
    detector.train_baseline(baseline_events)
    
    # Test with normal event
    print("\nTesting with normal event...")
    normal_event = NetworkEvent(
        timestamp=100.0,
        frequency=2405.0,
        protocol_id=6,
        signal_strength=-68.0,
        packet_size=1050,
        source_ip="192.168.1.100"
    )
    is_anomaly, score, details = detector.detect_anomaly(normal_event)
    print(f"  Normal event - Anomaly: {is_anomaly}, Score: {score:.3f}")
    
    # Test with anomalous event
    print("\nTesting with anomalous event...")
    anomalous_event = NetworkEvent(
        timestamp=101.0,
        frequency=2800.0,  # Unusual frequency
        protocol_id=99,  # Unusual protocol
        signal_strength=-30.0,  # Unusual signal strength
        packet_size=5000,  # Unusual packet size
        source_ip="10.0.0.1"
    )
    is_anomaly, score, details = detector.detect_anomaly(anomalous_event)
    print(f"  Anomalous event - Anomaly: {is_anomaly}, Score: {score:.3f}")
    
    # Print statistics
    stats = detector.get_statistics()
    print(f"\n=== Statistics ===")
    print(f"Events processed: {stats['total_events_processed']}")
    print(f"Anomalies detected: {stats['anomalies_detected']}")
    print(f"Detection rate: {stats['detection_rate']:.2%}")
    
    print("\n✓ Early warning system initialized")
