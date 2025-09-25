"""
Euystacio Core Module - Central kernel state management and operations

This module provides the core functionality for the euystacio-helmi-ai kernel,
including state management, validation, and integration points for the guardian system.
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from euystacio_audit_log import log_event

class EuystacioKernelState:
    """Core kernel state management with integrity protection"""
    
    def __init__(self):
        self.state = {
            'trust': 1.0,
            'harmony': 1.0, 
            'emotion': 'Calm',
            'context': 'Calm',
            'last_updated': datetime.utcnow().isoformat(),
            'heartbeat': time.time(),
            'safe_mode': False,
            'alert_level': 'normal'
        }
        self.state_history = []
        self.integrity_hash = self._calculate_hash()
        
    def _calculate_hash(self) -> str:
        """Calculate cryptographic hash of current state"""
        state_json = json.dumps(self.state, sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify state integrity hasn't been compromised"""
        current_hash = self._calculate_hash()
        return current_hash == self.integrity_hash
    
    def update_state(self, updates: Dict[str, Any], source: str = "system") -> bool:
        """Update kernel state with integrity checks"""
        if not self.verify_integrity():
            log_event("kernel_state", {"error": "State integrity compromised before update", "source": source})
            return False
            
        # Store previous state
        previous_state = self.state.copy()
        
        # Apply updates with validation  
        for key, value in updates.items():
            if key in self.state:
                if self._validate_state_change(key, value, previous_state[key]):
                    self.state[key] = value
                else:
                    log_event("kernel_state", {
                        "error": f"Invalid state change rejected",
                        "key": key, 
                        "old_value": previous_state[key],
                        "new_value": value,
                        "source": source
                    })
                    return False
                    
        # Update metadata
        self.state['last_updated'] = datetime.utcnow().isoformat()
        self.state['heartbeat'] = time.time()
        
        # Store in history and update hash
        self.state_history.append({
            'timestamp': self.state['last_updated'],
            'previous_state': previous_state,
            'updates': updates,
            'source': source
        })
        
        self.integrity_hash = self._calculate_hash()
        
        # Log successful update
        log_event("kernel_state", {
            "action": "state_updated",
            "updates": updates,
            "source": source,
            "new_hash": self.integrity_hash
        })
        
        return True
    
    def _validate_state_change(self, key: str, new_value: Any, old_value: Any) -> bool:
        """Validate individual state changes"""
        if key in ['trust', 'harmony']:
            # Trust and harmony must be float between 0.0 and 1.0
            return isinstance(new_value, (int, float)) and 0.0 <= new_value <= 1.0
        elif key == 'emotion':
            # Emotion must be valid enum value
            valid_emotions = ['Love', 'Anger', 'Calm', 'Joy', 'Fear', 'Neutral']
            return new_value in valid_emotions
        elif key == 'context':
            # Context must be valid enum value  
            valid_contexts = ['Calm', 'Tense', 'Crisis', 'Peaceful', 'Uncertain']
            return new_value in valid_contexts
        elif key == 'safe_mode':
            return isinstance(new_value, bool)
        elif key == 'alert_level':
            valid_levels = ['normal', 'warning', 'critical', 'emergency']
            return new_value in valid_levels
        
        return True
    
    def get_state_copy(self) -> Dict[str, Any]:
        """Get immutable copy of current state"""
        if not self.verify_integrity():
            log_event("kernel_state", {"error": "State integrity compromised during read"})
            return {}
        return self.state.copy()

# Global kernel state instance
_kernel_state = EuystacioKernelState()

def get_current_state() -> Dict[str, Any]:
    """Get current kernel state - main API function used by guardian"""
    return _kernel_state.get_state_copy()

def update_kernel_state(updates: Dict[str, Any], source: str = "api") -> bool:
    """Update kernel state with validation and logging"""
    return _kernel_state.update_state(updates, source)

def validate_input_integrity(data: Dict[str, Any]) -> bool:
    """Validate input data integrity and format (Phase 3.1)"""
    try:
        # Basic structure validation
        required_fields = ['emotion', 'context']
        for field in required_fields:
            if field not in data:
                log_event("input_validation", {"error": f"Missing required field: {field}", "data": data})
                return False
        
        # Type validation
        if not isinstance(data['emotion'], str) or not isinstance(data['context'], str):
            log_event("input_validation", {"error": "Invalid data types", "data": data})
            return False
            
        # Value validation using state validator
        if not _kernel_state._validate_state_change('emotion', data['emotion'], None):
            log_event("input_validation", {"error": "Invalid emotion value", "emotion": data['emotion']})
            return False
            
        if not _kernel_state._validate_state_change('context', data['context'], None):
            log_event("input_validation", {"error": "Invalid context value", "context": data['context']})
            return False
        
        # Optional: Cryptographic signature validation would go here
        # if 'signature' in data:
        #     return verify_crypto_signature(data)
            
        log_event("input_validation", {"action": "validation_passed", "data": data})
        return True
        
    except Exception as e:
        log_event("input_validation", {"error": f"Validation exception: {str(e)}", "data": data})
        return False

def calculate_checksum(data: Dict[str, Any]) -> str:
    """Calculate checksum for data integrity verification"""
    data_json = json.dumps(data, sort_keys=True)
    return hashlib.md5(data_json.encode()).hexdigest()

def get_kernel_heartbeat() -> float:
    """Get kernel heartbeat timestamp for watchdog monitoring"""
    return _kernel_state.state.get('heartbeat', 0.0)

def is_safe_mode() -> bool:
    """Check if kernel is in safe mode"""
    return _kernel_state.state.get('safe_mode', False)