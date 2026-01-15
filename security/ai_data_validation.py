"""
AI Data Validation and Poisoning Detection
Scenario B: Defense against AI injection attacks and data poisoning
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class DataSample:
    """Represents a data sample for AI training/inference."""
    data: np.ndarray
    label: Optional[int] = None
    timestamp: float = 0.0
    source: str = "unknown"
    metadata: Dict = None


class DataPoisoningDetector:
    """
    Detects and mitigates data poisoning attacks on AI systems.
    """
    
    def __init__(self, 
                 contamination_threshold: float = 0.1,
                 statistical_threshold: float = 3.0):
        """
        Initialize data poisoning detector.
        
        Args:
            contamination_threshold: Expected proportion of outliers
            statistical_threshold: Z-score threshold for anomaly detection
        """
        self.contamination_threshold = contamination_threshold
        self.statistical_threshold = statistical_threshold
        self.baseline_stats = None
        self.detected_poison_samples = []
        self.validated_samples = []
        
    def compute_baseline_statistics(self, clean_samples: List[DataSample]):
        """
        Compute baseline statistics from known clean samples.
        
        Args:
            clean_samples: List of verified clean data samples
        """
        if len(clean_samples) < 10:
            raise ValueError("Need at least 10 clean samples for baseline")
        
        # Extract data arrays
        data_arrays = [sample.data for sample in clean_samples]
        data_matrix = np.vstack(data_arrays)
        
        # Compute statistics
        self.baseline_stats = {
            'mean': np.mean(data_matrix, axis=0),
            'std': np.std(data_matrix, axis=0),
            'median': np.median(data_matrix, axis=0),
            'min': np.min(data_matrix, axis=0),
            'max': np.max(data_matrix, axis=0),
            'sample_count': len(clean_samples)
        }
        
        print(f"✓ Baseline computed from {len(clean_samples)} clean samples")
    
    def detect_statistical_anomaly(self, sample: DataSample) -> Tuple[bool, float]:
        """
        Detect statistical anomalies in data sample.
        
        Args:
            sample: Data sample to check
            
        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        if self.baseline_stats is None:
            raise ValueError("Baseline statistics not computed")
        
        mean = self.baseline_stats['mean']
        std = self.baseline_stats['std']
        
        # Calculate z-scores
        z_scores = np.abs((sample.data - mean) / (std + 1e-10))
        
        # Maximum z-score as anomaly indicator
        max_z_score = np.max(z_scores)
        is_anomaly = max_z_score > self.statistical_threshold
        
        return is_anomaly, float(max_z_score)
    
    def detect_label_flipping(self, 
                             samples: List[DataSample],
                             expected_label_distribution: Dict[int, float]) -> List[int]:
        """
        Detect label flipping attacks.
        
        Args:
            samples: List of labeled samples
            expected_label_distribution: Expected distribution of labels
            
        Returns:
            List of indices of suspicious samples
        """
        if not samples:
            return []
        
        # Count actual label distribution
        label_counts = {}
        for sample in samples:
            if sample.label is not None:
                label_counts[sample.label] = label_counts.get(sample.label, 0) + 1
        
        # Calculate actual distribution
        total = sum(label_counts.values())
        actual_distribution = {k: v/total for k, v in label_counts.items()}
        
        # Find labels with suspicious distribution
        suspicious_indices = []
        for i, sample in enumerate(samples):
            if sample.label is None:
                continue
            
            expected_freq = expected_label_distribution.get(sample.label, 0)
            actual_freq = actual_distribution.get(sample.label, 0)
            
            # If actual frequency is significantly different from expected
            if abs(actual_freq - expected_freq) > 0.15:  # 15% threshold
                suspicious_indices.append(i)
        
        return suspicious_indices
    
    def detect_backdoor_pattern(self, 
                                samples: List[DataSample],
                                trigger_size: int = 5) -> Tuple[bool, List[int]]:
        """
        Detect backdoor/trojan patterns in data.
        
        Args:
            samples: List of data samples
            trigger_size: Size of potential trigger pattern
            
        Returns:
            Tuple of (backdoor_detected, suspicious_sample_indices)
        """
        if len(samples) < 10:
            return False, []
        
        # Look for repeated patterns (potential triggers)
        pattern_counts = {}
        sample_indices = {}
        
        for i, sample in enumerate(samples):
            # Extract small pattern from data
            if len(sample.data) >= trigger_size:
                pattern = tuple(sample.data[:trigger_size].round(2))
                
                if pattern not in pattern_counts:
                    pattern_counts[pattern] = 0
                    sample_indices[pattern] = []
                
                pattern_counts[pattern] += 1
                sample_indices[pattern].append(i)
        
        # Find suspiciously common patterns
        total_samples = len(samples)
        suspicious_samples = []
        
        for pattern, count in pattern_counts.items():
            frequency = count / total_samples
            
            # If pattern appears in >20% of samples, it's suspicious
            if frequency > 0.2:
                suspicious_samples.extend(sample_indices[pattern])
        
        backdoor_detected = len(suspicious_samples) > 0
        
        return backdoor_detected, suspicious_samples
    
    def validate_sample(self, sample: DataSample) -> Tuple[bool, Dict]:
        """
        Comprehensive validation of a data sample.
        
        Args:
            sample: Sample to validate
            
        Returns:
            Tuple of (is_valid, validation_details)
        """
        validation_details = {
            'timestamp': datetime.utcnow().isoformat(),
            'source': sample.source,
            'checks_passed': [],
            'checks_failed': []
        }
        
        # Check 1: Statistical anomaly
        try:
            is_anomaly, anomaly_score = self.detect_statistical_anomaly(sample)
            if not is_anomaly:
                validation_details['checks_passed'].append('statistical_check')
            else:
                validation_details['checks_failed'].append({
                    'check': 'statistical_check',
                    'score': anomaly_score
                })
        except ValueError:
            validation_details['checks_failed'].append({
                'check': 'statistical_check',
                'reason': 'baseline_not_computed'
            })
        
        # Check 2: Range validation
        if self.baseline_stats is not None:
            min_val = self.baseline_stats['min']
            max_val = self.baseline_stats['max']
            
            # Allow 10% margin outside observed range
            margin = (max_val - min_val) * 0.1
            in_range = np.all((sample.data >= min_val - margin) & 
                            (sample.data <= max_val + margin))
            
            if in_range:
                validation_details['checks_passed'].append('range_check')
            else:
                validation_details['checks_failed'].append({
                    'check': 'range_check',
                    'reason': 'values_outside_expected_range'
                })
        
        # Check 3: Data integrity
        has_nan = np.any(np.isnan(sample.data))
        has_inf = np.any(np.isinf(sample.data))
        
        if not has_nan and not has_inf:
            validation_details['checks_passed'].append('integrity_check')
        else:
            validation_details['checks_failed'].append({
                'check': 'integrity_check',
                'has_nan': has_nan,
                'has_inf': has_inf
            })
        
        is_valid = len(validation_details['checks_failed']) == 0
        
        if is_valid:
            self.validated_samples.append(sample)
        else:
            self.detected_poison_samples.append({
                'sample': sample,
                'details': validation_details
            })
        
        return is_valid, validation_details
    
    def sanitize_dataset(self, 
                        samples: List[DataSample],
                        auto_remove: bool = True) -> Tuple[List[DataSample], List[DataSample]]:
        """
        Sanitize dataset by removing poisoned samples.
        
        Args:
            samples: Dataset to sanitize
            auto_remove: Automatically remove detected poison samples
            
        Returns:
            Tuple of (clean_samples, removed_samples)
        """
        clean_samples = []
        removed_samples = []
        
        for sample in samples:
            is_valid, details = self.validate_sample(sample)
            
            if is_valid:
                clean_samples.append(sample)
            elif auto_remove:
                removed_samples.append(sample)
            else:
                # Keep suspicious samples but flag them
                sample.metadata = sample.metadata or {}
                sample.metadata['flagged'] = True
                sample.metadata['validation'] = details
                clean_samples.append(sample)
        
        print(f"✓ Sanitization complete: {len(clean_samples)} clean, {len(removed_samples)} removed")
        
        return clean_samples, removed_samples
    
    def get_validation_statistics(self) -> Dict:
        """Get validation statistics."""
        return {
            'total_validated': len(self.validated_samples),
            'poison_detected': len(self.detected_poison_samples),
            'poisoning_rate': len(self.detected_poison_samples) / 
                            max(len(self.validated_samples) + len(self.detected_poison_samples), 1),
            'baseline_computed': self.baseline_stats is not None
        }


class ModelIntegrityChecker:
    """
    Checks AI model integrity to detect trojans or modifications.
    """
    
    def __init__(self):
        self.model_checksums = {}
        self.verification_history = []
    
    def register_model(self, model_id: str, model_weights: np.ndarray):
        """
        Register a trusted model with its checksum.
        
        Args:
            model_id: Model identifier
            model_weights: Model weight parameters
        """
        # Compute checksum of model weights
        weights_bytes = model_weights.tobytes()
        checksum = hashlib.sha256(weights_bytes).hexdigest()
        
        self.model_checksums[model_id] = {
            'checksum': checksum,
            'registered_at': datetime.utcnow().isoformat(),
            'weight_shape': model_weights.shape,
            'weight_size': model_weights.size
        }
        
        print(f"✓ Model {model_id} registered with checksum {checksum[:16]}...")
    
    def verify_model(self, model_id: str, model_weights: np.ndarray) -> Tuple[bool, Dict]:
        """
        Verify model integrity against registered checksum.
        
        Args:
            model_id: Model identifier
            model_weights: Current model weights
            
        Returns:
            Tuple of (is_valid, verification_details)
        """
        if model_id not in self.model_checksums:
            return False, {'error': 'Model not registered'}
        
        # Compute current checksum
        weights_bytes = model_weights.tobytes()
        current_checksum = hashlib.sha256(weights_bytes).hexdigest()
        
        registered_info = self.model_checksums[model_id]
        is_valid = current_checksum == registered_info['checksum']
        
        verification_details = {
            'model_id': model_id,
            'valid': is_valid,
            'expected_checksum': registered_info['checksum'],
            'actual_checksum': current_checksum,
            'verified_at': datetime.utcnow().isoformat()
        }
        
        self.verification_history.append(verification_details)
        
        return is_valid, verification_details


if __name__ == "__main__":
    import hashlib
    
    # Demonstration
    print("=== Data Poisoning Detection Demo ===")
    
    # Create detector
    detector = DataPoisoningDetector()
    
    # Generate clean training data
    print("\nGenerating clean baseline data...")
    clean_samples = []
    for i in range(50):
        data = np.random.normal(0, 1, 10)
        sample = DataSample(data=data, label=0, source="trusted")
        clean_samples.append(sample)
    
    # Compute baseline
    detector.compute_baseline_statistics(clean_samples)
    
    # Test with clean sample
    print("\nTesting clean sample...")
    clean_test = DataSample(data=np.random.normal(0, 1, 10), label=0, source="test")
    is_valid, details = detector.validate_sample(clean_test)
    print(f"  Clean sample valid: {is_valid}")
    print(f"  Checks passed: {len(details['checks_passed'])}")
    
    # Test with poisoned sample
    print("\nTesting poisoned sample...")
    poisoned_test = DataSample(data=np.random.normal(10, 1, 10), label=0, source="malicious")
    is_valid, details = detector.validate_sample(poisoned_test)
    print(f"  Poisoned sample valid: {is_valid}")
    print(f"  Checks failed: {len(details['checks_failed'])}")
    
    # Test dataset sanitization
    print("\nSanitizing mixed dataset...")
    mixed_dataset = clean_samples[:10]
    # Add some poisoned samples
    for _ in range(3):
        poisoned = DataSample(data=np.random.normal(10, 1, 10), label=0, source="malicious")
        mixed_dataset.append(poisoned)
    
    clean, removed = detector.sanitize_dataset(mixed_dataset)
    print(f"  Clean samples: {len(clean)}")
    print(f"  Removed samples: {len(removed)}")
    
    # Print statistics
    stats = detector.get_validation_statistics()
    print(f"\n=== Statistics ===")
    print(f"Total validated: {stats['total_validated']}")
    print(f"Poison detected: {stats['poison_detected']}")
    print(f"Poisoning rate: {stats['poisoning_rate']:.2%}")
    
    # Test model integrity checking
    print("\n=== Model Integrity Check Demo ===")
    integrity_checker = ModelIntegrityChecker()
    
    # Register a model
    model_weights = np.random.randn(100, 50)
    integrity_checker.register_model("peace_model_v1", model_weights)
    
    # Verify same model
    is_valid, details = integrity_checker.verify_model("peace_model_v1", model_weights)
    print(f"Model integrity check: {is_valid}")
    
    # Verify modified model
    modified_weights = model_weights + 0.001  # Slight modification
    is_valid, details = integrity_checker.verify_model("peace_model_v1", modified_weights)
    print(f"Modified model integrity check: {is_valid}")
    
    print("\n✓ AI data validation initialized")
