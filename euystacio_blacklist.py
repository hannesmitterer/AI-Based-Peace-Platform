"""
Euystacio Permanent Blacklist Module - Persistent node and entity blocking system

This module implements a permanent blacklist (playlist permanente) for the EUYSTACIO framework
to block communications from suspicious nodes and entities that threaten system security.
This provides continuous protection against attack attempts and theft.
"""

import json
import hashlib
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import threading

# Safe logging wrapper to prevent blocking
def _safe_log(log_func, event_type: str, data: Dict[str, Any]):
    """Safely call logging function without blocking"""
    try:
        log_func(event_type, data)
    except:
        # If logging fails, continue - blacklist functionality is critical
        pass

# Import audit logging with lazy loading
_log_security_event = None
_log_critical_event = None

def _get_loggers():
    """Lazy load audit loggers"""
    global _log_security_event, _log_critical_event
    if _log_security_event is None:
        try:
            from euystacio_audit_log import log_security_event, log_critical_event
            _log_security_event = log_security_event
            _log_critical_event = log_critical_event
        except:
            # Create no-op loggers if import fails
            _log_security_event = lambda *args, **kwargs: None
            _log_critical_event = lambda *args, **kwargs: None
    return _log_security_event, _log_critical_event

class PermanentBlacklist:
    """Permanent blacklist for blocking suspicious nodes and entities"""
    
    def __init__(self, blacklist_file: str = 'euystacio_blacklist.json'):
        self.blacklist_file = blacklist_file
        self.blacklist_lock = threading.Lock()
        self.blacklist_data = {
            'nodes': {},          # Blocked nodes (IP addresses, node IDs)
            'entities': {},       # Blocked entities (user IDs, API keys)
            'patterns': {},       # Blocked patterns (suspicious signatures)
            'metadata': {
                'created_at': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'total_blocks': 0
            }
        }
        
        # Load existing blacklist or create new one
        self._load_blacklist()
        
        # In-memory cache for fast lookups
        self._node_cache: Set[str] = set()
        self._entity_cache: Set[str] = set()
        self._pattern_cache: Set[str] = set()
        self._rebuild_cache()
        
        # Log initialization (safe - only after everything is set up)
        log_sec, _ = _get_loggers()
        _safe_log(log_sec, "blacklist_initialized", {
            "blacklist_file": self.blacklist_file,
            "nodes_count": len(self.blacklist_data['nodes']),
            "entities_count": len(self.blacklist_data['entities']),
            "patterns_count": len(self.blacklist_data['patterns'])
        })
    
    def _load_blacklist(self):
        """Load blacklist from persistent storage"""
        if os.path.exists(self.blacklist_file):
            try:
                with open(self.blacklist_file, 'r') as f:
                    loaded_data = json.load(f)
                    # Merge with default structure to handle version upgrades
                    self.blacklist_data.update(loaded_data)
                    
                _safe_log(_get_loggers()[0], "blacklist_loaded", {
                    "file": self.blacklist_file,
                    "nodes": len(self.blacklist_data.get('nodes', {})),
                    "entities": len(self.blacklist_data.get('entities', {}))
                })
            except Exception as e:
                _safe_log(_get_loggers()[1], "blacklist_load_failed", {
                    "error": str(e),
                    "file": self.blacklist_file
                })
                # Continue with empty blacklist
        else:
            # Create new blacklist file (call internal method without locking)
            self._save_blacklist_internal()
    
    def _save_blacklist_internal(self):
        """Internal save without acquiring lock (caller must hold lock)"""
        try:
            # Update metadata
            self.blacklist_data['metadata']['last_updated'] = datetime.utcnow().isoformat()
            
            # Ensure directory exists
            Path(self.blacklist_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first
            temp_file = f"{self.blacklist_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(self.blacklist_data, f, indent=2)
            
            # Atomic replace
            os.replace(temp_file, self.blacklist_file)
            
            _safe_log(_get_loggers()[0], "blacklist_saved", {
                "file": self.blacklist_file,
                "total_blocks": self.blacklist_data['metadata']['total_blocks']
            })
        except Exception as e:
            _safe_log(_get_loggers()[1], "blacklist_save_failed", {
                "error": str(e),
                "file": self.blacklist_file
            })
            raise
    
    def _save_blacklist(self):
        """Save blacklist to persistent storage"""
        with self.blacklist_lock:
            self._save_blacklist_internal()
    
    def _rebuild_cache(self):
        """Rebuild in-memory cache for fast lookups"""
        self._node_cache = set(self.blacklist_data.get('nodes', {}).keys())
        self._entity_cache = set(self.blacklist_data.get('entities', {}).keys())
        self._pattern_cache = set(self.blacklist_data.get('patterns', {}).keys())
    
    def add_node(self, node_id: str, reason: str, severity: str = "high", 
                 metadata: Dict[str, Any] = None) -> bool:
        """Add node to permanent blacklist"""
        with self.blacklist_lock:
            if node_id in self.blacklist_data['nodes']:
                # Update existing entry
                self.blacklist_data['nodes'][node_id]['occurrences'] += 1
                self.blacklist_data['nodes'][node_id]['last_seen'] = datetime.utcnow().isoformat()
                updated = True
            else:
                # Create new entry
                self.blacklist_data['nodes'][node_id] = {
                    'added_at': datetime.utcnow().isoformat(),
                    'last_seen': datetime.utcnow().isoformat(),
                    'reason': reason,
                    'severity': severity,
                    'metadata': metadata or {},
                    'occurrences': 1,
                    'status': 'active'
                }
                self.blacklist_data['metadata']['total_blocks'] += 1
                updated = False
            
            # Update cache
            self._node_cache.add(node_id)
            
            # Save to disk (use internal method - we already have the lock)
            self._save_blacklist_internal()
            
            # Log the block
            _safe_log(_get_loggers()[1], "node_blacklisted", {
                "node_id": node_id,
                "reason": reason,
                "severity": severity,
                "updated": updated
            })
            
            return True
    
    def add_entity(self, entity_id: str, reason: str, severity: str = "high",
                   metadata: Dict[str, Any] = None) -> bool:
        """Add entity to permanent blacklist"""
        with self.blacklist_lock:
            if entity_id in self.blacklist_data['entities']:
                # Update existing entry
                self.blacklist_data['entities'][entity_id]['occurrences'] += 1
                self.blacklist_data['entities'][entity_id]['last_seen'] = datetime.utcnow().isoformat()
                updated = True
            else:
                # Create new entry
                self.blacklist_data['entities'][entity_id] = {
                    'added_at': datetime.utcnow().isoformat(),
                    'last_seen': datetime.utcnow().isoformat(),
                    'reason': reason,
                    'severity': severity,
                    'metadata': metadata or {},
                    'occurrences': 1,
                    'status': 'active'
                }
                self.blacklist_data['metadata']['total_blocks'] += 1
                updated = False
            
            # Update cache
            self._entity_cache.add(entity_id)
            
            # Save to disk (use internal method - we already have the lock)
            self._save_blacklist_internal()
            
            # Log the block
            _safe_log(_get_loggers()[1], "entity_blacklisted", {
                "entity_id": entity_id,
                "reason": reason,
                "severity": severity,
                "updated": updated
            })
            
            return True
    
    def add_pattern(self, pattern: str, reason: str, severity: str = "medium",
                    metadata: Dict[str, Any] = None) -> bool:
        """Add suspicious pattern to permanent blacklist"""
        with self.blacklist_lock:
            pattern_hash = hashlib.md5(pattern.encode()).hexdigest()
            
            if pattern_hash in self.blacklist_data['patterns']:
                # Update existing entry
                self.blacklist_data['patterns'][pattern_hash]['occurrences'] += 1
                updated = True
            else:
                # Create new entry
                self.blacklist_data['patterns'][pattern_hash] = {
                    'pattern': pattern,
                    'added_at': datetime.utcnow().isoformat(),
                    'reason': reason,
                    'severity': severity,
                    'metadata': metadata or {},
                    'occurrences': 1,
                    'status': 'active'
                }
                self.blacklist_data['metadata']['total_blocks'] += 1
                updated = False
            
            # Update cache
            self._pattern_cache.add(pattern_hash)
            
            # Save to disk (use internal method - we already have the lock)
            self._save_blacklist_internal()
            
            # Log the block
            _safe_log(_get_loggers()[0], "pattern_blacklisted", {
                "pattern_hash": pattern_hash,
                "reason": reason,
                "severity": severity,
                "updated": updated
            })
            
            return True
    
    def is_node_blocked(self, node_id: str) -> bool:
        """Check if node is in blacklist (fast cache lookup)"""
        return node_id in self._node_cache
    
    def is_entity_blocked(self, entity_id: str) -> bool:
        """Check if entity is in blacklist (fast cache lookup)"""
        return entity_id in self._entity_cache
    
    def is_pattern_blocked(self, content: str) -> bool:
        """Check if content matches any blocked pattern"""
        # Check against all patterns
        for pattern_hash in self._pattern_cache:
            pattern_entry = self.blacklist_data['patterns'].get(pattern_hash, {})
            pattern = pattern_entry.get('pattern', '')
            if pattern and pattern.lower() in content.lower():
                # Update last seen
                with self.blacklist_lock:
                    pattern_entry['last_seen'] = datetime.utcnow().isoformat()
                    pattern_entry['occurrences'] += 1
                return True
        return False
    
    def check_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check input data against blacklist (comprehensive check)"""
        blocks = {
            'blocked': False,
            'reasons': [],
            'severity': 'none'
        }
        
        # Extract identifiers from input
        node_id = input_data.get('node_id')
        entity_id = input_data.get('entity_id')
        source_ip = input_data.get('source_ip')
        api_key = input_data.get('api_key')
        content = str(input_data.get('content', ''))
        
        # Check node ID
        if node_id and self.is_node_blocked(node_id):
            blocks['blocked'] = True
            blocks['reasons'].append(f"Node {node_id} is blacklisted")
            blocks['severity'] = self._get_severity(self.blacklist_data['nodes'][node_id]['severity'], blocks['severity'])
        
        # Check source IP as node
        if source_ip and self.is_node_blocked(source_ip):
            blocks['blocked'] = True
            blocks['reasons'].append(f"Source IP {source_ip} is blacklisted")
            blocks['severity'] = self._get_severity(self.blacklist_data['nodes'][source_ip]['severity'], blocks['severity'])
        
        # Check entity ID
        if entity_id and self.is_entity_blocked(entity_id):
            blocks['blocked'] = True
            blocks['reasons'].append(f"Entity {entity_id} is blacklisted")
            blocks['severity'] = self._get_severity(self.blacklist_data['entities'][entity_id]['severity'], blocks['severity'])
        
        # Check API key as entity
        if api_key and self.is_entity_blocked(api_key):
            blocks['blocked'] = True
            blocks['reasons'].append(f"API key is blacklisted")
            blocks['severity'] = 'critical'
        
        # Check content patterns
        if content and self.is_pattern_blocked(content):
            blocks['blocked'] = True
            blocks['reasons'].append("Content matches blocked pattern")
            blocks['severity'] = self._get_severity('medium', blocks['severity'])
        
        # Log if blocked
        if blocks['blocked']:
            _safe_log(_get_loggers()[0], "input_blocked_by_blacklist", {
                "reasons": blocks['reasons'],
                "severity": blocks['severity'],
                "input_hash": hashlib.md5(str(input_data).encode()).hexdigest()
            })
        
        return blocks
    
    def _get_severity(self, new_severity: str, current_severity: str) -> str:
        """Get higher severity level"""
        severity_levels = {'none': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        new_level = severity_levels.get(new_severity, 0)
        current_level = severity_levels.get(current_severity, 0)
        
        if new_level > current_level:
            return new_severity
        return current_severity
    
    def remove_node(self, node_id: str, authorized_by: str) -> bool:
        """Remove node from blacklist (requires authorization)"""
        with self.blacklist_lock:
            if node_id in self.blacklist_data['nodes']:
                # Mark as removed (soft delete for audit trail)
                self.blacklist_data['nodes'][node_id]['status'] = 'removed'
                self.blacklist_data['nodes'][node_id]['removed_at'] = datetime.utcnow().isoformat()
                self.blacklist_data['nodes'][node_id]['removed_by'] = authorized_by
                
                # Remove from cache
                self._node_cache.discard(node_id)
                
                # Save to disk (use internal method - we already have the lock)
                self._save_blacklist_internal()
                
                _safe_log(_get_loggers()[0], "node_removed_from_blacklist", {
                    "node_id": node_id,
                    "authorized_by": authorized_by
                })
                return True
        return False
    
    def remove_entity(self, entity_id: str, authorized_by: str) -> bool:
        """Remove entity from blacklist (requires authorization)"""
        with self.blacklist_lock:
            if entity_id in self.blacklist_data['entities']:
                # Mark as removed (soft delete for audit trail)
                self.blacklist_data['entities'][entity_id]['status'] = 'removed'
                self.blacklist_data['entities'][entity_id]['removed_at'] = datetime.utcnow().isoformat()
                self.blacklist_data['entities'][entity_id]['removed_by'] = authorized_by
                
                # Remove from cache
                self._entity_cache.discard(entity_id)
                
                # Save to disk (use internal method - we already have the lock)
                self._save_blacklist_internal()
                
                _safe_log(_get_loggers()[0], "entity_removed_from_blacklist", {
                    "entity_id": entity_id,
                    "authorized_by": authorized_by
                })
                return True
        return False
    
    def get_blacklist_status(self) -> Dict[str, Any]:
        """Get comprehensive blacklist status"""
        with self.blacklist_lock:
            active_nodes = sum(1 for n in self.blacklist_data['nodes'].values() if n.get('status') == 'active')
            active_entities = sum(1 for e in self.blacklist_data['entities'].values() if e.get('status') == 'active')
            active_patterns = sum(1 for p in self.blacklist_data['patterns'].values() if p.get('status') == 'active')
            
            return {
                'total_blocks': self.blacklist_data['metadata']['total_blocks'],
                'active_blocks': {
                    'nodes': active_nodes,
                    'entities': active_entities,
                    'patterns': active_patterns,
                    'total': active_nodes + active_entities + active_patterns
                },
                'metadata': self.blacklist_data['metadata'],
                'cache_status': {
                    'node_cache_size': len(self._node_cache),
                    'entity_cache_size': len(self._entity_cache),
                    'pattern_cache_size': len(self._pattern_cache)
                },
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_blocked_nodes(self, include_removed: bool = False) -> List[Dict[str, Any]]:
        """Get list of all blocked nodes"""
        nodes = []
        for node_id, data in self.blacklist_data['nodes'].items():
            if include_removed or data.get('status') == 'active':
                nodes.append({
                    'node_id': node_id,
                    **data
                })
        return nodes
    
    def get_blocked_entities(self, include_removed: bool = False) -> List[Dict[str, Any]]:
        """Get list of all blocked entities"""
        entities = []
        for entity_id, data in self.blacklist_data['entities'].items():
            if include_removed or data.get('status') == 'active':
                entities.append({
                    'entity_id': entity_id,
                    **data
                })
        return entities
    
    def export_blacklist(self, file_path: str = None) -> str:
        """Export blacklist to JSON file"""
        export_path = file_path or f"blacklist_export_{int(time.time())}.json"
        
        with self.blacklist_lock:
            export_data = {
                'exported_at': datetime.utcnow().isoformat(),
                'blacklist_version': self.blacklist_data['metadata']['version'],
                'data': self.blacklist_data
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            _safe_log(_get_loggers()[0], "blacklist_exported", {
                "export_path": export_path,
                "total_blocks": self.blacklist_data['metadata']['total_blocks']
            })
            
            return export_path

# Global blacklist instance
_permanent_blacklist = PermanentBlacklist()

# Public API functions
def add_node_to_blacklist(node_id: str, reason: str, severity: str = "high", 
                          metadata: Dict[str, Any] = None) -> bool:
    """Add node to permanent blacklist"""
    return _permanent_blacklist.add_node(node_id, reason, severity, metadata)

def add_entity_to_blacklist(entity_id: str, reason: str, severity: str = "high",
                            metadata: Dict[str, Any] = None) -> bool:
    """Add entity to permanent blacklist"""
    return _permanent_blacklist.add_entity(entity_id, reason, severity, metadata)

def add_pattern_to_blacklist(pattern: str, reason: str, severity: str = "medium",
                             metadata: Dict[str, Any] = None) -> bool:
    """Add suspicious pattern to permanent blacklist"""
    return _permanent_blacklist.add_pattern(pattern, reason, severity, metadata)

def is_node_blocked(node_id: str) -> bool:
    """Check if node is blacklisted"""
    return _permanent_blacklist.is_node_blocked(node_id)

def is_entity_blocked(entity_id: str) -> bool:
    """Check if entity is blacklisted"""
    return _permanent_blacklist.is_entity_blocked(entity_id)

def check_input_against_blacklist(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Check input against permanent blacklist"""
    return _permanent_blacklist.check_input(input_data)

def get_blacklist_status() -> Dict[str, Any]:
    """Get blacklist status"""
    return _permanent_blacklist.get_blacklist_status()

def remove_node_from_blacklist(node_id: str, authorized_by: str) -> bool:
    """Remove node from blacklist (authorized only)"""
    return _permanent_blacklist.remove_node(node_id, authorized_by)

def remove_entity_from_blacklist(entity_id: str, authorized_by: str) -> bool:
    """Remove entity from blacklist (authorized only)"""
    return _permanent_blacklist.remove_entity(entity_id, authorized_by)
