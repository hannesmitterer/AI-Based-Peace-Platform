"""
Lex Amoris Security Integration
Master module integrating all Lex Amoris strategic enhancements.

Combines:
1. Dynamic blacklist and rhythm validation
2. Lazy security with energy-based protection
3. IPFS backup and mirroring
4. Rescue channel for false positive handling
"""

from typing import Dict, Any, Optional
from datetime import datetime

from lex_amoris_rhythm_validator import RhythmValidator
from lazy_security import LazySecurity, SecurityLevel
from ipfs_backup import IPFSBackupManager
from lex_amoris_rescue_channel import (
    LexAmorisRescueChannel, 
    RescuePriority,
    RescueMessageType
)


class LexAmorisSecurityPlatform:
    """
    Integrated Lex Amoris security platform.
    Provides comprehensive protection through multiple coordinated layers.
    """
    
    def __init__(self,
                 rhythm_base_frequency: float = 432.0,
                 lazy_activation_threshold: float = 50.0,
                 ipfs_gateway: str = "https://ipfs.io",
                 backup_path: str = "/tmp/ipfs_backups"):
        
        # Initialize components
        self.rhythm_validator = RhythmValidator(base_frequency=rhythm_base_frequency)
        self.lazy_security = LazySecurity(activation_threshold=lazy_activation_threshold)
        self.ipfs_backup = IPFSBackupManager(ipfs_gateway=ipfs_gateway, backup_path=backup_path)
        self.rescue_channel = LexAmorisRescueChannel()
        
        # Register protection modules with lazy security
        self._register_protection_modules()
        
        # Statistics
        self.total_requests_processed = 0
        self.total_blocked = 0
        self.total_rescued = 0
        
    def _register_protection_modules(self):
        """Register protection modules with lazy security system"""
        
        # Rhythm validation module
        def rhythm_protection(request_data: Dict[str, Any]) -> Dict[str, Any]:
            result = self.rhythm_validator.validate_packet(request_data)
            return {"allowed": result["valid"], "details": result}
        
        self.lazy_security.register_protection_module(
            "rhythm_validation",
            rhythm_protection,
            energy_cost=2.0
        )
        
        # Rate limiting module (placeholder)
        def rate_limiting(request_data: Dict[str, Any]) -> Dict[str, Any]:
            # Simple rate limiting logic
            return {"allowed": True}
        
        self.lazy_security.register_protection_module(
            "rate_limiting",
            rate_limiting,
            energy_cost=1.0
        )
        
        # Monitoring module
        def monitoring(request_data: Dict[str, Any]) -> Dict[str, Any]:
            # Just log, never block
            return {"allowed": True, "logged": True}
        
        self.lazy_security.register_protection_module(
            "monitoring",
            monitoring,
            energy_cost=0.5
        )
    
    def process_request(self, 
                       request_data: Dict[str, Any],
                       origin_ip: Optional[str] = None,
                       sender_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a request through the complete Lex Amoris security platform.
        
        Args:
            request_data: Request to process
            origin_ip: Origin IP address (optional)
            sender_id: Sender identifier (optional)
            
        Returns:
            Processing result with security decisions
        """
        self.total_requests_processed += 1
        
        # Step 1: Update lazy security state (scan environment)
        security_state = self.lazy_security.update_security_state()
        
        # Step 2: Process through lazy security
        lazy_result = self.lazy_security.process_request(request_data)
        
        # If blocked and security is active, check if rescue is possible
        if not lazy_result["allowed"] and sender_id:
            # Check if this is a potential false positive
            node_id = f"node-{sender_id}"
            
            # Check if node is already unblocked via rescue channel
            if node_id in self.rescue_channel.unblocked_nodes:
                # Allow through - node has been rescued
                result = {
                    "allowed": True,
                    "reason": "rescued_node",
                    "original_block_reason": lazy_result["reason"],
                    "security_level": security_state["security"]["current_level"],
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                self.total_rescued += 1
            else:
                # Blocked - suggest rescue channel
                result = {
                    "allowed": False,
                    "reason": lazy_result["reason"],
                    "details": lazy_result,
                    "security_level": security_state["security"]["current_level"],
                    "rescue_available": True,
                    "rescue_instructions": {
                        "message": "Use rescue channel to request unblock",
                        "endpoint": "/api/rescue/request"
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                self.total_blocked += 1
        else:
            result = {
                "allowed": lazy_result["allowed"],
                "reason": lazy_result["reason"],
                "details": lazy_result,
                "security_level": security_state["security"]["current_level"],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            if not lazy_result["allowed"]:
                self.total_blocked += 1
        
        return result
    
    def request_rescue(self,
                      sender_id: str,
                      node_id: str,
                      reason: str,
                      evidence: Dict[str, Any],
                      priority: str = "NORMAL") -> Dict[str, Any]:
        """
        Request rescue/unblock for a blocked node.
        
        Args:
            sender_id: ID of requester
            node_id: ID of blocked node
            reason: Reason for rescue
            evidence: Supporting evidence
            priority: Priority level (LOW, NORMAL, HIGH, CRITICAL)
            
        Returns:
            Rescue result
        """
        # Convert priority string to enum
        priority_map = {
            "LOW": RescuePriority.LOW,
            "NORMAL": RescuePriority.NORMAL,
            "HIGH": RescuePriority.HIGH,
            "CRITICAL": RescuePriority.CRITICAL
        }
        priority_enum = priority_map.get(priority.upper(), RescuePriority.NORMAL)
        
        # Send rescue request
        result = self.rescue_channel.send_rescue_request(
            sender_id=sender_id,
            node_id=node_id,
            reason=reason,
            evidence=evidence,
            priority=priority_enum
        )
        
        return result
    
    def create_backup_snapshot(self) -> Dict[str, Any]:
        """
        Create complete IPFS backup snapshot of current state.
        
        Returns:
            Backup result with IPFS hashes
        """
        # Backup security configuration
        security_config = {
            "rhythm_validation": {
                "base_frequency": self.rhythm_validator.base_frequency,
                "tolerance": self.rhythm_validator.tolerance,
                "blacklist": self.rhythm_validator.get_blacklist_status()
            },
            "lazy_security": self.lazy_security.get_status(),
            "rescue_channel": self.rescue_channel.get_rescue_status(),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        security_backup = self.ipfs_backup.backup_security_configuration(security_config)
        
        # Create full mirror
        mirrors = self.ipfs_backup.create_full_mirror()
        
        return {
            "security_backup": {
                "backup_id": security_backup.backup_id,
                "content_hash": security_backup.content_hash,
                "size_bytes": security_backup.size_bytes,
                "gateway_url": security_backup.metadata.get("gateway_url")
            },
            "full_mirror": {
                key: {
                    "backup_id": record.backup_id,
                    "content_hash": record.content_hash,
                    "type": record.backup_type
                }
                for key, record in mirrors.items()
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def get_platform_status(self) -> Dict[str, Any]:
        """
        Get comprehensive platform status.
        
        Returns:
            Complete status of all components
        """
        return {
            "platform": "Lex Amoris Security Platform",
            "version": "1.0.0",
            "components": {
                "rhythm_validator": {
                    "status": "active",
                    "blacklist": self.rhythm_validator.get_blacklist_status()
                },
                "lazy_security": self.lazy_security.get_status(),
                "ipfs_backup": self.ipfs_backup.get_backup_status(),
                "rescue_channel": self.rescue_channel.get_rescue_status()
            },
            "statistics": {
                "total_requests": self.total_requests_processed,
                "total_blocked": self.total_blocked,
                "total_rescued": self.total_rescued,
                "block_rate": round(self.total_blocked / max(self.total_requests_processed, 1), 2)
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# Singleton instance for easy access
_platform_instance: Optional[LexAmorisSecurityPlatform] = None


def get_platform() -> LexAmorisSecurityPlatform:
    """Get singleton platform instance"""
    global _platform_instance
    if _platform_instance is None:
        _platform_instance = LexAmorisSecurityPlatform()
    return _platform_instance
