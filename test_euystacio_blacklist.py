"""
Tests for EUYSTACIO Permanent Blacklist Module

These tests verify the blacklist functionality for blocking suspicious nodes and entities.
"""

import os
import json
import tempfile
from datetime import datetime
from euystacio_blacklist import (
    PermanentBlacklist,
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

def test_blacklist_initialization():
    """Test blacklist initialization"""
    print("Testing blacklist initialization...")
    
    # Create temporary blacklist file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        blacklist = PermanentBlacklist(temp_file)
        
        # Check initial state
        status = blacklist.get_blacklist_status()
        assert status['active_blocks']['nodes'] == 0
        assert status['active_blocks']['entities'] == 0
        assert status['active_blocks']['patterns'] == 0
        
        print("✓ Blacklist initialization test passed")
        return True
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_add_node_to_blacklist():
    """Test adding nodes to blacklist"""
    print("Testing adding nodes to blacklist...")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        blacklist = PermanentBlacklist(temp_file)
        
        # Add a node
        result = blacklist.add_node(
            "192.168.1.100",
            "Suspicious activity detected",
            severity="high",
            metadata={"attack_type": "brute_force"}
        )
        
        assert result == True
        assert blacklist.is_node_blocked("192.168.1.100")
        
        # Check status
        status = blacklist.get_blacklist_status()
        assert status['active_blocks']['nodes'] == 1
        
        print("✓ Add node to blacklist test passed")
        return True
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_add_entity_to_blacklist():
    """Test adding entities to blacklist"""
    print("Testing adding entities to blacklist...")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        blacklist = PermanentBlacklist(temp_file)
        
        # Add an entity
        result = blacklist.add_entity(
            "malicious_user_123",
            "Attempted unauthorized access",
            severity="critical",
            metadata={"user_agent": "suspicious_bot"}
        )
        
        assert result == True
        assert blacklist.is_entity_blocked("malicious_user_123")
        
        # Check status
        status = blacklist.get_blacklist_status()
        assert status['active_blocks']['entities'] == 1
        
        print("✓ Add entity to blacklist test passed")
        return True
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_add_pattern_to_blacklist():
    """Test adding patterns to blacklist"""
    print("Testing adding patterns to blacklist...")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        blacklist = PermanentBlacklist(temp_file)
        
        # Add a pattern
        result = blacklist.add_pattern(
            "<script>alert('xss')</script>",
            "XSS injection attempt",
            severity="high"
        )
        
        assert result == True
        
        # Check if pattern is detected in content
        assert blacklist.is_pattern_blocked("<script>alert('xss')</script> malicious code")
        
        # Check status
        status = blacklist.get_blacklist_status()
        assert status['active_blocks']['patterns'] == 1
        
        print("✓ Add pattern to blacklist test passed")
        return True
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_check_input_against_blacklist():
    """Test comprehensive input checking"""
    print("Testing input checking against blacklist...")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        blacklist = PermanentBlacklist(temp_file)
        
        # Add test data
        blacklist.add_node("10.0.0.5", "Known attacker", "critical")
        blacklist.add_entity("bad_user", "Malicious entity", "high")
        blacklist.add_pattern("malware", "Malware signature", "high")
        
        # Test 1: Clean input (should pass)
        clean_input = {
            "node_id": "10.0.0.100",
            "entity_id": "good_user",
            "content": "normal message"
        }
        result = blacklist.check_input(clean_input)
        assert result['blocked'] == False
        assert len(result['reasons']) == 0
        
        # Test 2: Blocked node (should fail)
        blocked_node_input = {
            "node_id": "10.0.0.5",
            "entity_id": "good_user",
            "content": "normal message"
        }
        result = blacklist.check_input(blocked_node_input)
        assert result['blocked'] == True
        assert len(result['reasons']) > 0
        assert result['severity'] == 'critical'
        
        # Test 3: Blocked entity (should fail)
        blocked_entity_input = {
            "node_id": "10.0.0.100",
            "entity_id": "bad_user",
            "content": "normal message"
        }
        result = blacklist.check_input(blocked_entity_input)
        assert result['blocked'] == True
        assert len(result['reasons']) > 0
        
        # Test 4: Blocked pattern (should fail)
        blocked_pattern_input = {
            "node_id": "10.0.0.100",
            "entity_id": "good_user",
            "content": "this contains malware code"
        }
        result = blacklist.check_input(blocked_pattern_input)
        assert result['blocked'] == True
        assert len(result['reasons']) > 0
        
        print("✓ Input checking test passed")
        return True
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_blacklist_persistence():
    """Test blacklist persistence across instances"""
    print("Testing blacklist persistence...")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # Create first instance and add data
        blacklist1 = PermanentBlacklist(temp_file)
        blacklist1.add_node("192.168.1.50", "Test node", "high")
        blacklist1.add_entity("test_entity", "Test entity", "medium")
        
        # Create second instance and verify data persisted
        blacklist2 = PermanentBlacklist(temp_file)
        assert blacklist2.is_node_blocked("192.168.1.50")
        assert blacklist2.is_entity_blocked("test_entity")
        
        status = blacklist2.get_blacklist_status()
        assert status['active_blocks']['nodes'] == 1
        assert status['active_blocks']['entities'] == 1
        
        print("✓ Blacklist persistence test passed")
        return True
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_remove_from_blacklist():
    """Test removing items from blacklist"""
    print("Testing removal from blacklist...")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        blacklist = PermanentBlacklist(temp_file)
        
        # Add items
        blacklist.add_node("192.168.1.60", "Test node", "high")
        blacklist.add_entity("test_entity_2", "Test entity", "medium")
        
        # Verify they're blocked
        assert blacklist.is_node_blocked("192.168.1.60")
        assert blacklist.is_entity_blocked("test_entity_2")
        
        # Remove them
        result1 = blacklist.remove_node("192.168.1.60", "admin")
        result2 = blacklist.remove_entity("test_entity_2", "admin")
        
        assert result1 == True
        assert result2 == True
        
        # Verify they're no longer blocked
        assert not blacklist.is_node_blocked("192.168.1.60")
        assert not blacklist.is_entity_blocked("test_entity_2")
        
        print("✓ Removal from blacklist test passed")
        return True
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_global_api_functions():
    """Test global API functions"""
    print("Testing global API functions...")
    
    # These use the global instance, so they'll modify the actual blacklist
    # We'll test with unique identifiers to avoid conflicts
    
    test_node = f"test_node_{int(datetime.utcnow().timestamp())}"
    test_entity = f"test_entity_{int(datetime.utcnow().timestamp())}"
    
    # Add to blacklist
    add_node_to_blacklist(test_node, "Test reason", "high")
    add_entity_to_blacklist(test_entity, "Test reason", "high")
    
    # Check they're blocked
    assert is_node_blocked(test_node)
    assert is_entity_blocked(test_entity)
    
    # Get status
    status = get_blacklist_status()
    assert status['active_blocks']['total'] >= 2
    
    # Clean up
    remove_node_from_blacklist(test_node, "test")
    remove_entity_from_blacklist(test_entity, "test")
    
    print("✓ Global API functions test passed")
    return True

def run_all_tests():
    """Run all blacklist tests"""
    print("\n=== Running EUYSTACIO Blacklist Tests ===\n")
    
    tests = [
        test_blacklist_initialization,
        test_add_node_to_blacklist,
        test_add_entity_to_blacklist,
        test_add_pattern_to_blacklist,
        test_check_input_against_blacklist,
        test_blacklist_persistence,
        test_remove_from_blacklist,
        test_global_api_functions
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    return failed == 0

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
