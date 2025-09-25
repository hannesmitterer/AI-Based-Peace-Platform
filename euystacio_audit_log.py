"""
Euystacio Audit Logger - Immutable audit logging subsystem (Phase 4.2)

This module provides comprehensive, tamper-resistant audit logging for all
critical kernel events, especially those flagged by the guardian system.
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading
from pathlib import Path

class ImmutableAuditLogger:
    """Immutable audit logging system with cryptographic integrity protection"""
    
    def __init__(self, log_file: str = 'council_ledger.log', backup_count: int = 5):
        self.log_file = log_file
        self.backup_count = backup_count
        self.log_lock = threading.Lock()
        self.integrity_chain = []
        self.last_hash = self._initialize_hash_chain()
        
        # Ensure log directory exists
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Create initial log file if it doesn't exist
        if not os.path.exists(self.log_file):
            self._initialize_log_file()
    
    def _initialize_hash_chain(self) -> str:
        """Initialize the cryptographic hash chain"""
        if os.path.exists(self.log_file):
            return self._get_last_hash_from_file()
        return hashlib.sha256("GENESIS_BLOCK".encode()).hexdigest()
    
    def _get_last_hash_from_file(self) -> str:
        """Get the last entry hash from log file"""
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if last_line:
                        last_entry = json.loads(last_line)
                        return last_entry.get('entry_hash', '')
        except:
            pass
        return hashlib.sha256("GENESIS_BLOCK".encode()).hexdigest()
    
    def _initialize_log_file(self):
        """Initialize log file with genesis entry"""
        with self.log_lock:  # Add locking for initialization
            # Check if file was created by another thread while waiting
            if os.path.exists(self.log_file):
                self.last_hash = self._get_last_hash_from_file()
                return
                
            genesis_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'system_initialization',
                'data': {
                    'action': 'audit_system_initialized',
                    'version': '1.0.0',
                    'security_level': 'high'
                },
                'sequence': 0,
                'previous_hash': self.last_hash,
                'entry_hash': ''
            }
            
            # Calculate entry hash
            entry_for_hash = genesis_entry.copy()
            entry_for_hash.pop('entry_hash')
            genesis_entry['entry_hash'] = hashlib.sha256(
                json.dumps(entry_for_hash, sort_keys=True).encode()
            ).hexdigest()
            
            with open(self.log_file, 'w') as f:
                f.write(json.dumps(genesis_entry) + '\n')
            
            self.last_hash = genesis_entry['entry_hash']
    
    def log_event(self, event_type: str, data: Dict[str, Any], 
                  security_level: str = "normal") -> str:
        """Log event with immutable chaining and integrity protection"""
        with self.log_lock:
            try:
                # Get sequence number
                sequence = self._get_next_sequence()
                
                # Create log entry
                log_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': event_type,
                    'data': data,
                    'security_level': security_level,
                    'sequence': sequence,
                    'previous_hash': self.last_hash,
                    'entry_hash': ''
                }
                
                # Calculate entry hash (excluding the hash field itself)
                entry_for_hash = log_entry.copy()
                entry_for_hash.pop('entry_hash')
                entry_hash = hashlib.sha256(
                    json.dumps(entry_for_hash, sort_keys=True).encode()
                ).hexdigest()
                
                log_entry['entry_hash'] = entry_hash
                
                # Write to log file
                with open(self.log_file, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
                
                # Update chain
                self.last_hash = entry_hash
                self.integrity_chain.append({
                    'sequence': sequence,
                    'hash': entry_hash,
                    'timestamp': log_entry['timestamp']
                })
                
                # Rotate logs if needed
                if sequence % 1000 == 0:  # Rotate every 1000 entries
                    self._rotate_logs()
                
                return entry_hash
                
            except Exception as e:
                # Critical: audit logging failure
                emergency_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'audit_system_error',
                    'data': {
                        'error': str(e),
                        'original_event_type': event_type,
                        'security_level': 'critical'
                    }
                }
                
                # Try to write emergency entry
                try:
                    with open(f"{self.log_file}.emergency", 'a') as f:
                        f.write(json.dumps(emergency_entry) + '\n')
                except:
                    pass  # Last resort - can't even log the error
                
                raise Exception(f"Audit logging failure: {e}")
    
    def _get_next_sequence(self) -> int:
        """Get next sequence number from log file"""
        if not os.path.exists(self.log_file):
            return 0
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                if not lines:
                    return 0
                
                last_line = lines[-1].strip()
                if last_line:
                    last_entry = json.loads(last_line)
                    return last_entry.get('sequence', -1) + 1
                return 0
        except:
            return 0
    
    def verify_integrity_chain(self) -> Dict[str, Any]:
        """Verify the complete integrity of the audit log chain"""
        if not os.path.exists(self.log_file):
            return {"status": "error", "reason": "log_file_not_found"}
        
        try:
            with open(self.log_file, 'r') as f:
                entries = []
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
            
            if not entries:
                return {"status": "empty", "entries": 0}
            
            # Verify hash chain
            integrity_issues = []
            
            for i, entry in enumerate(entries):
                # Verify entry hash
                entry_for_hash = entry.copy()
                expected_hash = entry_for_hash.pop('entry_hash', '')
                calculated_hash = hashlib.sha256(
                    json.dumps(entry_for_hash, sort_keys=True).encode()
                ).hexdigest()
                
                if expected_hash != calculated_hash:
                    integrity_issues.append({
                        'sequence': entry.get('sequence', i),
                        'issue': 'hash_mismatch',
                        'expected': expected_hash,
                        'calculated': calculated_hash
                    })
                
                # Verify chain linkage
                if i > 0:
                    previous_entry = entries[i-1]
                    if entry.get('previous_hash') != previous_entry.get('entry_hash'):
                        integrity_issues.append({
                            'sequence': entry.get('sequence', i),
                            'issue': 'chain_break',
                            'expected_previous': previous_entry.get('entry_hash'),
                            'actual_previous': entry.get('previous_hash')
                        })
            
            return {
                "status": "verified" if not integrity_issues else "compromised",
                "entries": len(entries),
                "integrity_issues": integrity_issues,
                "first_entry": entries[0]['timestamp'] if entries else None,
                "last_entry": entries[-1]['timestamp'] if entries else None,
                "verification_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "reason": f"verification_failed: {str(e)}"}
    
    def get_integrity_hash(self) -> str:
        """Get overall integrity hash of the entire log file"""
        if not os.path.exists(self.log_file):
            return ""
        
        hasher = hashlib.sha256()
        try:
            with open(self.log_file, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return ""
    
    def _rotate_logs(self):
        """Rotate log files to prevent them from growing too large"""
        try:
            # Rotate backup files
            for i in range(self.backup_count - 1, 0, -1):
                old_file = f"{self.log_file}.{i}"
                new_file = f"{self.log_file}.{i + 1}"
                if os.path.exists(old_file):
                    os.rename(old_file, new_file)
            
            # Move current log to .1
            if os.path.exists(self.log_file):
                os.rename(self.log_file, f"{self.log_file}.1")
            
            # Create new log file with chain continuation
            self._initialize_log_file()
            
        except Exception as e:
            # Log rotation failure - continue with current file
            pass
    
    def get_recent_events(self, hours: int = 24, event_types: List[str] = None) -> List[Dict[str, Any]]:
        """Get recent events from the audit log"""
        if not os.path.exists(self.log_file):
            return []
        
        cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
        recent_events = []
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entry = json.loads(line)
                        entry_time = datetime.fromisoformat(entry['timestamp']).timestamp()
                        
                        if entry_time >= cutoff_time:
                            if not event_types or entry['type'] in event_types:
                                recent_events.append(entry)
            
            return recent_events
            
        except Exception as e:
            return []
    
    def export_audit_report(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Export comprehensive audit report"""
        try:
            integrity_status = self.verify_integrity_chain()
            recent_events = self.get_recent_events(24)  # Last 24 hours
            
            # Count events by type
            event_counts = {}
            security_levels = {}
            
            for event in recent_events:
                event_type = event.get('type', 'unknown')
                security_level = event.get('security_level', 'normal')
                
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                security_levels[security_level] = security_levels.get(security_level, 0) + 1
            
            return {
                "report_timestamp": datetime.utcnow().isoformat(),
                "integrity_status": integrity_status,
                "recent_activity_summary": {
                    "total_events_24h": len(recent_events),
                    "events_by_type": event_counts,
                    "events_by_security_level": security_levels
                },
                "system_status": {
                    "log_file": self.log_file,
                    "log_file_size": os.path.getsize(self.log_file) if os.path.exists(self.log_file) else 0,
                    "last_hash": self.last_hash,
                    "chain_length": len(self.integrity_chain)
                }
            }
            
        except Exception as e:
            return {
                "report_timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e)
            }

# Global audit logger instance
_audit_logger = ImmutableAuditLogger()

# Backward compatibility function
def log_event(event_type: str, data: Any = None, security_level: str = "normal") -> str:
    """Log event using global audit logger (backward compatible)"""
    if isinstance(data, str):
        # Handle legacy string-only data
        data = {"message": data}
    elif not isinstance(data, dict):
        data = {"data": data}
    
    return _audit_logger.log_event(event_type, data, security_level)

# Additional convenience functions
def log_security_event(event_type: str, data: Dict[str, Any]) -> str:
    """Log high-security event"""
    return _audit_logger.log_event(event_type, data, "high")

def log_critical_event(event_type: str, data: Dict[str, Any]) -> str:
    """Log critical security event"""
    return _audit_logger.log_event(event_type, data, "critical")

def verify_audit_integrity() -> Dict[str, Any]:
    """Verify audit log integrity"""
    return _audit_logger.verify_integrity_chain()

def get_audit_report() -> Dict[str, Any]:
    """Get comprehensive audit report"""
    return _audit_logger.export_audit_report()

# Legacy class for compatibility
class EuystacioAuditLogger:
    """Legacy audit logger class for backward compatibility"""
    
    def __init__(self, log_file='council_ledger.log'):
        self.log_file = log_file
    
    def log_event(self, event_type, data):
        return log_event(event_type, data)
    
    def get_integrity_hash(self):
        return _audit_logger.get_integrity_hash()
