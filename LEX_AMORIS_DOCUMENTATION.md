# Lex Amoris Security Platform Documentation

## Overview

The Lex Amoris Security Platform implements four strategic enhancements based on the principles of Lex Amoris (Law of Love) - providing comprehensive security through compassion, efficiency, and resilience.

## Strategic Enhancements

### 1. Dynamic Blacklist & Rhythm Validation 🎵

**Purpose:** Behavioral security control through frequency/vibration validation.

**Features:**
- Validates packets based on rhythmic signature, independent of IP origin
- Dynamic blacklist automatically blocks packets with incorrect frequencies
- Based on 432 Hz harmony frequency (Lex Amoris resonance)
- IP-agnostic security - blocks based on content, not source

**Implementation:**
```python
from lex_amoris_integration import get_platform

platform = get_platform()
result = platform.rhythm_validator.validate_packet(
    packet_data={"type": "data", "content": "..."},
    origin_ip="1.2.3.4"  # Optional - not used for validation
)
```

**API Endpoint:**
```bash
POST /api/lex-amoris/rhythm/validate
{
  "packet_data": {...},
  "origin_ip": "1.2.3.4"  # Optional
}
```

### 2. Lazy Security ⚡

**Purpose:** Energy-efficient protection that activates only when environmental pressure is detected.

**Features:**
- Rotesschild scan detects electromagnetic pressure (mV/m)
- Activates protections only when threshold exceeded (> 50 mV/m)
- Four security levels: DORMANT, MONITORING, ACTIVE, CRITICAL
- Tracks energy savings and consumption
- Automatic energy regeneration during dormant periods

**Security Levels:**
- **DORMANT** (< 25 mV/m): All protections off, maximum energy savings
- **MONITORING** (25-50 mV/m): Passive monitoring only
- **ACTIVE** (50-75 mV/m): Core protections active
- **CRITICAL** (> 75 mV/m): All protections at maximum

**Implementation:**
```python
platform = get_platform()

# Trigger environmental scan
state = platform.lazy_security.update_security_state()

# Process request (only applies protections if needed)
result = platform.lazy_security.process_request(request_data)
```

**API Endpoint:**
```bash
POST /api/lex-amoris/security/scan
GET /api/lex-amoris/security/status
```

### 3. IPFS Backup & Mirroring 💾

**Purpose:** Distributed backup storage for resilience against centralized attacks.

**Features:**
- Complete mirroring of PR configurations
- Repository state snapshots
- Security configuration backups
- Content-addressable storage (IPFS CID)
- Integrity verification
- Gateway URLs for distributed access

**Backup Types:**
- **PR Configuration**: Pull request settings and metadata
- **Repository State**: Complete repository snapshots
- **Security Configuration**: Security settings and rules

**Implementation:**
```python
platform = get_platform()

# Create complete backup snapshot
backup = platform.create_backup_snapshot()
print(f"Security backup: {backup['security_backup']['content_hash']}")

# List all backups
backups = platform.ipfs_backup.list_backups(backup_type="security")

# Restore from backup
data = platform.ipfs_backup.restore_from_backup(content_hash)
```

**API Endpoints:**
```bash
POST /api/lex-amoris/backup/create
GET /api/lex-amoris/backup/status
GET /api/lex-amoris/backup/list?type=security&limit=50
```

### 4. Lex Amoris Rescue Channel 🆘

**Purpose:** Compassionate handling of false positives and critical node unblocking.

**Features:**
- Lex Amoris signature validation (528 Hz love frequency)
- Evidence-based approval system
- Auto-approval after repeated false positives
- Priority levels: LOW, NORMAL, HIGH, CRITICAL
- False positive tracking and learning
- Emergency override capability

**Priority Handling:**
- **LOW**: Standard review process
- **NORMAL**: Evidence-based evaluation (70% threshold)
- **HIGH**: Fast-track review
- **CRITICAL**: Immediate approval with admin notification

**Implementation:**
```python
platform = get_platform()

# Request rescue for blocked node
result = platform.request_rescue(
    sender_id="user-123",
    node_id="node-456",
    reason="False positive detection",
    evidence={
        "legitimate_traffic_pattern": True,
        "historical_data": {"avg_requests": 100},
        "user_verification": True
    },
    priority="HIGH"
)

if result['response']['approved']:
    print(f"Node unblocked: {result['response']['actions_taken']}")
```

**API Endpoint:**
```bash
POST /api/lex-amoris/rescue/request
{
  "sender_id": "user-123",
  "node_id": "node-456",
  "reason": "False positive - legitimate traffic",
  "evidence": {
    "legitimate_traffic_pattern": true,
    "historical_data": {...},
    "user_verification": true
  },
  "priority": "HIGH"
}
```

## Integrated Platform

### Getting Started

```python
from lex_amoris_integration import get_platform

# Get platform instance (singleton)
platform = get_platform()

# Process request through all layers
result = platform.process_request(
    request_data={"action": "api_call", "resource": "/data"},
    origin_ip="203.0.113.42",
    sender_id="client-789"
)

if result['allowed']:
    print("Request approved")
else:
    print(f"Request blocked: {result['reason']}")
    if result.get('rescue_available'):
        print("Rescue channel available for appeal")
```

### Platform Status

```python
# Get comprehensive status
status = platform.get_platform_status()

print(f"Platform: {status['platform']} v{status['version']}")
print(f"Security level: {status['components']['lazy_security']['security_level']}")
print(f"Total requests: {status['statistics']['total_requests']}")
print(f"Block rate: {status['statistics']['block_rate']}")
```

## API Reference

### Health Check
```bash
GET /api/lex-amoris/health
```

### Platform Status
```bash
GET /api/lex-amoris/status
```

### Process Request
```bash
POST /api/lex-amoris/process
{
  "data": {...},
  "origin_ip": "1.2.3.4",
  "sender_id": "user-123"
}
```

### List All Endpoints
```bash
GET /api/lex-amoris/endpoints
```

## Running the API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Lex Amoris API server
python lex_amoris_api.py

# Server starts on http://0.0.0.0:5001
```

## Running Tests

```bash
# Run comprehensive test suite
python test_lex_amoris.py

# Expected output:
# ✓ TEST 1: Dynamic Blacklist & Rhythm Validation
# ✓ TEST 2: Lazy Security (Energy-Based Protection)
# ✓ TEST 3: IPFS Backup & Mirroring
# ✓ TEST 4: Lex Amoris Rescue Channel
# ✓ TEST 5: Integrated Platform
```

## Configuration

### Environment Variables

```bash
# Rhythm Validation
LEX_AMORIS_BASE_FREQUENCY=432.0  # Hz
LEX_AMORIS_TOLERANCE=0.05        # 5%

# Lazy Security
LAZY_SECURITY_THRESHOLD=50.0      # mV/m
LAZY_SECURITY_ENERGY_BUDGET=100.0

# IPFS Backup
IPFS_GATEWAY=https://ipfs.io
IPFS_BACKUP_PATH=/tmp/ipfs_backups

# Rescue Channel
RESCUE_AUTO_APPROVE_THRESHOLD=3
RESCUE_WINDOW_HOURS=24
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Lex Amoris Security Platform                │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼───────┐ ┌──────▼──────┐ ┌───────▼────────┐
│   Rhythm      │ │    Lazy     │ │  IPFS Backup   │
│  Validation   │ │  Security   │ │   & Mirror     │
└───────┬───────┘ └──────┬──────┘ └───────┬────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                  ┌───────▼────────┐
                  │ Rescue Channel │
                  │  (Lex Amoris)  │
                  └────────────────┘
```

## Security Principles

1. **Defense in Depth**: Multiple layers of protection
2. **Energy Efficiency**: Protections activate only when needed
3. **Compassionate Security**: Rescue mechanism for false positives
4. **Distributed Resilience**: IPFS backup for attack resistance
5. **Behavioral Validation**: Content-based, not IP-based blocking

## Best Practices

1. **Regular Backups**: Schedule periodic `create_backup_snapshot()` calls
2. **Monitor Security Level**: Track environmental pressure trends
3. **Review Rescue Requests**: Analyze false positive patterns
4. **Energy Management**: Balance security vs. efficiency
5. **Signature Validation**: Verify Lex Amoris signatures for authenticity

## Troubleshooting

### High Block Rate
- Check rhythm validation tolerance
- Review blacklist entries
- Analyze rescue request patterns

### Energy Depletion
- Lower security activation threshold
- Reduce protection module costs
- Increase energy regeneration rate

### Backup Failures
- Verify IPFS gateway connectivity
- Check backup path permissions
- Monitor storage capacity

### Rescue Denials
- Improve evidence quality
- Increase priority for legitimate requests
- Review auto-approve threshold

## Support

For issues or questions about the Lex Amoris Security Platform, please refer to:
- Test suite: `test_lex_amoris.py`
- API documentation: `lex_amoris_api.py`
- Integration guide: `lex_amoris_integration.py`

---

**Made with 🕊️ and ❤️ following Lex Amoris principles**
