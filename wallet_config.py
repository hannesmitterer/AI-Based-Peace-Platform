"""
Wallet Configuration Module for AI-Based Peace Platform

This module provides utilities to load and validate the consolidated wallet configuration.
It ensures that wallet operations use the correct addresses and parameters.
"""

import json
import os
from typing import Dict, Optional, List
from datetime import datetime


class WalletConfigError(Exception):
    """Custom exception for wallet configuration errors."""
    pass


class WalletConfig:
    """
    Manages wallet configuration for the AI-Based Peace Platform.
    
    This class handles the consolidated wallet structure where multiple
    wallet types (governance audit, digital bonds) are redirected to a
    single primary EVM wallet for simplified operations and audit efficiency.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the wallet configuration.
        
        Args:
            config_path: Path to the wallets.json configuration file.
                        If None, uses default path relative to this module.
        """
        if config_path is None:
            # Default to config/wallets.json relative to repository root
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, 'config', 'wallets.json')
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load the wallet configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise WalletConfigError(f"Wallet configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise WalletConfigError(f"Invalid JSON in wallet configuration: {e}")
    
    def get_wallet_address(self, wallet_name: str, _visited: Optional[set] = None) -> str:
        """
        Get the active wallet address for a given wallet name.
        
        For consolidated wallets, this follows the redirect to the primary wallet.
        
        Args:
            wallet_name: Name of the wallet (e.g., 'primary', 'governance_audit', 'digital_bonds')
            _visited: Internal parameter for cycle detection (do not use)
        
        Returns:
            The EVM wallet address
        
        Raises:
            WalletConfigError: If wallet is not found or configuration is invalid
        """
        if _visited is None:
            _visited = set()
        
        if wallet_name in _visited:
            raise WalletConfigError(f"Circular redirect detected: {' -> '.join(_visited)} -> {wallet_name}")
        
        if wallet_name not in self.config.get('wallets', {}):
            raise WalletConfigError(f"Wallet '{wallet_name}' not found in configuration")
        
        wallet = self.config['wallets'][wallet_name]
        
        # Follow redirects for consolidated wallets
        if 'redirectTo' in wallet:
            redirect_target = wallet['redirectTo']
            if redirect_target not in self.config['wallets']:
                raise WalletConfigError(
                    f"Wallet '{wallet_name}' redirects to '{redirect_target}' which does not exist"
                )
            _visited.add(wallet_name)
            return self.get_wallet_address(redirect_target, _visited)
        
        # Return the address from the wallet
        if 'address' not in wallet:
            raise WalletConfigError(f"Wallet '{wallet_name}' does not have an address")
        
        return wallet['address']
    
    def get_primary_wallet(self) -> Dict:
        """Get the primary wallet configuration."""
        return self.config['wallets'].get('primary', {})
    
    def get_offering_details(self) -> Dict:
        """Get the offering details and parameters."""
        return self.config.get('offering', {})
    
    def is_wallet_consolidated(self, wallet_name: str) -> bool:
        """
        Check if a wallet has been consolidated into another wallet.
        
        Args:
            wallet_name: Name of the wallet to check
        
        Returns:
            True if the wallet is consolidated (has a redirect), False otherwise
        """
        if wallet_name not in self.config.get('wallets', {}):
            return False
        
        wallet = self.config['wallets'][wallet_name]
        return 'redirectTo' in wallet and wallet.get('status') == 'consolidated'
    
    def get_pending_confirmations(self) -> List[str]:
        """
        Get list of pending confirmations required before launch.
        
        Returns:
            List of pending confirmation items
        """
        offering = self.config.get('offering', {})
        return offering.get('pendingConfirmations', [])
    
    def get_post_merge_actions(self) -> List[Dict]:
        """
        Get list of post-merge actions required.
        
        Returns:
            List of action items with priority, description, and status
        """
        return self.config.get('postMergeActions', [])
    
    def validate_configuration(self) -> bool:
        """
        Validate the wallet configuration.
        
        Returns:
            True if configuration is valid
        
        Raises:
            WalletConfigError: If validation fails
        """
        # Check that primary wallet exists and has an address
        primary = self.config.get('wallets', {}).get('primary')
        if not primary:
            raise WalletConfigError("Primary wallet not found in configuration")
        
        if not primary.get('address'):
            raise WalletConfigError("Primary wallet does not have an address")
        
        # Validate address format (EVM address validation)
        address = primary['address']
        if not address.startswith('0x'):
            raise WalletConfigError(f"Invalid EVM address format: must start with 0x")
        
        if len(address) != 42:
            raise WalletConfigError(f"Invalid EVM address length: must be 42 characters (0x + 40 hex digits)")
        
        # Check all characters after 0x are hexadecimal
        try:
            int(address[2:], 16)
        except ValueError:
            raise WalletConfigError(
                f"Invalid EVM address format: contains non-hexadecimal characters"
            )
        
        # Check that all consolidated wallets redirect correctly
        for wallet_name, wallet in self.config.get('wallets', {}).items():
            if 'redirectTo' in wallet:
                redirect_target = wallet['redirectTo']
                if redirect_target not in self.config['wallets']:
                    raise WalletConfigError(
                        f"Wallet '{wallet_name}' redirects to non-existent wallet '{redirect_target}'"
                    )
        
        # Validate offering configuration
        offering = self.config.get('offering', {})
        if offering:
            if 'startDate' in offering:
                try:
                    datetime.fromisoformat(offering['startDate'].replace('Z', '+00:00'))
                except ValueError as e:
                    raise WalletConfigError(f"Invalid offering start date format: {e}")
            
            if 'fundraisingGoal' in offering:
                goal = offering['fundraisingGoal']
                if not isinstance(goal, (int, float)) or goal <= 0:
                    raise WalletConfigError(
                        f"Invalid fundraising goal: {goal}. Must be a positive number."
                    )
        
        return True


def get_active_wallet_address(wallet_name: str = 'primary') -> str:
    """
    Convenience function to get the active wallet address.
    
    Args:
        wallet_name: Name of the wallet (default: 'primary')
    
    Returns:
        The EVM wallet address
    """
    config = WalletConfig()
    return config.get_wallet_address(wallet_name)


if __name__ == '__main__':
    # Example usage and validation
    try:
        config = WalletConfig()
        config.validate_configuration()
        
        print("✓ Wallet configuration is valid")
        print(f"\nPrimary wallet address: {config.get_wallet_address('primary')}")
        print(f"Governance audit wallet redirects to: {config.get_wallet_address('governance_audit')}")
        print(f"Digital bonds wallet redirects to: {config.get_wallet_address('digital_bonds')}")
        
        print(f"\nOffering details:")
        offering = config.get_offering_details()
        print(f"  Start date: {offering.get('startDate')}")
        print(f"  Fundraising goal: {offering.get('fundraisingGoal')}")
        print(f"  Status: {offering.get('status')}")
        
        print(f"\nPending confirmations:")
        for item in config.get_pending_confirmations():
            print(f"  - {item}")
        
    except WalletConfigError as e:
        print(f"✗ Configuration error: {e}")
        exit(1)
