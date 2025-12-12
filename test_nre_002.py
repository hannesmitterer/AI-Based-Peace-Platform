"""
Test suite for NRE-002 Content Protection and Anti-Censorship System

This test suite validates the NRE-002 protocol implementation,
ensuring anti-censorship guarantees, archive integrity, content
stratification, and user control mechanisms.
"""

import pytest
import json
import hashlib
from datetime import datetime
from nre_002_system import (
    NRE002System,
    NRE002Config,
    ContentArchive,
    ContentStratification,
    ContentWarningSystem,
    UserAccessControl,
    StratificationLevel,
    ContentWarningType
)


class TestNRE002Config:
    """Test suite for NRE-002 configuration."""
    
    @pytest.fixture
    def config(self):
        """Fixture to provide NRE002Config instance."""
        return NRE002Config()
    
    def test_config_loads_successfully(self, config):
        """Test that configuration loads without errors."""
        assert config.config is not None
        assert config.config.get('protocol') == 'NRE-002'
    
    def test_censorship_prohibited(self, config):
        """Test that censorship is prohibited by configuration."""
        assert config.is_censorship_prohibited() is True
    
    def test_override_always_available(self, config):
        """Test that user override is always available."""
        assert config.is_override_available() is True


class TestContentArchive:
    """Test suite for immutable content archive."""
    
    @pytest.fixture
    def archive(self):
        """Fixture to provide ContentArchive instance."""
        return ContentArchive()
    
    def test_store_content(self, archive):
        """Test storing content with cryptographic protection."""
        content = "Historical documentation content"
        metadata = {"title": "Test Document", "year": 1945}
        
        content_hash = archive.store_content("test_001", content, metadata)
        
        assert content_hash is not None
        assert len(content_hash) == 64  # SHA-256 produces 64 hex characters
        assert content_hash == hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def test_verify_integrity_success(self, archive):
        """Test successful integrity verification."""
        content = "Test content"
        archive.store_content("test_002", content, {})
        
        assert archive.verify_integrity("test_002") is True
    
    def test_verify_integrity_missing_content(self, archive):
        """Test integrity verification fails for missing content."""
        assert archive.verify_integrity("nonexistent") is False
    
    def test_get_content(self, archive):
        """Test retrieving archived content."""
        content = "Test content"
        metadata = {"test": "metadata"}
        archive.store_content("test_003", content, metadata)
        
        retrieved = archive.get_content("test_003")
        
        assert retrieved is not None
        assert retrieved['content'] == content
        assert retrieved['metadata'] == metadata
        assert retrieved['immutable'] is True
    
    def test_version_history(self, archive):
        """Test version history tracking."""
        archive.store_content("test_004", "Initial content", {})
        
        history = archive.get_version_history("test_004")
        
        assert len(history) == 1
        assert history[0]['content'] == "Initial content"
    
    def test_change_logging(self, archive):
        """Test that all changes are logged."""
        archive.store_content("test_005", "Content", {})
        
        assert len(archive.change_log) > 0
        assert archive.change_log[-1]['action'] == "content_stored"
        assert archive.change_log[-1]['content_id'] == "test_005"


class TestContentStratification:
    """Test suite for content stratification system."""
    
    @pytest.fixture
    def stratification(self):
        """Fixture to provide ContentStratification instance."""
        return ContentStratification()
    
    def test_stratify_content(self, stratification):
        """Test content stratification."""
        record = stratification.stratify_content(
            "content_001",
            StratificationLevel.COMPLETE,
            "Primary source documentation",
            "Independent Historical Curatorium"
        )
        
        assert record['content_id'] == "content_001"
        assert record['stratification_level'] == 3
        assert record['appeal_available'] is True
        assert 'complete_version_link' in record
    
    def test_get_stratification(self, stratification):
        """Test retrieving stratification record."""
        stratification.stratify_content(
            "content_002",
            StratificationLevel.DETAILED,
            "Academic content",
            "Curator"
        )
        
        record = stratification.get_stratification("content_002")
        
        assert record is not None
        assert record['stratification_level'] == 2
    
    def test_transparency_report(self, stratification):
        """Test transparency report generation."""
        stratification.stratify_content(
            "content_003",
            StratificationLevel.FOUNDATION,
            "General audience",
            "Curator"
        )
        
        report = stratification.get_transparency_report()
        
        assert len(report) == 1
        assert report[0]['content_id'] == "content_003"


class TestContentWarningSystem:
    """Test suite for content warning system."""
    
    @pytest.fixture
    def warnings(self):
        """Fixture to provide ContentWarningSystem instance."""
        return ContentWarningSystem()
    
    def test_add_warning(self, warnings):
        """Test adding content warning."""
        warning = warnings.add_warning(
            "content_001",
            [ContentWarningType.GRAPHIC_CONTENT, ContentWarningType.VIOLENCE],
            "graphic violence"
        )
        
        assert warning['content_id'] == "content_001"
        assert len(warning['warning_types']) == 2
        assert warning['bypass_available'] is True
        assert warning['acknowledgment_required'] is True
    
    def test_get_warning(self, warnings):
        """Test retrieving content warning."""
        warnings.add_warning(
            "content_002",
            [ContentWarningType.TRAUMA_SENSITIVE],
            "sensitive content"
        )
        
        warning = warnings.get_warning("content_002")
        
        assert warning is not None
        assert ContentWarningType.TRAUMA_SENSITIVE.value in warning['warning_types']
    
    def test_format_warning(self, warnings):
        """Test warning formatting for display."""
        warnings.add_warning(
            "content_003",
            [ContentWarningType.HISTORICAL_ATROCITY],
            "historical violence"
        )
        
        formatted = warnings.format_warning("content_003")
        
        assert "⚠️ Content Warning" in formatted
        assert "historical violence" in formatted
        assert "[View Content]" in formatted
        assert "[Alternative Summary]" in formatted


class TestUserAccessControl:
    """Test suite for user access control."""
    
    @pytest.fixture
    def config(self):
        """Fixture to provide NRE002Config."""
        return NRE002Config()
    
    @pytest.fixture
    def access_control(self, config):
        """Fixture to provide UserAccessControl instance."""
        return UserAccessControl(config)
    
    def test_access_with_override(self, access_control):
        """Test that override always grants access (NRE-002 requirement)."""
        can_access, reason = access_control.can_access_level(
            "user_001",
            "content_001",
            StratificationLevel.COMPLETE,
            override_requested=True
        )
        
        assert can_access is True
        assert "NRE-002" in reason
    
    def test_access_without_override(self, access_control):
        """Test normal access follows anti-censorship policy."""
        can_access, reason = access_control.can_access_level(
            "user_002",
            "content_002",
            StratificationLevel.DETAILED,
            override_requested=False
        )
        
        # NRE-002: No algorithmic blocking
        assert can_access is True
        assert "anti-censorship" in reason
    
    def test_set_user_preference(self, access_control):
        """Test setting user content preferences."""
        access_control.set_user_preference(
            "user_003",
            StratificationLevel.FOUNDATION,
            show_warnings=True
        )
        
        prefs = access_control.user_preferences["user_003"]
        assert prefs['default_level'] == 1
        assert prefs['show_warnings'] is True
    
    def test_access_logging(self, access_control):
        """Test that access is logged for transparency."""
        access_control.can_access_level(
            "user_004",
            "content_004",
            StratificationLevel.COMPLETE,
            override_requested=False
        )
        
        assert len(access_control.access_log) > 0
        assert access_control.access_log[-1]['user_id'] == "user_004"
    
    def test_get_access_metrics(self, access_control):
        """Test access metrics for transparency reporting."""
        # Normal access
        access_control.can_access_level(
            "user_005", "content_005", StratificationLevel.FOUNDATION, False
        )
        # Override access
        access_control.can_access_level(
            "user_006", "content_006", StratificationLevel.COMPLETE, True
        )
        
        metrics = access_control.get_access_metrics()
        
        assert metrics['total_accesses'] == 2
        assert metrics['override_requests'] == 1
        assert metrics['override_percentage'] == 50.0


class TestNRE002System:
    """Integration test suite for complete NRE-002 system."""
    
    @pytest.fixture
    def system(self):
        """Fixture to provide NRE002System instance."""
        return NRE002System()
    
    def test_system_initialization(self, system):
        """Test that NRE-002 system initializes correctly."""
        assert system.config is not None
        assert system.archive is not None
        assert system.stratification is not None
        assert system.warnings is not None
        assert system.access_control is not None
    
    def test_archive_content_complete_workflow(self, system):
        """Test complete content archival workflow."""
        result = system.archive_content(
            content_id="integration_001",
            content="Historical documentation",
            metadata={"title": "Test", "year": 1945},
            level=StratificationLevel.COMPLETE,
            curator="Test Curator",
            rationale="Testing purposes",
            warning_types=[ContentWarningType.HISTORICAL_ATROCITY]
        )
        
        assert result['content_id'] == "integration_001"
        assert result['hash'] is not None
        assert result['stratification'] is not None
        assert result['warning'] is not None
        assert result['status'] == "archived"
    
    def test_access_content_with_override(self, system):
        """Test content access with user override."""
        # First archive content
        system.archive_content(
            "integration_002",
            "Complete content",
            {},
            StratificationLevel.COMPLETE,
            "Curator",
            "Test"
        )
        
        # Then access with override
        success, content, message = system.access_content(
            "user_001",
            "integration_002",
            StratificationLevel.COMPLETE,
            override=True
        )
        
        assert success is True
        assert content is not None
        assert "NRE-002" in message
    
    def test_access_content_normal(self, system):
        """Test normal content access."""
        system.archive_content(
            "integration_003",
            "Test content",
            {},
            StratificationLevel.FOUNDATION,
            "Curator",
            "Test"
        )
        
        success, content, message = system.access_content(
            "user_002",
            "integration_003",
            StratificationLevel.FOUNDATION,
            override=False
        )
        
        assert success is True
        assert content is not None
    
    def test_access_nonexistent_content(self, system):
        """Test accessing nonexistent content fails gracefully."""
        success, content, message = system.access_content(
            "user_003",
            "nonexistent",
            StratificationLevel.FOUNDATION,
            override=False
        )
        
        assert success is False
        assert content is None
        assert "not found" in message
    
    def test_integrity_verification_in_access(self, system):
        """Test that content access includes integrity verification."""
        system.archive_content(
            "integration_004",
            "Content to verify",
            {},
            StratificationLevel.DETAILED,
            "Curator",
            "Test"
        )
        
        success, content, message = system.access_content(
            "user_004",
            "integration_004",
            StratificationLevel.DETAILED,
            override=False
        )
        
        # Should succeed because integrity is valid
        assert success is True
    
    def test_generate_transparency_report(self, system):
        """Test transparency report generation."""
        # Archive some content
        system.archive_content(
            "integration_005",
            "Content",
            {},
            StratificationLevel.FOUNDATION,
            "Curator",
            "Test"
        )
        
        # Access it
        system.access_content(
            "user_005",
            "integration_005",
            StratificationLevel.FOUNDATION,
            override=False
        )
        
        # Generate report
        report = system.generate_transparency_report()
        
        assert report['protocol'] == "NRE-002"
        assert 'version' in report
        assert 'curation_decisions' in report
        assert 'access_metrics' in report
        assert 'archive_integrity' in report
        assert 'anti_censorship_status' in report
        
        # Verify anti-censorship status
        assert report['anti_censorship_status']['censorship_prohibited'] is True
        assert report['anti_censorship_status']['override_available'] is True


class TestAntiCensorshipCompliance:
    """Test suite specifically for anti-censorship compliance."""
    
    @pytest.fixture
    def system(self):
        """Fixture to provide NRE002System instance."""
        return NRE002System()
    
    def test_no_age_based_blocking(self, system):
        """Test that access is not blocked based on user age."""
        # This is a critical NRE-002 requirement
        system.archive_content(
            "sensitive_001",
            "Sensitive content",
            {},
            StratificationLevel.COMPLETE,
            "Curator",
            "Test"
        )
        
        # Even with a hypothetical "young user", access should be granted
        # (with override or through anti-censorship policy)
        success, _, message = system.access_content(
            "young_user",
            "sensitive_001",
            StratificationLevel.COMPLETE,
            override=True
        )
        
        assert success is True
    
    def test_no_profile_based_blocking(self, system):
        """Test that access is not blocked based on user profile."""
        system.archive_content(
            "sensitive_002",
            "Content",
            {},
            StratificationLevel.COMPLETE,
            "Curator",
            "Test"
        )
        
        # All user types should have access
        for user in ["student", "researcher", "general_public", "educator"]:
            success, _, _ = system.access_content(
                user,
                "sensitive_002",
                StratificationLevel.COMPLETE,
                override=False
            )
            assert success is True, f"Access denied for {user} - NRE-002 violation!"
    
    def test_override_always_works(self, system):
        """Test that user override always grants access."""
        system.archive_content(
            "sensitive_003",
            "Content",
            {},
            StratificationLevel.COMPLETE,
            "Curator",
            "Test",
            warning_types=[ContentWarningType.GRAPHIC_CONTENT]
        )
        
        # Override should ALWAYS work, regardless of any other factors
        for i in range(10):
            success, _, message = system.access_content(
                f"user_{i}",
                "sensitive_003",
                StratificationLevel.COMPLETE,
                override=True
            )
            assert success is True
            assert "override" in message.lower() or "nre-002" in message.lower()
    
    def test_complete_level_always_accessible(self, system):
        """Test that Level 3 (Complete) is always accessible."""
        system.archive_content(
            "complete_001",
            "Complete unredacted content",
            {},
            StratificationLevel.COMPLETE,
            "Curator",
            "Test"
        )
        
        # Access to complete level with override must always work
        success, content, _ = system.access_content(
            "any_user",
            "complete_001",
            StratificationLevel.COMPLETE,
            override=True
        )
        
        assert success is True
        assert content is not None
        assert content['level'] == 3


class TestArchiveIntegrity:
    """Test suite for archive integrity features."""
    
    @pytest.fixture
    def archive(self):
        """Fixture to provide ContentArchive instance."""
        return ContentArchive()
    
    def test_content_immutable(self, archive):
        """Test that archived content cannot be modified."""
        content = "Original content"
        archive.store_content("immutable_001", content, {})
        
        # Attempting to modify should not affect archived content
        entry = archive.get_content("immutable_001")
        assert entry['immutable'] is True
        assert entry['content'] == "Original content"
    
    def test_hash_verification(self, archive):
        """Test cryptographic hash verification."""
        content = "Test content for hashing"
        hash1 = archive.store_content("hash_001", content, {})
        
        # Verify hash matches expected SHA-256
        expected_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        assert hash1 == expected_hash
    
    def test_timestamp_recorded(self, archive):
        """Test that timestamps are recorded for all operations."""
        archive.store_content("timestamp_001", "Content", {})
        
        entry = archive.get_content("timestamp_001")
        assert 'timestamp' in entry
        # Verify timestamp is ISO format with Z
        assert entry['timestamp'].endswith('Z')


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
