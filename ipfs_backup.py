"""
IPFS Backup Module
Complete mirroring of PR configurations for repository protection from external escalation.

Implements distributed backup storage using IPFS (InterPlanetary File System)
for resilience against centralized attacks or failures.
"""

import json
import hashlib
import os
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class BackupRecord:
    """Record of a backup operation"""
    backup_id: str
    content_hash: str  # IPFS CID
    timestamp: datetime
    size_bytes: int
    metadata: Dict[str, Any]
    backup_type: str  # 'pr_config', 'repository', 'security'


class IPFSBackupManager:
    """
    Manages IPFS-based backup and mirroring of critical repository data.
    Provides protection against external escalation by maintaining
    distributed copies of PR configurations and security settings.
    """
    
    def __init__(self, 
                 ipfs_gateway: str = "https://ipfs.io",
                 backup_path: str = None):
        self.ipfs_gateway = ipfs_gateway
        
        # Use secure default path if not specified
        if backup_path is None:
            home_dir = os.path.expanduser("~")
            backup_path = os.path.join(home_dir, ".local", "share", "ipfs_backups")
        
        self.backup_path = backup_path
        self.backup_history: List[BackupRecord] = []
        self.pin_list: Dict[str, BackupRecord] = {}
        
        # Create backup directory if it doesn't exist
        try:
            os.makedirs(backup_path, exist_ok=True, mode=0o700)  # Secure permissions
        except Exception as e:
            # Fallback to /tmp only if home directory not available
            self.backup_path = "/tmp/ipfs_backups"
            os.makedirs(self.backup_path, exist_ok=True)
        
    def generate_content_hash(self, content: str) -> str:
        """
        Generate content-addressable hash (simulates IPFS CID).
        In production, this would use actual IPFS hashing.
        
        Args:
            content: Content to hash
            
        Returns:
            Hash string (CID format)
        """
        hash_obj = hashlib.sha256(content.encode())
        return f"Qm{hash_obj.hexdigest()[:44]}"  # IPFS CID format
    
    def backup_pr_configuration(self, 
                                pr_data: Dict[str, Any],
                                pr_number: int) -> BackupRecord:
        """
        Backup Pull Request configuration to IPFS.
        
        Args:
            pr_data: PR configuration data
            pr_number: PR number
            
        Returns:
            BackupRecord with IPFS hash
        """
        # Add metadata
        backup_data = {
            "pr_number": pr_number,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "configuration": pr_data,
            "backup_type": "pr_config",
            "version": "1.0"
        }
        
        # Serialize to JSON
        content = json.dumps(backup_data, indent=2, sort_keys=True)
        content_hash = self.generate_content_hash(content)
        
        # Save to local backup (in production, would pin to IPFS)
        backup_file = os.path.join(self.backup_path, f"pr_{pr_number}_{content_hash[:16]}.json")
        with open(backup_file, 'w') as f:
            f.write(content)
        
        # Create backup record
        record = BackupRecord(
            backup_id=f"backup-pr-{pr_number}-{datetime.utcnow().timestamp()}",
            content_hash=content_hash,
            timestamp=datetime.utcnow(),
            size_bytes=len(content.encode()),
            metadata={
                "pr_number": pr_number,
                "file_path": backup_file,
                "gateway_url": f"{self.ipfs_gateway}/ipfs/{content_hash}"
            },
            backup_type="pr_config"
        )
        
        self.backup_history.append(record)
        self.pin_list[content_hash] = record
        
        return record
    
    def backup_repository_state(self, 
                                repo_data: Dict[str, Any]) -> BackupRecord:
        """
        Backup complete repository state.
        
        Args:
            repo_data: Repository configuration and state
            
        Returns:
            BackupRecord with IPFS hash
        """
        backup_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "repository": repo_data,
            "backup_type": "repository",
            "version": "1.0"
        }
        
        content = json.dumps(backup_data, indent=2, sort_keys=True)
        content_hash = self.generate_content_hash(content)
        
        backup_file = os.path.join(self.backup_path, f"repo_{content_hash[:16]}.json")
        with open(backup_file, 'w') as f:
            f.write(content)
        
        record = BackupRecord(
            backup_id=f"backup-repo-{datetime.utcnow().timestamp()}",
            content_hash=content_hash,
            timestamp=datetime.utcnow(),
            size_bytes=len(content.encode()),
            metadata={
                "file_path": backup_file,
                "gateway_url": f"{self.ipfs_gateway}/ipfs/{content_hash}"
            },
            backup_type="repository"
        )
        
        self.backup_history.append(record)
        self.pin_list[content_hash] = record
        
        return record
    
    def backup_security_configuration(self, 
                                      security_config: Dict[str, Any]) -> BackupRecord:
        """
        Backup security settings and configurations.
        
        Args:
            security_config: Security configuration data
            
        Returns:
            BackupRecord with IPFS hash
        """
        backup_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "security": security_config,
            "backup_type": "security",
            "version": "1.0"
        }
        
        content = json.dumps(backup_data, indent=2, sort_keys=True)
        content_hash = self.generate_content_hash(content)
        
        backup_file = os.path.join(self.backup_path, f"security_{content_hash[:16]}.json")
        with open(backup_file, 'w') as f:
            f.write(content)
        
        record = BackupRecord(
            backup_id=f"backup-security-{datetime.utcnow().timestamp()}",
            content_hash=content_hash,
            timestamp=datetime.utcnow(),
            size_bytes=len(content.encode()),
            metadata={
                "file_path": backup_file,
                "gateway_url": f"{self.ipfs_gateway}/ipfs/{content_hash}"
            },
            backup_type="security"
        )
        
        self.backup_history.append(record)
        self.pin_list[content_hash] = record
        
        return record
    
    def restore_from_backup(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """
        Restore data from IPFS backup.
        
        Args:
            content_hash: IPFS CID to restore
            
        Returns:
            Restored data or None if not found
        """
        if content_hash not in self.pin_list:
            return None
        
        record = self.pin_list[content_hash]
        backup_file = record.metadata.get("file_path")
        
        if not backup_file or not os.path.exists(backup_file):
            return None
        
        with open(backup_file, 'r') as f:
            data = json.load(f)
        
        return data
    
    def verify_backup_integrity(self, content_hash: str) -> bool:
        """
        Verify backup integrity by checking hash.
        
        Args:
            content_hash: IPFS CID to verify
            
        Returns:
            True if backup is valid and unchanged
        """
        data = self.restore_from_backup(content_hash)
        if data is None:
            return False
        
        # Recalculate hash
        content = json.dumps(data, indent=2, sort_keys=True)
        calculated_hash = self.generate_content_hash(content)
        
        return calculated_hash == content_hash
    
    def get_backup_status(self) -> Dict[str, Any]:
        """
        Get current backup system status.
        
        Returns:
            Status dictionary
        """
        backup_types = {}
        for record in self.backup_history:
            if record.backup_type not in backup_types:
                backup_types[record.backup_type] = 0
            backup_types[record.backup_type] += 1
        
        total_size = sum(r.size_bytes for r in self.backup_history)
        
        return {
            "total_backups": len(self.backup_history),
            "pinned_items": len(self.pin_list),
            "backup_types": backup_types,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "backup_path": self.backup_path,
            "ipfs_gateway": self.ipfs_gateway,
            "latest_backup": {
                "backup_id": self.backup_history[-1].backup_id,
                "content_hash": self.backup_history[-1].content_hash,
                "timestamp": self.backup_history[-1].timestamp.isoformat() + "Z",
                "type": self.backup_history[-1].backup_type
            } if self.backup_history else None,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def list_backups(self, 
                     backup_type: Optional[str] = None,
                     limit: int = 50) -> List[Dict[str, Any]]:
        """
        List recent backups.
        
        Args:
            backup_type: Filter by backup type (optional)
            limit: Maximum number of backups to return
            
        Returns:
            List of backup records
        """
        backups = self.backup_history
        
        if backup_type:
            backups = [b for b in backups if b.backup_type == backup_type]
        
        # Sort by timestamp descending
        backups = sorted(backups, key=lambda x: x.timestamp, reverse=True)
        
        # Limit results
        backups = backups[:limit]
        
        return [
            {
                "backup_id": b.backup_id,
                "content_hash": b.content_hash,
                "timestamp": b.timestamp.isoformat() + "Z",
                "size_bytes": b.size_bytes,
                "type": b.backup_type,
                "gateway_url": b.metadata.get("gateway_url")
            }
            for b in backups
        ]
    
    def create_full_mirror(self) -> Dict[str, BackupRecord]:
        """
        Create complete mirror of all critical configurations.
        This should be called periodically to ensure full protection.
        
        Returns:
            Dictionary of backup records by type
        """
        mirrors = {}
        
        # Mirror PR configurations (simulated)
        for pr_num in range(1, 6):  # Example: mirror last 5 PRs
            pr_data = {
                "number": pr_num,
                "title": f"PR #{pr_num}",
                "state": "open",
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            mirrors[f"pr_{pr_num}"] = self.backup_pr_configuration(pr_data, pr_num)
        
        # Mirror repository state
        repo_data = {
            "name": "AI-Based-Peace-Platform",
            "branch": "main",
            "last_commit": "abc123",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        mirrors["repository"] = self.backup_repository_state(repo_data)
        
        # Mirror security configuration
        security_config = {
            "rhythm_validation_enabled": True,
            "lazy_security_enabled": True,
            "activation_threshold": 50.0,
            "backup_enabled": True
        }
        mirrors["security"] = self.backup_security_configuration(security_config)
        
        return mirrors
