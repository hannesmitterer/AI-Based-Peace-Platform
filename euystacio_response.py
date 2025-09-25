"""
Euystacio Response Module - Handles threat response protocols and safety mechanisms

This module implements the response protocols for the euystacio-helmi-ai kernel,
including safe mode activation, alert generation, and input quarantine mechanisms.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from euystacio_audit_log import log_event
from euystacio_core import update_kernel_state, get_current_state

class QuarantineManager:
    """Manages quarantine of suspicious inputs"""
    
    def __init__(self):
        self.quarantined_inputs = []
        self.quarantine_reasons = {}
    
    def quarantine_input(self, input_data: Dict[str, Any], reason: str) -> str:
        """Quarantine suspicious input with reason"""
        quarantine_id = f"q_{int(time.time())}_{len(self.quarantined_inputs)}"
        
        quarantine_record = {
            'id': quarantine_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': input_data.copy(),
            'reason': reason,
            'status': 'quarantined'
        }
        
        self.quarantined_inputs.append(quarantine_record)
        self.quarantine_reasons[quarantine_id] = reason
        
        log_event("input_quarantine", {
            "action": "input_quarantined",
            "quarantine_id": quarantine_id,
            "reason": reason,
            "data_hash": hash(str(input_data))
        })
        
        return quarantine_id
    
    def release_quarantine(self, quarantine_id: str, authorized_by: str) -> bool:
        """Release quarantined input if authorized"""
        for record in self.quarantined_inputs:
            if record['id'] == quarantine_id:
                record['status'] = 'released'
                record['released_by'] = authorized_by
                record['released_at'] = datetime.utcnow().isoformat()
                
                log_event("input_quarantine", {
                    "action": "quarantine_released", 
                    "quarantine_id": quarantine_id,
                    "authorized_by": authorized_by
                })
                return True
        return False

class SafeModeManager:
    """Manages kernel safe mode operations"""
    
    def __init__(self):
        self.safe_mode_history = []
        self.safe_mode_restrictions = {
            'disable_external_api': True,
            'limit_state_changes': True,
            'enhanced_logging': True,
            'require_authorization': True
        }
    
    def activate_safe_mode(self, reason: str, triggered_by: str = "guardian") -> bool:
        """Activate safe mode with comprehensive logging"""
        current_state = get_current_state()
        if current_state.get('safe_mode'):
            log_event("safe_mode", {"action": "already_active", "reason": reason})
            return True
        
        # Update kernel state to safe mode
        safe_mode_update = {
            'safe_mode': True,
            'alert_level': 'critical'
        }
        
        if update_kernel_state(safe_mode_update, f"safe_mode_activation_{triggered_by}"):
            # Record safe mode activation
            activation_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'reason': reason,
                'triggered_by': triggered_by,
                'previous_state': current_state,
                'restrictions': self.safe_mode_restrictions
            }
            
            self.safe_mode_history.append(activation_record)
            
            log_event("safe_mode", {
                "action": "activated",
                "reason": reason,
                "triggered_by": triggered_by,
                "restrictions": self.safe_mode_restrictions
            })
            
            # Send critical alert
            send_alert(f"SAFE MODE ACTIVATED: {reason}", severity="critical")
            return True
        
        return False
    
    def deactivate_safe_mode(self, authorized_by: str, authorization_code: str = None) -> bool:
        """Deactivate safe mode with proper authorization"""
        current_state = get_current_state()
        if not current_state.get('safe_mode'):
            log_event("safe_mode", {"action": "not_active", "authorized_by": authorized_by})
            return True
        
        # Verify authorization (simplified - would be more robust in production)
        if not self._verify_deactivation_authorization(authorized_by, authorization_code):
            log_event("safe_mode", {
                "action": "deactivation_unauthorized",
                "authorized_by": authorized_by
            })
            send_alert(f"Unauthorized safe mode deactivation attempt by {authorized_by}", severity="warning")
            return False
        
        # Update kernel state 
        deactivation_update = {
            'safe_mode': False,
            'alert_level': 'normal'
        }
        
        if update_kernel_state(deactivation_update, f"safe_mode_deactivation_{authorized_by}"):
            # Update history record
            if self.safe_mode_history:
                self.safe_mode_history[-1].update({
                    'deactivated_at': datetime.utcnow().isoformat(),
                    'deactivated_by': authorized_by
                })
            
            log_event("safe_mode", {
                "action": "deactivated",
                "authorized_by": authorized_by
            })
            
            send_alert(f"Safe mode deactivated by {authorized_by}", severity="info")
            return True
        
        return False
    
    def _verify_deactivation_authorization(self, authorized_by: str, authorization_code: str = None) -> bool:
        """Verify authorization for safe mode deactivation"""
        # Simplified authorization - in production would use cryptographic verification
        authorized_users = ['admin', 'guardian', 'operator']
        return authorized_by in authorized_users

class AlertManager:
    """Manages system alerts and notifications"""
    
    def __init__(self):
        self.alert_history = []
        self.alert_levels = {
            'info': 1,
            'warning': 2, 
            'critical': 3,
            'emergency': 4
        }
    
    def send_alert(self, message: str, severity: str = "warning", 
                   alert_type: str = "general", recipients: List[str] = None) -> str:
        """Send system alert with proper categorization"""
        alert_id = f"alert_{int(time.time())}_{len(self.alert_history)}"
        
        alert_record = {
            'id': alert_id,
            'timestamp': datetime.utcnow().isoformat(),
            'message': message,
            'severity': severity,
            'type': alert_type,
            'recipients': recipients or ['system_admin'],
            'status': 'sent'
        }
        
        self.alert_history.append(alert_record)
        
        log_event("alert", {
            "alert_id": alert_id,
            "message": message,
            "severity": severity,
            "type": alert_type,
            "recipients": recipients or ['system_admin']
        })
        
        # In production, this would integrate with external notification systems
        print(f"[ALERT-{severity.upper()}] {message}")
        
        return alert_id
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts within specified timeframe"""
        cutoff_time = time.time() - (hours * 3600)
        recent_alerts = []
        
        for alert in self.alert_history:
            alert_time = datetime.fromisoformat(alert['timestamp']).timestamp()
            if alert_time >= cutoff_time:
                recent_alerts.append(alert)
        
        return recent_alerts

# Global instances
_quarantine_manager = QuarantineManager()
_safe_mode_manager = SafeModeManager()
_alert_manager = AlertManager()

# Public API functions used by guardian
def activate_safe_mode(reason: str = "Threat detected", triggered_by: str = "guardian") -> bool:
    """Activate kernel safe mode (Phase 4.1)"""
    return _safe_mode_manager.activate_safe_mode(reason, triggered_by)

def deactivate_safe_mode(authorized_by: str, authorization_code: str = None) -> bool:
    """Deactivate safe mode with authorization"""
    return _safe_mode_manager.deactivate_safe_mode(authorized_by, authorization_code)

def send_alert(message: str, severity: str = "warning", alert_type: str = "security") -> str:
    """Send system alert (Phase 4.1)"""
    return _alert_manager.send_alert(message, severity, alert_type)

def quarantine_input(input_data: Dict[str, Any], reason: str) -> str:
    """Quarantine suspicious input (Phase 4.1)"""
    return _quarantine_manager.quarantine_input(input_data, reason)

def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status"""
    current_state = get_current_state()
    recent_alerts = _alert_manager.get_recent_alerts()
    
    return {
        'kernel_state': current_state,
        'safe_mode_active': current_state.get('safe_mode', False),
        'alert_level': current_state.get('alert_level', 'normal'),
        'recent_alerts_count': len(recent_alerts),
        'quarantined_inputs': len(_quarantine_manager.quarantined_inputs),
        'timestamp': datetime.utcnow().isoformat()
    }

def emergency_shutdown(reason: str, triggered_by: str = "system") -> bool:
    """Emergency shutdown protocol with full logging"""
    log_event("emergency_shutdown", {
        "reason": reason,
        "triggered_by": triggered_by,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Activate safe mode first
    activate_safe_mode(f"Emergency shutdown: {reason}", triggered_by)
    
    # Send emergency alert
    send_alert(f"EMERGENCY SHUTDOWN INITIATED: {reason}", severity="emergency")
    
    # Additional shutdown procedures would go here
    return True