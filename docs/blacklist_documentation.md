# EUYSTACIO Permanent Blacklist - Documentation

## Overview

The EUYSTACIO Permanent Blacklist is a security feature that provides continuous protection against attack attempts and theft by permanently blocking communications from suspicious nodes and entities that threaten system security.

## Features

### 1. Permanent Blocking
- **Nodes**: Block by IP address, node ID, or any identifier
- **Entities**: Block users, API keys, or other entity identifiers
- **Patterns**: Block based on suspicious content patterns

### 2. Persistent Storage
- Blacklist data is stored in JSON format
- Automatic persistence on every change
- Atomic file operations to prevent corruption
- Version-aware data loading with validation

### 3. Fast Lookups
- In-memory caching for instant blocking decisions
- Separate caches for nodes, entities, and patterns
- Cache automatically updated on blacklist changes

### 4. Thread-Safe Operations
- All operations protected by threading locks
- Prevents race conditions and data corruption
- Safe for concurrent access

### 5. Audit Trail
- Soft delete mechanism preserves history
- All blacklist events logged to audit system
- Tracks who added/removed entries and when

## API Endpoints

### Get Blacklist Status
```
GET /api/blacklist/status
```
Returns comprehensive blacklist statistics including:
- Total number of blocks
- Active blocks by category (nodes, entities, patterns)
- Metadata (creation time, last update, version)
- Cache status

### Add Node to Blacklist
```
POST /api/blacklist/node/add
Content-Type: application/json

{
  "node_id": "192.168.1.100",
  "reason": "Suspicious activity detected",
  "severity": "high",
  "metadata": {
    "attack_type": "brute_force",
    "attempts": 50
  }
}
```

Severity levels: `low`, `medium`, `high`, `critical`

### Add Entity to Blacklist
```
POST /api/blacklist/entity/add
Content-Type: application/json

{
  "entity_id": "malicious_user_123",
  "reason": "Attempted unauthorized access",
  "severity": "critical",
  "metadata": {
    "user_agent": "suspicious_bot"
  }
}
```

### Add Pattern to Blacklist
```
POST /api/blacklist/pattern/add
Content-Type: application/json

{
  "pattern": "<script>",
  "reason": "XSS injection attempt",
  "severity": "high",
  "metadata": {
    "pattern_type": "xss"
  }
}
```

### Check Input Against Blacklist
```
POST /api/blacklist/check
Content-Type: application/json

{
  "node_id": "192.168.1.100",
  "entity_id": "user123",
  "source_ip": "10.0.0.5",
  "api_key": "key_abc123",
  "content": "message content here"
}
```

Response:
```json
{
  "success": true,
  "blocked": true,
  "reasons": [
    "Node 192.168.1.100 is blacklisted",
    "Content matches blocked pattern"
  ],
  "severity": "high"
}
```

### Check Specific Node
```
GET /api/blacklist/node/check/<node_id>
```

Response:
```json
{
  "success": true,
  "node_id": "192.168.1.100",
  "blocked": true
}
```

### Check Specific Entity
```
GET /api/blacklist/entity/check/<entity_id>
```

### List All Blocked Nodes
```
GET /api/blacklist/nodes?include_removed=false
```

Returns array of blocked nodes with details:
```json
{
  "success": true,
  "count": 5,
  "nodes": [
    {
      "node_id": "192.168.1.100",
      "added_at": "2026-01-15T01:00:00.000000",
      "last_seen": "2026-01-15T01:30:00.000000",
      "reason": "Suspicious activity detected",
      "severity": "high",
      "metadata": {},
      "occurrences": 3,
      "status": "active"
    }
  ]
}
```

### List All Blocked Entities
```
GET /api/blacklist/entities?include_removed=false
```

### Remove Node from Blacklist
```
POST /api/blacklist/node/remove
Content-Type: application/json

{
  "node_id": "192.168.1.100",
  "authorized_by": "admin_user"
}
```

**Note**: Removal is a soft delete - the entry is marked as removed but preserved for audit purposes.

### Remove Entity from Blacklist
```
POST /api/blacklist/entity/remove
Content-Type: application/json

{
  "entity_id": "user123",
  "authorized_by": "admin_user"
}
```

## Python API

### Import
```python
from euystacio_blacklist import (
    add_node_to_blacklist,
    add_entity_to_blacklist,
    add_pattern_to_blacklist,
    is_node_blocked,
    is_entity_blocked,
    check_input_against_blacklist,
    get_blacklist_status,
    remove_node_from_blacklist,
    remove_entity_from_blacklist
)
```

### Add to Blacklist
```python
# Add a node
add_node_to_blacklist(
    "192.168.1.100",
    "Suspicious activity detected",
    severity="high",
    metadata={"attack_type": "brute_force"}
)

# Add an entity
add_entity_to_blacklist(
    "malicious_user",
    "Attempted unauthorized access",
    severity="critical"
)

# Add a pattern
add_pattern_to_blacklist(
    "<script>",
    "XSS injection attempt",
    severity="high"
)
```

### Check if Blocked
```python
# Check specific node
if is_node_blocked("192.168.1.100"):
    print("Node is blocked")

# Check specific entity
if is_entity_blocked("malicious_user"):
    print("Entity is blocked")

# Comprehensive input check
input_data = {
    "node_id": "192.168.1.100",
    "entity_id": "user123",
    "content": "message content"
}
result = check_input_against_blacklist(input_data)
if result['blocked']:
    print(f"Blocked: {result['reasons']}")
    print(f"Severity: {result['severity']}")
```

### Get Status
```python
status = get_blacklist_status()
print(f"Total blocks: {status['total_blocks']}")
print(f"Active nodes: {status['active_blocks']['nodes']}")
print(f"Active entities: {status['active_blocks']['entities']}")
```

### Remove from Blacklist
```python
# Remove node (requires authorization)
remove_node_from_blacklist("192.168.1.100", "admin_user")

# Remove entity
remove_entity_from_blacklist("user123", "admin_user")
```

## Guardian Integration

The blacklist is automatically integrated with the EUYSTACIO Guardian system. When the guardian validates input, it:

1. **Checks against blacklist first** - Before any other validation
2. **Blocks immediately** - If input matches blacklist, it's quarantined
3. **Auto-adds threats** - Detected malicious patterns are automatically added
4. **Reports status** - Blacklist status included in guardian status reports

### Example Guardian Usage
```python
from euystacio_helmi_guardian import EuystacioHelmiGuardian

guardian = EuystacioHelmiGuardian()

# Validate input (automatically checks blacklist)
input_data = {
    "node_id": "192.168.1.100",
    "emotion": "Calm",
    "context": "Peaceful"
}

if guardian.validate_input(input_data):
    print("Input validated")
else:
    print("Input blocked")

# Get guardian status (includes blacklist info)
status = guardian.get_guardian_status()
print(f"Blacklist status: {status['blacklist_status']}")
```

## Data Storage

### File Format
The blacklist is stored in JSON format at `euystacio_blacklist.json`:

```json
{
  "nodes": {
    "192.168.1.100": {
      "added_at": "2026-01-15T01:00:00.000000",
      "last_seen": "2026-01-15T01:30:00.000000",
      "reason": "Suspicious activity detected",
      "severity": "high",
      "metadata": {},
      "occurrences": 3,
      "status": "active"
    }
  },
  "entities": {},
  "patterns": {},
  "metadata": {
    "created_at": "2026-01-15T00:00:00.000000",
    "last_updated": "2026-01-15T01:30:00.000000",
    "version": "1.0.0",
    "total_blocks": 1
  }
}
```

### Custom Storage Location
```python
from euystacio_blacklist import PermanentBlacklist

# Create blacklist with custom file location
custom_blacklist = PermanentBlacklist("/path/to/custom_blacklist.json")
```

## Security Considerations

1. **Pattern Hashing**: Patterns are hashed using SHA-256 for secure storage
2. **Data Validation**: All loaded data is validated before use
3. **Atomic Operations**: File writes use atomic replace to prevent corruption
4. **Audit Logging**: All blacklist events are logged for security audit
5. **Soft Delete**: Removed entries are preserved for forensic analysis

## Performance

- **Fast Lookups**: O(1) average case for node/entity checks using hash sets
- **Pattern Matching**: O(n) where n is number of patterns (optimized with lock-free read)
- **Cache Updates**: Automatic cache synchronization on all changes
- **Thread Safety**: Lock-based synchronization ensures data consistency

## Monitoring

Monitor blacklist effectiveness through:
- Guardian status endpoint: `/api/blacklist/status`
- Audit logs: Check `council_ledger.log` for blacklist events
- Metrics: Track `active_blocks`, `total_blocks`, and `occurrences`

## Best Practices

1. **Regular Review**: Periodically review blocked nodes/entities
2. **Severity Levels**: Use appropriate severity levels for different threats
3. **Metadata**: Include detailed metadata for forensic analysis
4. **Authorization**: Always provide `authorized_by` when removing entries
5. **Pattern Specificity**: Use specific patterns to avoid false positives
6. **Backup**: Regularly backup `euystacio_blacklist.json`

## Troubleshooting

### Blacklist Not Working
- Check that `euystacio_blacklist.py` is imported correctly
- Verify file permissions on `euystacio_blacklist.json`
- Check audit logs for blacklist initialization errors

### False Positives
- Review pattern list for overly broad patterns
- Check entity/node IDs for wildcards or regex
- Use metadata to understand why entries were added

### Performance Issues
- If pattern matching is slow, reduce number of patterns
- Consider consolidating similar patterns
- Monitor cache hit rates in status endpoint

## Example Use Cases

### 1. Block Brute Force Attacks
```python
# Detect multiple failed login attempts
failed_attempts = detect_failed_logins("192.168.1.100")
if failed_attempts > 5:
    add_node_to_blacklist(
        "192.168.1.100",
        f"Brute force attack: {failed_attempts} failed attempts",
        severity="critical",
        metadata={"attack_type": "brute_force", "attempts": failed_attempts}
    )
```

### 2. Block Known Malicious Patterns
```python
# Block common attack patterns
malicious_patterns = [
    "<script>",
    "'; DROP TABLE",
    "exec(",
    "eval(",
    "../../../etc/passwd"
]

for pattern in malicious_patterns:
    add_pattern_to_blacklist(
        pattern,
        f"Known attack pattern: {pattern[:20]}...",
        severity="high"
    )
```

### 3. Temporary Block with Removal
```python
# Block temporarily, then remove after investigation
add_node_to_blacklist("10.0.0.5", "Suspicious activity under investigation", "medium")

# ... investigate ...

# Remove after clearing
remove_node_from_blacklist("10.0.0.5", "security_admin")
```

## Support

For issues or questions about the blacklist system:
1. Check audit logs for detailed error messages
2. Review test suite in `test_euystacio_blacklist.py` for usage examples
3. Consult the guardian specification in `docs/guardian_specification.md`
