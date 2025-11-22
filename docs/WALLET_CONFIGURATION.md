# Wallet Configuration Documentation

## Overview

The AI-Based Peace Platform uses a consolidated wallet structure for investment operations. This document describes the wallet configuration, consolidation strategy, and pending requirements.

## Consolidated Wallet Structure

### Primary Wallet (Consolidated)
- **Address**: `0x6c10692145718353070cc6cb5c21adf2073ffa1f`
- **Type**: EVM (Ethereum Virtual Machine)
- **Purposes**:
  - Investment collection
  - Governance audit operations
  - Digital bonds management
- **Status**: Active

### Consolidated Wallets

The following wallets have been consolidated into the primary wallet:

1. **Governance Audit Wallet**
   - Redirects to: Primary wallet
   - Consolidation date: 2025-11-03
   - Purpose: All governance audit operations now use the primary wallet address

2. **Digital Bonds Wallet**
   - Redirects to: Primary wallet
   - Consolidation date: 2025-11-03
   - Purpose: All digital bonds operations now use the primary wallet address

## Benefits of Consolidation

1. **Simplified Operations**: Single wallet address for all investment-related operations
2. **Improved Audit Efficiency**: Centralized transaction history in one address
3. **Reduced Complexity**: Fewer wallet addresses to manage and monitor
4. **Enhanced Security**: Consolidated security measures for a single wallet
5. **Cost Efficiency**: Reduced gas fees and operational overhead

## Offering Parameters

### Current Configuration
- **Start Date**: December 1, 2025, 00:00:00 UTC
- **Fundraising Goal**: 5,000,000 units (asset to be confirmed)
- **Status**: Pending final confirmation

### Pending Confirmations

The following parameters require confirmation before launch:

1. **Chain/Network**
   - Options: Polygon, Arbitrum, or other EVM-compatible chain
   - Status: Awaiting decision
   - Impact: Determines gas costs, transaction speed, and ecosystem compatibility

2. **Fundraising Asset**
   - Options: USDC, ETH, DAI, or other cryptocurrency/stablecoin
   - Status: Awaiting decision
   - Impact: Determines investor accessibility and price stability

3. **Asset Decimals**
   - Typical values:
     - USDC: 6 decimals
     - ETH: 18 decimals
     - DAI: 18 decimals
   - Status: To be confirmed based on asset selection
   - Impact: Affects how amounts are represented on-chain

## Post-Merge Actions

After merging the wallet consolidation changes, the following actions are required:

| Priority | Action | Description | Status |
|----------|--------|-------------|--------|
| 1 | Confirm chain/network | Select and confirm the blockchain network | Pending |
| 2 | Confirm fundraising asset | Select and confirm the asset for fundraising | Pending |
| 3 | Confirm asset decimals | Confirm decimals relative to the selected asset | Pending |
| 4 | Configure on-chain automation | Set up and test on-chain automation for the wallet | Pending |
| 5 | Test wallet operations | Comprehensive testing of all operations | Pending |

## Usage

### Python Module

The wallet configuration can be accessed programmatically using the `wallet_config.py` module:

```python
from wallet_config import WalletConfig, get_active_wallet_address

# Get the primary wallet address
address = get_active_wallet_address()
print(f"Primary wallet: {address}")

# Use the full configuration
config = WalletConfig()

# Get address for any wallet (follows redirects automatically)
gov_audit_address = config.get_wallet_address('governance_audit')
bonds_address = config.get_wallet_address('digital_bonds')

# Both will return the primary wallet address
assert gov_audit_address == bonds_address

# Get offering details
offering = config.get_offering_details()
print(f"Start date: {offering['startDate']}")
print(f"Goal: {offering['fundraisingGoal']}")

# Check pending confirmations
confirmations = config.get_pending_confirmations()
for item in confirmations:
    print(f"Pending: {item}")

# Validate configuration
config.validate_configuration()
```

### Direct JSON Access

The wallet configuration is stored in `config/wallets.json` and can be accessed directly:

```json
{
  "wallets": {
    "primary": {
      "address": "0x6c10692145718353070cc6cb5c21adf2073ffa1f",
      "type": "EVM",
      "purposes": ["investment_collection", "governance_audit", "digital_bonds"]
    },
    "governance_audit": {
      "redirectTo": "primary",
      "status": "consolidated"
    },
    "digital_bonds": {
      "redirectTo": "primary",
      "status": "consolidated"
    }
  }
}
```

## Configuration Updates

When the pending parameters are confirmed, update the configuration file:

### Example: After Chain Selection

```json
{
  "wallets": {
    "primary": {
      "chain": "polygon",
      "chainNote": null
    }
  }
}
```

### Example: After Asset Selection

```json
{
  "offering": {
    "fundraisingAsset": "USDC",
    "fundraisingAssetNote": null,
    "decimals": 6,
    "decimalsNote": null,
    "status": "confirmed"
  }
}
```

## Testing

Run the test suite to validate the configuration:

```bash
python -m pytest test_wallet_config.py -v
```

The test suite includes:
- Configuration loading and validation
- Wallet address resolution
- Redirect functionality
- Offering parameters
- Data integrity checks

## Security Considerations

1. **Private Keys**: Never store private keys in the configuration file
2. **Access Control**: Limit access to wallet configuration files
3. **Validation**: Always validate configuration before use
4. **Audit Trail**: All changes are recorded in the audit trail
5. **Multi-signature**: Consider implementing multi-signature requirements for the primary wallet

## Audit Trail

All significant changes to the wallet configuration are recorded in the `auditTrail` section:

```json
{
  "auditTrail": [
    {
      "date": "2025-11-03T18:14:33Z",
      "action": "Initial consolidation",
      "description": "Created consolidated wallet configuration",
      "affectedWallets": ["primary", "governance_audit", "digital_bonds"]
    }
  ]
}
```

## Support and Contact

For questions or issues related to wallet configuration:
- Review the test suite in `test_wallet_config.py`
- Check the module implementation in `wallet_config.py`
- Refer to the configuration file at `config/wallets.json`

## Next Steps

1. Review and approve the consolidated wallet configuration
2. Confirm the chain/network selection
3. Confirm the fundraising asset
4. Update the configuration with confirmed parameters
5. Test wallet operations on the selected chain
6. Deploy on-chain automation
7. Begin fundraising operations on December 1, 2025
