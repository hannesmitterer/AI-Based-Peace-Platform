"""
Test suite for wallet configuration module

This test suite validates the consolidated wallet configuration,
ensuring all wallets redirect correctly and the offering parameters
are properly configured.
"""

import pytest
import json
import os
import tempfile
from wallet_config import WalletConfig, WalletConfigError, get_active_wallet_address


class TestWalletConfiguration:
    """Test suite for wallet configuration functionality."""
    
    @pytest.fixture
    def wallet_config(self):
        """Fixture to provide a WalletConfig instance."""
        return WalletConfig()
    
    def test_config_loads_successfully(self, wallet_config):
        """Test that the configuration file loads without errors."""
        assert wallet_config.config is not None
        assert 'wallets' in wallet_config.config
        assert 'offering' in wallet_config.config
    
    def test_primary_wallet_address(self, wallet_config):
        """Test that the primary wallet has the correct address."""
        address = wallet_config.get_wallet_address('primary')
        assert address == '0x6c10692145718353070cc6cb5c21adf2073ffa1f'
    
    def test_primary_wallet_format(self, wallet_config):
        """Test that the primary wallet address has valid EVM format."""
        address = wallet_config.get_wallet_address('primary')
        assert address.startswith('0x')
        assert len(address) == 42
        # Check all characters are hexadecimal
        assert all(c in '0123456789abcdefABCDEF' for c in address[2:])
    
    def test_governance_audit_wallet_redirect(self, wallet_config):
        """Test that governance audit wallet redirects to primary."""
        address = wallet_config.get_wallet_address('governance_audit')
        primary_address = wallet_config.get_wallet_address('primary')
        assert address == primary_address
    
    def test_digital_bonds_wallet_redirect(self, wallet_config):
        """Test that digital bonds wallet redirects to primary."""
        address = wallet_config.get_wallet_address('digital_bonds')
        primary_address = wallet_config.get_wallet_address('primary')
        assert address == primary_address
    
    def test_all_wallets_resolve_to_same_address(self, wallet_config):
        """Test that all wallet types resolve to the same consolidated address."""
        primary_addr = wallet_config.get_wallet_address('primary')
        governance_addr = wallet_config.get_wallet_address('governance_audit')
        bonds_addr = wallet_config.get_wallet_address('digital_bonds')
        
        assert primary_addr == governance_addr == bonds_addr
    
    def test_is_wallet_consolidated(self, wallet_config):
        """Test wallet consolidation status detection."""
        assert not wallet_config.is_wallet_consolidated('primary')
        assert wallet_config.is_wallet_consolidated('governance_audit')
        assert wallet_config.is_wallet_consolidated('digital_bonds')
    
    def test_nonexistent_wallet_raises_error(self, wallet_config):
        """Test that requesting a non-existent wallet raises an error."""
        with pytest.raises(WalletConfigError):
            wallet_config.get_wallet_address('nonexistent_wallet')
    
    def test_offering_start_date(self, wallet_config):
        """Test that offering has the correct start date."""
        offering = wallet_config.get_offering_details()
        assert offering['startDate'] == '2025-12-01T00:00:00Z'
    
    def test_offering_fundraising_goal(self, wallet_config):
        """Test that offering has the correct fundraising goal."""
        offering = wallet_config.get_offering_details()
        assert offering['fundraisingGoal'] == 5000000
    
    def test_offering_status(self, wallet_config):
        """Test that offering status is pending confirmation."""
        offering = wallet_config.get_offering_details()
        assert offering['status'] == 'pending_final_confirmation'
    
    def test_pending_confirmations_exist(self, wallet_config):
        """Test that pending confirmations are listed."""
        confirmations = wallet_config.get_pending_confirmations()
        assert len(confirmations) == 3
        assert 'chain/network selection' in confirmations
        assert 'fundraising asset selection' in confirmations
        assert 'asset decimals configuration' in confirmations
    
    def test_post_merge_actions_exist(self, wallet_config):
        """Test that post-merge actions are defined."""
        actions = wallet_config.get_post_merge_actions()
        assert len(actions) > 0
        # Check that actions have required fields
        for action in actions:
            assert 'priority' in action
            assert 'action' in action
            assert 'description' in action
            assert 'status' in action
    
    def test_configuration_validates_successfully(self, wallet_config):
        """Test that the configuration passes validation."""
        assert wallet_config.validate_configuration() is True
    
    def test_get_active_wallet_address_convenience_function(self):
        """Test the convenience function for getting active wallet address."""
        address = get_active_wallet_address()
        assert address == '0x6c10692145718353070cc6cb5c21adf2073ffa1f'
    
    def test_get_primary_wallet(self, wallet_config):
        """Test retrieving the full primary wallet configuration."""
        primary = wallet_config.get_primary_wallet()
        assert primary['address'] == '0x6c10692145718353070cc6cb5c21adf2073ffa1f'
        assert primary['type'] == 'EVM'
        assert 'investment_collection' in primary['purposes']
        assert 'governance_audit' in primary['purposes']
        assert 'digital_bonds' in primary['purposes']


class TestWalletConfigurationValidation:
    """Test suite for wallet configuration validation."""
    
    @pytest.fixture
    def temp_config(self):
        """Fixture to create and cleanup temporary config files."""
        temp_files = []
        
        def create_config(config_data):
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
            json.dump(config_data, temp_file)
            temp_file.close()
            temp_files.append(temp_file.name)
            return temp_file.name
        
        yield create_config
        
        # Cleanup all temp files
        for temp_path in temp_files:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass
    
    def test_invalid_wallet_address_format(self, temp_config):
        """Test validation fails with invalid address format."""
        config_data = {
            "wallets": {
                "primary": {
                    "address": "invalid_address",
                    "type": "EVM"
                }
            },
            "offering": {}
        }
        temp_path = temp_config(config_data)
        
        config = WalletConfig(temp_path)
        with pytest.raises(WalletConfigError, match="Invalid EVM address"):
            config.validate_configuration()
    
    def test_missing_primary_wallet(self, temp_config):
        """Test validation fails when primary wallet is missing."""
        config_data = {
            "wallets": {},
            "offering": {}
        }
        temp_path = temp_config(config_data)
        
        config = WalletConfig(temp_path)
        with pytest.raises(WalletConfigError, match="Primary wallet not found"):
            config.validate_configuration()
    
    def test_invalid_redirect_target(self, temp_config):
        """Test validation fails when redirect target doesn't exist."""
        config_data = {
            "wallets": {
                "primary": {
                    "address": "0x6c10692145718353070cc6cb5c21adf2073ffa1f",
                    "type": "EVM"
                },
                "governance_audit": {
                    "redirectTo": "nonexistent_wallet"
                }
            },
            "offering": {}
        }
        temp_path = temp_config(config_data)
        
        config = WalletConfig(temp_path)
        with pytest.raises(WalletConfigError, match="redirects to non-existent wallet"):
            config.validate_configuration()
    
    def test_invalid_fundraising_goal(self, temp_config):
        """Test validation fails with invalid fundraising goal."""
        config_data = {
            "wallets": {
                "primary": {
                    "address": "0x6c10692145718353070cc6cb5c21adf2073ffa1f",
                    "type": "EVM"
                }
            },
            "offering": {
                "fundraisingGoal": -1000
            }
        }
        temp_path = temp_config(config_data)
        
        config = WalletConfig(temp_path)
        with pytest.raises(WalletConfigError, match="Invalid fundraising goal"):
            config.validate_configuration()
    
    def test_invalid_start_date_format(self, temp_config):
        """Test validation fails with invalid start date format."""
        config_data = {
            "wallets": {
                "primary": {
                    "address": "0x6c10692145718353070cc6cb5c21adf2073ffa1f",
                    "type": "EVM"
                }
            },
            "offering": {
                "startDate": "invalid-date-format"
            }
        }
        temp_path = temp_config(config_data)
        
        config = WalletConfig(temp_path)
        with pytest.raises(WalletConfigError, match="Invalid offering start date format"):
            config.validate_configuration()
    
    def test_circular_redirect_detection(self, temp_config):
        """Test that circular redirects are detected and prevented."""
        config_data = {
            "wallets": {
                "primary": {
                    "address": "0x6c10692145718353070cc6cb5c21adf2073ffa1f",
                    "type": "EVM"
                },
                "wallet_a": {
                    "redirectTo": "wallet_b"
                },
                "wallet_b": {
                    "redirectTo": "wallet_a"
                }
            },
            "offering": {}
        }
        temp_path = temp_config(config_data)
        
        config = WalletConfig(temp_path)
        with pytest.raises(WalletConfigError, match="Circular redirect detected"):
            config.get_wallet_address('wallet_a')


class TestWalletConfigIntegration:
    """Integration tests for wallet configuration."""
    
    def test_consolidated_wallets_have_same_purposes(self):
        """Test that consolidated wallets serve their original purposes through primary."""
        config = WalletConfig()
        primary = config.get_primary_wallet()
        
        # Verify that primary wallet includes purposes of consolidated wallets
        assert 'governance_audit' in primary['purposes']
        assert 'digital_bonds' in primary['purposes']
        assert 'investment_collection' in primary['purposes']
    
    def test_audit_trail_records_consolidation(self):
        """Test that audit trail records the consolidation event."""
        config = WalletConfig()
        audit_trail = config.config.get('auditTrail', [])
        
        assert len(audit_trail) > 0
        initial_consolidation = audit_trail[0]
        assert 'consolidation' in initial_consolidation['action'].lower()
        assert 'primary' in initial_consolidation['affectedWallets']
    
    def test_all_post_merge_actions_have_pending_status(self):
        """Test that all post-merge actions are initially pending."""
        config = WalletConfig()
        actions = config.get_post_merge_actions()
        
        for action in actions:
            assert action['status'] == 'pending'


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
