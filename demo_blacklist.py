#!/usr/bin/env python3
"""
EUYSTACIO Blacklist Demo
Demonstrates the permanent blacklist functionality for blocking suspicious nodes and entities.
"""

import sys
import time
from euystacio_blacklist import (
    add_node_to_blacklist,
    add_entity_to_blacklist,
    add_pattern_to_blacklist,
    is_node_blocked,
    is_entity_blocked,
    check_input_against_blacklist,
    get_blacklist_status,
    remove_node_from_blacklist,
    _permanent_blacklist
)

def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def demo_basic_blocking():
    """Demonstrate basic node and entity blocking"""
    print_section("Demo 1: Basic Node and Entity Blocking")
    
    # Add suspicious nodes
    print("Adding suspicious nodes to blacklist...")
    add_node_to_blacklist(
        "192.168.1.100",
        "Multiple failed login attempts detected",
        severity="high",
        metadata={"failed_attempts": 15, "attack_type": "brute_force"}
    )
    add_node_to_blacklist(
        "10.0.0.5",
        "Port scanning activity detected",
        severity="critical",
        metadata={"scanned_ports": [22, 80, 443, 3306]}
    )
    print("✓ Nodes added")
    
    # Add suspicious entities
    print("\nAdding suspicious entities to blacklist...")
    add_entity_to_blacklist(
        "malicious_user_123",
        "Attempted SQL injection",
        severity="critical",
        metadata={"injection_type": "sql"}
    )
    add_entity_to_blacklist(
        "bot_crawler_456",
        "Aggressive scraping behavior",
        severity="medium",
        metadata={"requests_per_minute": 500}
    )
    print("✓ Entities added")
    
    # Check if blocked
    print("\nChecking if nodes/entities are blocked...")
    print(f"  192.168.1.100 blocked: {is_node_blocked('192.168.1.100')}")
    print(f"  10.0.0.5 blocked: {is_node_blocked('10.0.0.5')}")
    print(f"  malicious_user_123 blocked: {is_entity_blocked('malicious_user_123')}")
    print(f"  bot_crawler_456 blocked: {is_entity_blocked('bot_crawler_456')}")
    print(f"  safe_user blocked: {is_entity_blocked('safe_user')}")

def demo_pattern_blocking():
    """Demonstrate pattern-based blocking"""
    print_section("Demo 2: Pattern-Based Blocking")
    
    # Add malicious patterns
    print("Adding malicious patterns to blacklist...")
    patterns = [
        ("<script>", "XSS injection attempt", "high"),
        ("'; DROP TABLE", "SQL injection attempt", "critical"),
        ("eval(", "Code execution attempt", "high"),
        ("../../../", "Path traversal attempt", "high"),
    ]
    
    for pattern, reason, severity in patterns:
        add_pattern_to_blacklist(pattern, reason, severity)
        print(f"  ✓ Added pattern: {pattern}")
    
    # Test pattern matching
    print("\nTesting pattern detection...")
    test_inputs = [
        "Normal safe content",
        "Hello <script>alert('xss')</script> world",
        "SELECT * FROM users WHERE id = 1'; DROP TABLE users--",
        "Please navigate to ../../../etc/passwd",
    ]
    
    for test_input in test_inputs:
        result = check_input_against_blacklist({"content": test_input})
        status = "🔒 BLOCKED" if result['blocked'] else "✅ ALLOWED"
        print(f"  {status}: {test_input[:50]}...")
        if result['blocked']:
            print(f"    Reasons: {', '.join(result['reasons'])}")

def demo_comprehensive_check():
    """Demonstrate comprehensive input checking"""
    print_section("Demo 3: Comprehensive Input Validation")
    
    # Test various input scenarios
    test_cases = [
        {
            "name": "Clean input",
            "data": {
                "node_id": "192.168.1.200",
                "entity_id": "good_user",
                "content": "Hello, this is a normal message"
            }
        },
        {
            "name": "Blocked node",
            "data": {
                "node_id": "192.168.1.100",  # Already blacklisted
                "entity_id": "good_user",
                "content": "Normal message"
            }
        },
        {
            "name": "Blocked entity",
            "data": {
                "node_id": "192.168.1.200",
                "entity_id": "malicious_user_123",  # Already blacklisted
                "content": "Normal message"
            }
        },
        {
            "name": "Blocked pattern",
            "data": {
                "node_id": "192.168.1.200",
                "entity_id": "good_user",
                "content": "Check this <script>alert('xss')</script>"
            }
        },
    ]
    
    print("Testing comprehensive input validation...\n")
    for test_case in test_cases:
        result = check_input_against_blacklist(test_case['data'])
        status = "🔒 BLOCKED" if result['blocked'] else "✅ ALLOWED"
        print(f"{status} - {test_case['name']}")
        if result['blocked']:
            print(f"  Severity: {result['severity']}")
            for reason in result['reasons']:
                print(f"  - {reason}")
        print()

def demo_blacklist_status():
    """Demonstrate blacklist status reporting"""
    print_section("Demo 4: Blacklist Status and Statistics")
    
    status = get_blacklist_status()
    
    print("Current Blacklist Status:")
    print(f"  Total blocks ever created: {status['total_blocks']}")
    print(f"\n  Active Blocks:")
    print(f"    Nodes: {status['active_blocks']['nodes']}")
    print(f"    Entities: {status['active_blocks']['entities']}")
    print(f"    Patterns: {status['active_blocks']['patterns']}")
    print(f"    Total Active: {status['active_blocks']['total']}")
    
    print(f"\n  Cache Status:")
    print(f"    Node cache size: {status['cache_status']['node_cache_size']}")
    print(f"    Entity cache size: {status['cache_status']['entity_cache_size']}")
    print(f"    Pattern cache size: {status['cache_status']['pattern_cache_size']}")
    
    print(f"\n  Metadata:")
    print(f"    Created: {status['metadata']['created_at']}")
    print(f"    Last updated: {status['metadata']['last_updated']}")
    print(f"    Version: {status['metadata']['version']}")

def demo_list_blocked():
    """Demonstrate listing blocked items"""
    print_section("Demo 5: Listing Blocked Items")
    
    # List blocked nodes
    print("Blocked Nodes:")
    nodes = _permanent_blacklist.get_blocked_nodes()
    for node in nodes:
        print(f"  • {node['node_id']}")
        print(f"    Reason: {node['reason']}")
        print(f"    Severity: {node['severity']}")
        print(f"    Occurrences: {node['occurrences']}")
        print(f"    Added: {node['added_at']}")
        print()
    
    # List blocked entities
    print("Blocked Entities:")
    entities = _permanent_blacklist.get_blocked_entities()
    for entity in entities:
        print(f"  • {entity['entity_id']}")
        print(f"    Reason: {entity['reason']}")
        print(f"    Severity: {entity['severity']}")
        print(f"    Occurrences: {entity['occurrences']}")
        print(f"    Added: {entity['added_at']}")
        print()

def demo_removal():
    """Demonstrate removing from blacklist"""
    print_section("Demo 6: Removing from Blacklist")
    
    # Add a test node for removal
    test_node = "192.168.1.50"
    print(f"Adding test node {test_node} to blacklist...")
    add_node_to_blacklist(test_node, "Test for removal demo", "low")
    print(f"  ✓ Node added")
    print(f"  Is blocked: {is_node_blocked(test_node)}")
    
    # Remove it
    print(f"\nRemoving {test_node} from blacklist...")
    remove_node_from_blacklist(test_node, "demo_admin")
    print(f"  ✓ Node removed")
    print(f"  Is blocked: {is_node_blocked(test_node)}")
    
    print("\nNote: Removal is a soft delete - the entry is preserved for audit purposes")

def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  EUYSTACIO PERMANENT BLACKLIST DEMONSTRATION")
    print("  Protecting the system from suspicious nodes and entities")
    print("="*60)
    
    try:
        demo_basic_blocking()
        time.sleep(0.5)
        
        demo_pattern_blocking()
        time.sleep(0.5)
        
        demo_comprehensive_check()
        time.sleep(0.5)
        
        demo_blacklist_status()
        time.sleep(0.5)
        
        demo_list_blocked()
        time.sleep(0.5)
        
        demo_removal()
        
        print_section("Demo Complete")
        print("✅ All demonstrations completed successfully!")
        print("\nThe permanent blacklist is now protecting the EUYSTACIO framework")
        print("from suspicious nodes, entities, and malicious patterns.")
        print("\nFor more information, see: docs/blacklist_documentation.md")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
