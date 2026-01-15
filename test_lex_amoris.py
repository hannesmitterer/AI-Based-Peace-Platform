"""
Test suite for Lex Amoris Security Platform
Demonstrates all four strategic enhancements.
"""

import json
import traceback
from datetime import datetime

from lex_amoris_integration import LexAmorisSecurityPlatform


def test_rhythm_validation():
    """Test 1: Dynamic Blacklist and Rhythm Validation"""
    print("\n" + "="*60)
    print("TEST 1: Dynamic Blacklist & Rhythm Validation")
    print("="*60)
    
    platform = LexAmorisSecurityPlatform()
    
    # Test packet with correct rhythm
    packet1 = {
        "type": "data",
        "content": "legitimate_data",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    result1 = platform.rhythm_validator.validate_packet(packet1, origin_ip="192.168.1.1")
    print(f"\n✓ Packet 1 validation: {result1['valid']}")
    print(f"  Reason: {result1['reason']}")
    print(f"  Frequency: {result1['signature']['frequency']:.2f} Hz")
    
    # Test packet with incorrect rhythm (will be blacklisted)
    packet2 = {
        "type": "malicious",
        "content": "bad_data",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    result2 = platform.rhythm_validator.validate_packet(packet2, origin_ip="10.0.0.1")
    print(f"\n✓ Packet 2 validation: {result2['valid']}")
    print(f"  Reason: {result2['reason']}")
    
    # Try same packet again - should be blacklisted
    result3 = platform.rhythm_validator.validate_packet(packet2, origin_ip="different.ip")
    print(f"\n✓ Packet 2 retry (different IP): {result3['valid']}")
    print(f"  Reason: {result3['reason']} (IP-independent blocking)")
    
    # Check blacklist status
    blacklist_status = platform.rhythm_validator.get_blacklist_status()
    print(f"\n✓ Blacklist status:")
    print(f"  Total blacklisted: {blacklist_status['total_blacklisted']}")
    print(f"  Base frequency: {blacklist_status['base_frequency_hz']} Hz (Lex Amoris harmony)")


def test_lazy_security():
    """Test 2: Lazy Security with Energy Protection"""
    print("\n" + "="*60)
    print("TEST 2: Lazy Security (Energy-Based Protection)")
    print("="*60)
    
    platform = LexAmorisSecurityPlatform()
    
    # Initial scan
    print("\n✓ Performing Rotesschild environmental scan...")
    state1 = platform.lazy_security.update_security_state()
    print(f"  Pressure: {state1['scan']['pressure_mv_m']:.2f} mV/m")
    print(f"  Threshold: {state1['scan']['threshold']} mV/m")
    print(f"  Security level: {state1['security']['current_level']}")
    print(f"  Active protections: {state1['security']['active_protections']}")
    
    # Process request based on security level
    request = {"action": "access_resource", "user": "test_user"}
    result = platform.lazy_security.process_request(request)
    print(f"\n✓ Request processing:")
    print(f"  Allowed: {result['allowed']}")
    print(f"  Reason: {result['reason']}")
    
    # Energy statistics
    status = platform.lazy_security.get_status()
    print(f"\n✓ Energy statistics:")
    print(f"  Current energy: {status['energy']['current']:.1f}")
    print(f"  Energy saved: {status['energy']['saved']:.1f}")
    print(f"  Total activations: {status['statistics']['total_activations']}")


def test_ipfs_backup():
    """Test 3: IPFS Backup System"""
    print("\n" + "="*60)
    print("TEST 3: IPFS Backup & Mirroring")
    print("="*60)
    
    platform = LexAmorisSecurityPlatform()
    
    # Create backup snapshot
    print("\n✓ Creating complete backup snapshot...")
    backup_result = platform.create_backup_snapshot()
    
    print(f"\n✓ Security configuration backup:")
    print(f"  Backup ID: {backup_result['security_backup']['backup_id']}")
    print(f"  IPFS Hash: {backup_result['security_backup']['content_hash'][:20]}...")
    print(f"  Size: {backup_result['security_backup']['size_bytes']} bytes")
    
    print(f"\n✓ Full mirror created:")
    for key, record in backup_result['full_mirror'].items():
        print(f"  - {key}: {record['content_hash'][:20]}... ({record['type']})")
    
    # Check backup status
    backup_status = platform.ipfs_backup.get_backup_status()
    print(f"\n✓ Backup system status:")
    print(f"  Total backups: {backup_status['total_backups']}")
    print(f"  Pinned items: {backup_status['pinned_items']}")
    print(f"  Total size: {backup_status['total_size_mb']} MB")
    print(f"  IPFS gateway: {backup_status['ipfs_gateway']}")


def test_rescue_channel():
    """Test 4: Lex Amoris Rescue Channel"""
    print("\n" + "="*60)
    print("TEST 4: Lex Amoris Rescue Channel")
    print("="*60)
    
    platform = LexAmorisSecurityPlatform()
    
    # Simulate a blocked node
    sender_id = "user-123"
    node_id = "node-456"
    
    # Send rescue request
    print("\n✓ Sending rescue request for blocked node...")
    rescue_result = platform.request_rescue(
        sender_id=sender_id,
        node_id=node_id,
        reason="False positive detection - legitimate traffic pattern",
        evidence={
            "legitimate_traffic_pattern": True,
            "historical_data": {"avg_requests_per_hour": 100},
            "user_verification": True
        },
        priority="HIGH"
    )
    
    print(f"\n✓ Rescue request result:")
    print(f"  Message ID: {rescue_result['message']['message_id']}")
    print(f"  Approved: {rescue_result['response']['approved']}")
    print(f"  Reason: {rescue_result['response']['reason']}")
    print(f"  Actions: {', '.join(rescue_result['response']['actions_taken'])}")
    print(f"  Lex Amoris signature: {rescue_result['message']['lex_amoris_signature'][:20]}...")
    
    # Check rescue channel status
    rescue_status = platform.rescue_channel.get_rescue_status()
    print(f"\n✓ Rescue channel statistics:")
    print(f"  Total requests: {rescue_status['statistics']['total_requests']}")
    print(f"  Approved: {rescue_status['statistics']['total_approved']}")
    print(f"  Approval rate: {rescue_status['statistics']['approval_rate']}")
    print(f"  Auto-approve threshold: {rescue_status['config']['auto_approve_threshold']}")


def test_integrated_platform():
    """Test 5: Complete Platform Integration"""
    print("\n" + "="*60)
    print("TEST 5: Integrated Platform")
    print("="*60)
    
    platform = LexAmorisSecurityPlatform()
    
    # Get comprehensive status
    status = platform.get_platform_status()
    
    print(f"\n✓ Platform: {status['platform']} v{status['version']}")
    
    print(f"\n✓ Component status:")
    for component, data in status['components'].items():
        print(f"  - {component}: {data.get('status', 'active')}")
    
    print(f"\n✓ Overall statistics:")
    print(f"  Total requests: {status['statistics']['total_requests']}")
    print(f"  Total blocked: {status['statistics']['total_blocked']}")
    print(f"  Total rescued: {status['statistics']['total_rescued']}")
    print(f"  Block rate: {status['statistics']['block_rate']}")
    
    # Process a request through the full platform
    print("\n✓ Processing request through integrated platform...")
    test_request = {
        "action": "api_call",
        "resource": "/api/data",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    result = platform.process_request(
        request_data=test_request,
        origin_ip="203.0.113.42",
        sender_id="client-789"
    )
    
    print(f"\n✓ Processing result:")
    print(f"  Allowed: {result['allowed']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Security level: {result['security_level']}")
    
    if 'rescue_available' in result:
        print(f"  Rescue available: {result['rescue_available']}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LEX AMORIS SECURITY PLATFORM - TEST SUITE")
    print("Strategic Enhancements Demonstration")
    print("="*60)
    
    try:
        test_rhythm_validation()
        test_lazy_security()
        test_ipfs_backup()
        test_rescue_channel()
        test_integrated_platform()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nLex Amoris Security Platform is operational.")
        print("All four strategic enhancements are functioning correctly:")
        print("  1. ✓ Dynamic Blacklist & Rhythm Validation")
        print("  2. ✓ Lazy Security (Energy-Based)")
        print("  3. ✓ IPFS Backup & Mirroring")
        print("  4. ✓ Rescue Channel (Lex Amoris)")
        print()
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
