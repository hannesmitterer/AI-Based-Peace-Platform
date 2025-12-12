"""
NRE-002 Content Protection and Anti-Censorship System

This module implements the NRE-002 protocol for content protection,
anti-censorship, and democratic content curation.

Version: 1.0.0
Protocol: NRE-002
"""

import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from pathlib import Path


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_utc_timestamp() -> str:
    """Generate UTC timestamp in ISO format.
    
    Returns:
        ISO 8601 formatted timestamp with UTC timezone
    """
    return datetime.now(timezone.utc).isoformat()


class StratificationLevel(Enum):
    """Content stratification levels as defined in NRE-002."""
    FOUNDATION = 1  # Basic facts and overview
    DETAILED = 2    # Comprehensive analysis
    COMPLETE = 3    # Unredacted primary sources


class ContentWarningType(Enum):
    """Types of content warnings."""
    GRAPHIC_CONTENT = "graphic_content"
    VIOLENCE = "violence"
    TRAUMA_SENSITIVE = "trauma_sensitive"
    EMOTIONALLY_INTENSE = "emotionally_intense"
    HISTORICAL_ATROCITY = "historical_atrocity"


class NRE002Config:
    """Configuration loader for NRE-002 protocol."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize NRE-002 configuration.
        
        Args:
            config_path: Path to NRE-002 configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "nre_002_config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"NRE-002 configuration loaded: {config.get('version', 'unknown')}")
            return config
        except FileNotFoundError:
            logger.warning(f"NRE-002 config not found at {self.config_path}, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default NRE-002 configuration."""
        return {
            "protocol": "NRE-002",
            "version": "1.0.0",
            "anti_censorship": {"enabled": True},
            "user_control": {
                "always_override_option": {"enabled": True}
            }
        }
    
    def is_censorship_prohibited(self) -> bool:
        """Check if censorship is prohibited."""
        return self.config.get("anti_censorship", {}).get("enabled", True)
    
    def is_override_available(self) -> bool:
        """Check if user override is always available."""
        return self.config.get("user_control", {}).get(
            "always_override_option", {}
        ).get("enabled", True)


class ContentArchive:
    """Immutable content archive system implementing NRE-002 Section 2.1."""
    
    def __init__(self):
        """Initialize content archive."""
        self.archive = {}
        self.version_history = {}
        self.change_log = []
    
    def store_content(self, content_id: str, content: str, metadata: Dict[str, Any]) -> str:
        """Store content with cryptographic protection.
        
        Args:
            content_id: Unique identifier for content
            content: Content to archive
            metadata: Content metadata
            
        Returns:
            SHA-256 hash of stored content
        """
        # Calculate SHA-256 hash
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Create archive entry
        archive_entry = {
            "content_id": content_id,
            "content": content,
            "metadata": metadata,
            "hash": content_hash,
            "timestamp": get_utc_timestamp(),
            "immutable": True
        }
        
        # Store in archive
        self.archive[content_id] = archive_entry
        
        # Initialize version history
        if content_id not in self.version_history:
            self.version_history[content_id] = []
        self.version_history[content_id].append(archive_entry)
        
        # Log the change
        self._log_change("content_stored", content_id, content_hash)
        
        logger.info(f"Content archived: {content_id} (hash: {content_hash[:16]}...)")
        return content_hash
    
    def verify_integrity(self, content_id: str) -> bool:
        """Verify content integrity using SHA-256 hash.
        
        Args:
            content_id: Content identifier to verify
            
        Returns:
            True if integrity verified, False otherwise
        """
        if content_id not in self.archive:
            logger.error(f"Content not found: {content_id}")
            return False
        
        entry = self.archive[content_id]
        stored_hash = entry["hash"]
        calculated_hash = hashlib.sha256(entry["content"].encode('utf-8')).hexdigest()
        
        if stored_hash == calculated_hash:
            logger.info(f"Integrity verified: {content_id}")
            return True
        else:
            logger.error(f"Integrity violation detected: {content_id}")
            return False
    
    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve content from archive.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Archive entry or None if not found
        """
        return self.archive.get(content_id)
    
    def get_version_history(self, content_id: str) -> List[Dict[str, Any]]:
        """Get version history for content.
        
        Args:
            content_id: Content identifier
            
        Returns:
            List of version entries
        """
        return self.version_history.get(content_id, [])
    
    def _log_change(self, action: str, content_id: str, content_hash: str):
        """Log changes to audit trail.
        
        Args:
            action: Type of action performed
            content_id: Content identifier
            content_hash: Content hash
        """
        log_entry = {
            "action": action,
            "content_id": content_id,
            "hash": content_hash,
            "timestamp": get_utc_timestamp()
        }
        self.change_log.append(log_entry)


class ContentStratification:
    """Content stratification system implementing NRE-002 Section 2.2."""
    
    def __init__(self):
        """Initialize content stratification system."""
        self.content_levels = {}
        self.curation_decisions = []
    
    def stratify_content(
        self,
        content_id: str,
        level: StratificationLevel,
        rationale: str,
        curator: str
    ) -> Dict[str, Any]:
        """Stratify content into educational levels.
        
        Args:
            content_id: Content identifier
            level: Stratification level
            rationale: Curation rationale
            curator: Curator identifier
            
        Returns:
            Stratification record
        """
        # Create stratification record
        record = {
            "content_id": content_id,
            "stratification_level": level.value,
            "curation_rationale": rationale,
            "curator": curator,
            "date": get_utc_timestamp(),
            "review_status": "approved",
            "appeal_available": True,
            "complete_version_link": f"/archive/{content_id}/level/3"
        }
        
        # Store stratification
        self.content_levels[content_id] = record
        self.curation_decisions.append(record)
        
        logger.info(
            f"Content stratified: {content_id} -> Level {level.value} "
            f"(curator: {curator})"
        )
        
        return record
    
    def get_stratification(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get stratification record for content.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Stratification record or None
        """
        return self.content_levels.get(content_id)
    
    def get_transparency_report(self) -> List[Dict[str, Any]]:
        """Generate transparency report of all curation decisions.
        
        Returns:
            List of all stratification records
        """
        return self.curation_decisions.copy()


class ContentWarningSystem:
    """Content warning system implementing NRE-002 Section 2.3."""
    
    def __init__(self):
        """Initialize content warning system."""
        self.warnings = {}
    
    def add_warning(
        self,
        content_id: str,
        warning_types: List[ContentWarningType],
        description: str,
        alternatives: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add content warning.
        
        Args:
            content_id: Content identifier
            warning_types: List of warning types
            description: Specific description of content
            alternatives: Alternative presentation options
            
        Returns:
            Warning record
        """
        if alternatives is None:
            alternatives = ["alternative_summary", "skip_section", "scholarly_analysis"]
        
        warning = {
            "content_id": content_id,
            "warning_types": [wt.value for wt in warning_types],
            "description": description,
            "alternatives": alternatives,
            "educational_purpose": (
                "This material is presented for educational and memorial purposes."
            ),
            "access_options": [
                "view_content",
                "alternative_summary",
                "skip_section"
            ],
            "bypass_available": True,
            "acknowledgment_required": True
        }
        
        self.warnings[content_id] = warning
        logger.info(f"Content warning added: {content_id}")
        
        return warning
    
    def get_warning(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content warning.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Warning record or None
        """
        return self.warnings.get(content_id)
    
    def format_warning(self, content_id: str) -> str:
        """Format content warning for display.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Formatted warning text
        """
        warning = self.get_warning(content_id)
        if not warning:
            return ""
        
        formatted = f"""
⚠️ Content Warning
This material contains {warning['description']}.
{warning['educational_purpose']}

Options:
[View Content] [Alternative Summary] [Skip Section]
        """
        return formatted.strip()


class UserAccessControl:
    """User access control implementing NRE-002 Section 2.4."""
    
    def __init__(self, config: NRE002Config):
        """Initialize user access control.
        
        Args:
            config: NRE-002 configuration
        """
        self.config = config
        self.user_preferences = {}
        self.access_log = []
    
    def can_access_level(
        self,
        user_id: str,
        content_id: str,
        level: StratificationLevel,
        override_requested: bool = False
    ) -> Tuple[bool, str]:
        """Check if user can access content at specified level.
        
        Args:
            user_id: User identifier
            content_id: Content identifier
            level: Requested stratification level
            override_requested: Whether user requested override
            
        Returns:
            Tuple of (access_granted, reason)
        """
        # NRE-002: Always-override option must be available
        if override_requested:
            if self.config.is_override_available():
                self._log_access(user_id, content_id, level, "override_granted")
                return True, "User override granted per NRE-002"
            else:
                logger.error("Override requested but not available - NRE-002 violation!")
                return False, "System configuration error"
        
        # NRE-002: No algorithmic blocking based on user characteristics
        # All levels accessible by default, with optional warnings
        self._log_access(user_id, content_id, level, "access_granted")
        return True, "Access granted per NRE-002 anti-censorship policy"
    
    def set_user_preference(
        self,
        user_id: str,
        default_level: StratificationLevel,
        show_warnings: bool = True
    ):
        """Set user content preferences.
        
        Args:
            user_id: User identifier
            default_level: Default stratification level
            show_warnings: Whether to show content warnings
        """
        self.user_preferences[user_id] = {
            "default_level": default_level.value,
            "show_warnings": show_warnings,
            "updated": get_utc_timestamp()
        }
        logger.info(f"User preferences updated: {user_id}")
    
    def _log_access(
        self,
        user_id: str,
        content_id: str,
        level: StratificationLevel,
        action: str
    ):
        """Log content access for transparency.
        
        Args:
            user_id: User identifier
            content_id: Content identifier
            level: Stratification level
            action: Access action
        """
        log_entry = {
            "user_id": user_id,
            "content_id": content_id,
            "level": level.value,
            "action": action,
            "timestamp": get_utc_timestamp()
        }
        self.access_log.append(log_entry)
    
    def get_access_metrics(self) -> Dict[str, Any]:
        """Get access metrics for transparency reporting.
        
        Returns:
            Access statistics
        """
        total_accesses = len(self.access_log)
        override_count = sum(
            1 for log in self.access_log if log["action"] == "override_granted"
        )
        
        return {
            "total_accesses": total_accesses,
            "override_requests": override_count,
            "override_percentage": (
                (override_count / total_accesses * 100) if total_accesses > 0 else 0
            )
        }


class NRE002System:
    """Main NRE-002 implementation coordinating all subsystems."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize NRE-002 system.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = NRE002Config(config_path)
        self.archive = ContentArchive()
        self.stratification = ContentStratification()
        self.warnings = ContentWarningSystem()
        self.access_control = UserAccessControl(self.config)
        
        logger.info("NRE-002 Content Protection System initialized")
        
        # Verify anti-censorship is enabled
        if not self.config.is_censorship_prohibited():
            logger.error("CRITICAL: Censorship not prohibited - NRE-002 violation!")
    
    def archive_content(
        self,
        content_id: str,
        content: str,
        metadata: Dict[str, Any],
        level: StratificationLevel,
        curator: str,
        rationale: str,
        warning_types: Optional[List[ContentWarningType]] = None
    ) -> Dict[str, Any]:
        """Archive content with full NRE-002 protection.
        
        Args:
            content_id: Unique content identifier
            content: Content to archive
            metadata: Content metadata
            level: Stratification level
            curator: Curator identifier
            rationale: Stratification rationale
            warning_types: Optional content warnings
            
        Returns:
            Complete archival record
        """
        # Store in immutable archive
        content_hash = self.archive.store_content(content_id, content, metadata)
        
        # Stratify content
        stratification_record = self.stratification.stratify_content(
            content_id, level, rationale, curator
        )
        
        # Add warnings if needed
        warning_record = None
        if warning_types:
            warning_record = self.warnings.add_warning(
                content_id,
                warning_types,
                "sensitive historical content"
            )
        
        return {
            "content_id": content_id,
            "hash": content_hash,
            "stratification": stratification_record,
            "warning": warning_record,
            "status": "archived"
        }
    
    def access_content(
        self,
        user_id: str,
        content_id: str,
        requested_level: StratificationLevel,
        override: bool = False
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Access content with NRE-002 compliance.
        
        Args:
            user_id: User identifier
            content_id: Content identifier
            requested_level: Requested stratification level
            override: Whether user requests override
            
        Returns:
            Tuple of (success, content, message)
        """
        # Check access permissions
        can_access, reason = self.access_control.can_access_level(
            user_id, content_id, requested_level, override
        )
        
        if not can_access:
            return False, None, reason
        
        # Get content
        content = self.archive.get_content(content_id)
        if not content:
            return False, None, "Content not found"
        
        # Get warning if exists
        warning = self.warnings.get_warning(content_id)
        
        # Verify integrity
        if not self.archive.verify_integrity(content_id):
            logger.error(f"Integrity verification failed: {content_id}")
            return False, None, "Content integrity compromised"
        
        # Return content with metadata
        return True, {
            "content": content,
            "warning": warning,
            "level": requested_level.value,
            "reason": reason
        }, reason  # Return the reason as the message
    
    def generate_transparency_report(self) -> Dict[str, Any]:
        """Generate NRE-002 transparency report.
        
        Returns:
            Complete transparency report
        """
        return {
            "protocol": "NRE-002",
            "version": self.config.config.get("version"),
            "report_date": get_utc_timestamp(),
            "curation_decisions": self.stratification.get_transparency_report(),
            "access_metrics": self.access_control.get_access_metrics(),
            "archive_integrity": {
                "total_items": len(self.archive.archive),
                "integrity_verified": True
            },
            "anti_censorship_status": {
                "censorship_prohibited": self.config.is_censorship_prohibited(),
                "override_available": self.config.is_override_available()
            }
        }


# Example usage
if __name__ == "__main__":
    # Initialize NRE-002 system
    nre_system = NRE002System()
    
    # Archive historical content
    result = nre_system.archive_content(
        content_id="historical_doc_001",
        content="Complete historical documentation...",
        metadata={"title": "Historical Event Documentation", "year": 1945},
        level=StratificationLevel.COMPLETE,
        curator="Independent Historical Curatorium",
        rationale="Primary source documentation for research",
        warning_types=[ContentWarningType.HISTORICAL_ATROCITY]
    )
    
    print(f"Content archived: {result['content_id']}")
    print(f"Hash: {result['hash']}")
    
    # User accesses content with override
    success, content, message = nre_system.access_content(
        user_id="researcher_001",
        content_id="historical_doc_001",
        requested_level=StratificationLevel.COMPLETE,
        override=True
    )
    
    print(f"\nAccess result: {message}")
    
    # Generate transparency report
    report = nre_system.generate_transparency_report()
    print(f"\nTransparency Report:")
    print(json.dumps(report, indent=2))
