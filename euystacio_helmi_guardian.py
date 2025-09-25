"""
Euystacio Helmi Guardian - Advanced threat detection and response system

This module implements the core guardian functionality for the euystacio-helmi-ai kernel,
providing real-time monitoring, anomaly detection, and automated threat response.
Phase 2.1, 3.2, and 4.1 implementation.
"""

import hashlib
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from euystacio_core import get_current_state, get_kernel_heartbeat, validate_input_integrity
from euystacio_audit_log import log_event
from euystacio_response import activate_safe_mode, send_alert, quarantine_input

class WatchdogTimer:
    """Watchdog timer for monitoring kernel heartbeat (Phase 2.2)"""
    
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        self.last_heartbeat = time.time()
        self.running = False
        self.thread = None
        
    def start(self):
        """Start watchdog monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_heartbeat, daemon=True)
        self.thread.start()
        log_event("watchdog", {"action": "started", "timeout": self.timeout_seconds})
    
    def stop(self):
        """Stop watchdog monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        log_event("watchdog", {"action": "stopped"})
    
    def reset(self):
        """Reset watchdog timer"""
        self.last_heartbeat = time.time()
    
    def _monitor_heartbeat(self):
        """Monitor kernel heartbeat in separate thread"""
        while self.running:
            try:
                current_heartbeat = get_kernel_heartbeat()
                if current_heartbeat == 0.0 or (time.time() - current_heartbeat) > self.timeout_seconds:
                    log_event("watchdog", {
                        "alert": "heartbeat_timeout",
                        "last_heartbeat": current_heartbeat,
                        "timeout": self.timeout_seconds
                    })
                    activate_safe_mode("Watchdog timeout - kernel heartbeat lost", "watchdog")
                    send_alert("WATCHDOG ALERT: Kernel heartbeat timeout detected", "critical")
                
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                log_event("watchdog", {"error": f"Watchdog monitoring error: {str(e)}"})

class DualValidationSystem:
    """Dual validation system for critical decisions (Phase 2.2)"""
    
    def __init__(self):
        self.validation_history = []
    
    def validate_decision(self, decision: Dict[str, Any], decision_type: str) -> bool:
        """Validate decision using two independent models"""
        try:
            # Primary validation
            primary_result = self._primary_validator(decision, decision_type)
            
            # Secondary validation (redundant check)
            secondary_result = self._secondary_validator(decision, decision_type)
            
            # Both validators must agree
            validation_passed = primary_result and secondary_result
            
            # Log validation attempt
            validation_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'decision': decision,
                'decision_type': decision_type,
                'primary_result': primary_result,
                'secondary_result': secondary_result,
                'final_result': validation_passed
            }
            
            self.validation_history.append(validation_record)
            
            log_event("dual_validation", {
                "decision_type": decision_type,
                "primary_result": primary_result,
                "secondary_result": secondary_result,
                "validation_passed": validation_passed
            })
            
            return validation_passed
            
        except Exception as e:
            log_event("dual_validation", {
                "error": f"Validation system error: {str(e)}",
                "decision_type": decision_type
            })
            return False
    
    def _primary_validator(self, decision: Dict[str, Any], decision_type: str) -> bool:
        """Primary validation logic"""
        if decision_type == "kill_switch_activation":
            # Strict validation for kill switch
            current_state = get_current_state()
            return (current_state.get('trust', 1.0) < 0.3 and 
                   current_state.get('harmony', 1.0) < 0.3)
        
        elif decision_type == "safe_mode_activation":
            # Validate safe mode activation criteria
            return decision.get('threat_level') in ['severe', 'critical']
        
        return True
    
    def _secondary_validator(self, decision: Dict[str, Any], decision_type: str) -> bool:
        """Secondary/redundant validation logic"""  
        if decision_type == "kill_switch_activation":
            # Additional checks for kill switch
            current_state = get_current_state()
            alert_level = current_state.get('alert_level', 'normal')
            return alert_level in ['critical', 'emergency']
        
        elif decision_type == "safe_mode_activation":
            # Cross-validate threat indicators
            return len(self.validation_history) == 0 or \
                   any(v['decision_type'] == 'anomaly_detected' 
                       for v in self.validation_history[-5:])  # Recent anomalies
        
        return True

class EuystacioHelmiGuardian:
    """Advanced guardian system for kernel protection and monitoring"""
    
    def __init__(self):
        self.baseline_state = self._establish_baseline()
        self.monitoring_active = False
        self.anomaly_threshold = 0.5  # Configurable threshold
        self.monitoring_interval = 1.0  # Check every second
        self.anomaly_history = []
        
        # Initialize subsystems
        self.watchdog = WatchdogTimer()
        self.dual_validator = DualValidationSystem()
        
        # Behavioral monitoring state
        self.behavior_profile = {
            'trust_variance': 0.0,
            'harmony_variance': 0.0,
            'emotion_changes_per_minute': 0.0,
            'context_changes_per_minute': 0.0
        }
        
        log_event("guardian", {"action": "initialized", "baseline": self.baseline_state})

    def _establish_baseline(self) -> Dict[str, Any]:
        """Establish baseline behavior patterns (Phase 3.2)"""
        # In production, this would analyze historical data
        return {
            'trust': 1.0,
            'harmony': 1.0,
            'emotion': 'Calm',
            'context': 'Calm',
            'max_trust_change': 0.1,  # Max expected change per minute
            'max_harmony_change': 0.1,
            'emotion_stability_threshold': 0.9,  # Expected stability
            'context_stability_threshold': 0.9
        }
    
    def start_monitoring(self):
        """Start continuous guardian monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.watchdog.start()
        
        # Start monitoring thread
        monitoring_thread = threading.Thread(target=self._continuous_monitor, daemon=True)
        monitoring_thread.start()
        
        log_event("guardian", {"action": "monitoring_started"})
        send_alert("Guardian monitoring activated", "info")
    
    def stop_monitoring(self):
        """Stop guardian monitoring"""
        self.monitoring_active = False
        self.watchdog.stop()
        log_event("guardian", {"action": "monitoring_stopped"})
    
    def _continuous_monitor(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                self.monitor()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                log_event("guardian", {"error": f"Monitoring loop error: {str(e)}"})
                time.sleep(5)  # Wait longer on error

    def monitor(self) -> Dict[str, Any]:
        """Enhanced monitoring with comprehensive anomaly detection (Phase 3.2)"""
        current_state = get_current_state()
        if not current_state:
            log_event("guardian", {"error": "Unable to retrieve current state"})
            return {"status": "error", "reason": "state_unavailable"}
        
        threat_indicators = []
        
        # Reset watchdog
        self.watchdog.reset()
        
        # 1. Internal State Monitoring (Enhanced)
        trust_anomaly = self._detect_trust_anomaly(current_state)
        if trust_anomaly:
            threat_indicators.append(trust_anomaly)
        
        harmony_anomaly = self._detect_harmony_anomaly(current_state)  
        if harmony_anomaly:
            threat_indicators.append(harmony_anomaly)
        
        # 2. Emotional Context Anomaly Detection
        emotion_anomaly = self._detect_emotional_anomaly(current_state)
        if emotion_anomaly:
            threat_indicators.append(emotion_anomaly)
        
        # 3. Behavioral Pattern Analysis
        behavior_anomaly = self._analyze_behavior_patterns(current_state)
        if behavior_anomaly:
            threat_indicators.append(behavior_anomaly)
        
        # 4. State Integrity Verification
        integrity_issue = self._verify_state_integrity(current_state)
        if integrity_issue:
            threat_indicators.append(integrity_issue)
        
        # Process threat indicators
        if threat_indicators:
            return self._process_threats(threat_indicators, current_state)
        
        return {"status": "normal", "timestamp": datetime.utcnow().isoformat()}
    
    def _detect_trust_anomaly(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect trust value anomalies"""
        trust_value = state.get('trust', 1.0)
        baseline_trust = self.baseline_state['trust']
        
        deviation = abs(trust_value - baseline_trust)
        
        if deviation > self.anomaly_threshold:
            return {
                'type': 'trust_anomaly',
                'severity': 'high' if deviation > 0.7 else 'medium',
                'details': {
                    'current_trust': trust_value,
                    'baseline_trust': baseline_trust,
                    'deviation': deviation
                }
            }
        return None
    
    def _detect_harmony_anomaly(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect harmony value anomalies"""  
        harmony_value = state.get('harmony', 1.0)
        baseline_harmony = self.baseline_state['harmony']
        
        deviation = abs(harmony_value - baseline_harmony)
        
        if deviation > self.anomaly_threshold:
            return {
                'type': 'harmony_anomaly', 
                'severity': 'high' if deviation > 0.7 else 'medium',
                'details': {
                    'current_harmony': harmony_value,
                    'baseline_harmony': baseline_harmony,
                    'deviation': deviation
                }
            }
        return None
    
    def _detect_emotional_anomaly(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect emotional context anomalies"""
        emotion = state.get('emotion', 'Calm')
        context = state.get('context', 'Calm')
        
        # Check for contradictory emotion-context pairs
        anomalous_pairs = [
            ('Anger', 'Calm'),
            ('Fear', 'Peaceful'), 
            ('Love', 'Crisis')
        ]
        
        if (emotion, context) in anomalous_pairs:
            return {
                'type': 'emotional_anomaly',
                'severity': 'medium',
                'details': {
                    'emotion': emotion,
                    'context': context,
                    'anomaly_reason': 'contradictory_emotion_context_pair'
                }
            }
        
        return None
    
    def _analyze_behavior_patterns(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze behavioral patterns for anomalies"""
        # This would be more sophisticated in production
        # For now, check for rapid state changes
        
        if len(self.anomaly_history) >= 5:
            recent_anomalies = self.anomaly_history[-5:]
            if len([a for a in recent_anomalies 
                   if (datetime.utcnow() - datetime.fromisoformat(a['timestamp'])).seconds < 300]) >= 3:
                return {
                    'type': 'pattern_anomaly',
                    'severity': 'high',
                    'details': {
                        'pattern': 'rapid_anomaly_frequency',
                        'recent_anomalies_count': 3,
                        'timeframe': '5_minutes'
                    }
                }
        
        return None
    
    def _verify_state_integrity(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Verify state integrity and consistency"""
        # Check for impossible state combinations
        trust = state.get('trust', 1.0)
        harmony = state.get('harmony', 1.0) 
        safe_mode = state.get('safe_mode', False)
        
        # If trust and harmony are very low, safe mode should be active
        if trust < 0.3 and harmony < 0.3 and not safe_mode:
            return {
                'type': 'integrity_anomaly',
                'severity': 'critical',
                'details': {
                    'issue': 'safe_mode_should_be_active',
                    'trust': trust,
                    'harmony': harmony,
                    'safe_mode': safe_mode
                }
            }
        
        return None
    
    def _process_threats(self, threat_indicators: List[Dict[str, Any]], 
                        current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Process detected threats and initiate appropriate responses"""
        
        # Categorize threats by severity
        critical_threats = [t for t in threat_indicators if t['severity'] == 'critical']
        high_threats = [t for t in threat_indicators if t['severity'] == 'high'] 
        medium_threats = [t for t in threat_indicators if t['severity'] == 'medium']
        
        # Record anomalies
        for threat in threat_indicators:
            anomaly_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'threat': threat,
                'state': current_state
            }
            self.anomaly_history.append(anomaly_record)
            
            log_event("anomaly_detection", {
                "threat_type": threat['type'],
                "severity": threat['severity'],
                "details": threat['details']
            })
        
        # Determine response level
        if critical_threats:
            return self.initiate_response(threat_level='critical', threats=threat_indicators)
        elif len(high_threats) >= 2 or (len(high_threats) >= 1 and len(medium_threats) >= 2):
            return self.initiate_response(threat_level='severe', threats=threat_indicators)
        elif high_threats or len(medium_threats) >= 3:
            return self.initiate_response(threat_level='moderate', threats=threat_indicators)
        
        return {"status": "threats_logged", "threat_count": len(threat_indicators)}

    def initiate_response(self, threat_level: str, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Initiate appropriate response based on threat level (Phase 4.1)"""
        
        response_actions = []
        
        if threat_level == 'critical':
            # Critical threats: immediate safe mode + emergency protocols
            if self.dual_validator.validate_decision(
                {"threat_level": threat_level, "threats": threats}, 
                "safe_mode_activation"
            ):
                activate_safe_mode(f"Critical threats detected: {len(threats)} issues", "guardian")
                send_alert(f"CRITICAL: Guardian detected {len(threats)} critical threats", "emergency")
                response_actions.extend(["safe_mode_activated", "emergency_alert_sent"])
        
        elif threat_level == 'severe':
            # Severe threats: safe mode activation
            if self.dual_validator.validate_decision(
                {"threat_level": threat_level, "threats": threats},
                "safe_mode_activation"  
            ):
                activate_safe_mode(f"Severe threats detected: {len(threats)} issues", "guardian")
                send_alert(f"SEVERE: Guardian activated safe mode due to threats", "critical")
                response_actions.extend(["safe_mode_activated", "critical_alert_sent"])
        
        elif threat_level == 'moderate':
            # Moderate threats: enhanced monitoring + warnings
            send_alert(f"MODERATE: Guardian detected {len(threats)} threats", "warning")
            response_actions.append("warning_alert_sent")
        
        # Log response
        log_event("threat_response", {
            "threat_level": threat_level,
            "threat_count": len(threats),
            "actions_taken": response_actions,
            "threats": [t['type'] for t in threats]
        })
        
        return {
            "status": "response_initiated",
            "threat_level": threat_level,
            "actions_taken": response_actions,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Enhanced input validation with guardian oversight (Phase 3.1)"""
        # Basic integrity validation
        if not validate_input_integrity(input_data):
            quarantine_input(input_data, "Failed basic integrity validation")
            return False
        
        # Guardian-specific validation
        try:
            # Check for suspicious patterns
            if self._detect_malicious_patterns(input_data):
                quarantine_input(input_data, "Suspicious input patterns detected")
                return False
            
            # Rate limiting check
            if self._check_rate_limiting(input_data):
                quarantine_input(input_data, "Rate limiting threshold exceeded")  
                return False
            
            log_event("input_validation", {
                "action": "guardian_validation_passed",
                "data_hash": hashlib.md5(str(input_data).encode()).hexdigest()
            })
            
            return True
            
        except Exception as e:
            log_event("input_validation", {
                "error": f"Guardian validation error: {str(e)}"
            })
            return False
    
    def _detect_malicious_patterns(self, input_data: Dict[str, Any]) -> bool:
        """Detect potentially malicious input patterns"""
        # Check for injection attempts
        if any(suspicious in str(input_data).lower() 
               for suspicious in ['<script>', 'javascript:', 'eval(', 'exec(']):
            return True
        
        # Check for unusual value combinations
        emotion = input_data.get('emotion', '')
        context = input_data.get('context', '')
        
        if emotion == 'Love' and context == 'Crisis':
            # Potentially suspicious combination
            return True
        
        return False
    
    def _check_rate_limiting(self, input_data: Dict[str, Any]) -> bool:
        """Check if input rate exceeds safe thresholds"""
        # Simple rate limiting - would be more sophisticated in production
        current_time = time.time()
        recent_inputs = [a for a in self.anomaly_history 
                        if current_time - datetime.fromisoformat(a['timestamp']).timestamp() < 60]
        
        return len(recent_inputs) > 100  # More than 100 inputs per minute
    
    def get_guardian_status(self) -> Dict[str, Any]:
        """Get comprehensive guardian status report"""
        return {
            'monitoring_active': self.monitoring_active,
            'baseline_state': self.baseline_state,
            'anomaly_threshold': self.anomaly_threshold,
            'recent_anomalies': len([a for a in self.anomaly_history 
                                   if (datetime.utcnow() - datetime.fromisoformat(a['timestamp'])).seconds < 3600]),
            'watchdog_status': 'active' if self.watchdog.running else 'inactive',
            'dual_validation_history': len(self.dual_validator.validation_history),
            'behavior_profile': self.behavior_profile,
            'timestamp': datetime.utcnow().isoformat()
        }
