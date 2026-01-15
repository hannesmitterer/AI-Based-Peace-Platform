#!/usr/bin/env python3
"""
Lex Amoris Security Platform - Usage Example
Demonstrates integration of all four strategic enhancements.
"""

import time
import traceback
from datetime import datetime
from lex_amoris_integration import LexAmorisSecurityPlatform


def print_header(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_rhythm_validation():
    """Example: Using rhythm validation"""
    print_header("Example 1: Rhythm Validation & Dynamic Blacklist")
    
    platform = LexAmorisSecurityPlatform()
    
    # Simulate incoming packets
    packets = [
        {"type": "login", "user": "alice", "timestamp": datetime.utcnow().isoformat()},
        {"type": "data_request", "resource": "/api/users"},
        {"type": "malicious_probe", "payload": "exploit_attempt"},
    ]
    
    print("\nValidating incoming packets...")
    for i, packet in enumerate(packets, 1):
        result = platform.rhythm_validator.validate_packet(packet)
        status = "✓ PASS" if result['valid'] else "✗ FAIL"
        print(f"\nPacket {i}: {status}")
        print(f"  Type: {packet['type']}")
        print(f"  Reason: {result['reason']}")
        if not result['valid'] and 'signature' in result:
            print(f"  Frequency: {result['signature']['frequency']:.2f} Hz")
            print(f"  Expected: {result['signature']['expected_frequency']} Hz")
    
    # Show blacklist status
    blacklist = platform.rhythm_validator.get_blacklist_status()
    print(f"\n📋 Blacklist Status:")
    print(f"   Total blacklisted: {blacklist['total_blacklisted']}")
    print(f"   Duration: {blacklist['blacklist_duration_seconds']} seconds")


def example_lazy_security():
    """Example: Using lazy security"""
    print_header("Example 2: Lazy Security with Environmental Scanning")
    
    platform = LexAmorisSecurityPlatform()
    
    print("\nPerforming environmental scans over time...")
    for i in range(3):
        state = platform.lazy_security.update_security_state()
        
        print(f"\n⚡ Scan {i+1}:")
        print(f"   Pressure: {state['scan']['pressure_mv_m']:.2f} mV/m")
        print(f"   Threshold: {state['scan']['threshold']} mV/m")
        print(f"   Security Level: {state['security']['current_level']}")
        print(f"   Active Protections: {len(state['security']['active_protections'])}")
        print(f"   Energy Remaining: {state['security']['energy_remaining']:.1f}")
        
        time.sleep(0.1)  # Small delay between scans
    
    # Show energy statistics
    status = platform.lazy_security.get_status()
    print(f"\n💡 Energy Statistics:")
    print(f"   Energy saved: {status['energy']['saved']:.1f} units")
    print(f"   Total activations: {status['statistics']['total_activations']}")


def example_ipfs_backup():
    """Example: Using IPFS backup"""
    print_header("Example 3: IPFS Backup & Mirroring")
    
    platform = LexAmorisSecurityPlatform()
    
    print("\n💾 Creating backup snapshot...")
    backup = platform.create_backup_snapshot()
    
    print(f"\n✓ Security Configuration Backup:")
    print(f"   Backup ID: {backup['security_backup']['backup_id']}")
    print(f"   IPFS Hash: {backup['security_backup']['content_hash'][:32]}...")
    print(f"   Size: {backup['security_backup']['size_bytes']} bytes")
    
    print(f"\n✓ Full Repository Mirror:")
    for key, record in backup['full_mirror'].items():
        print(f"   {key:12} -> {record['content_hash'][:32]}... ({record['type']})")
    
    # List recent backups
    backups = platform.ipfs_backup.list_backups(limit=5)
    print(f"\n📚 Recent Backups: {len(backups)} total")
    
    # Show backup status
    status = platform.ipfs_backup.get_backup_status()
    print(f"\n📊 Backup Status:")
    print(f"   Total backups: {status['total_backups']}")
    print(f"   Pinned items: {status['pinned_items']}")
    print(f"   Total size: {status['total_size_mb']} MB")


def example_rescue_channel():
    """Example: Using rescue channel"""
    print_header("Example 4: Rescue Channel for False Positives")
    
    platform = LexAmorisSecurityPlatform()
    
    print("\n🆘 Requesting rescue for blocked node...")
    
    # Create a rescue request
    result = platform.request_rescue(
        sender_id="admin-001",
        node_id="production-server-42",
        reason="Legitimate traffic pattern incorrectly flagged",
        evidence={
            "legitimate_traffic_pattern": True,
            "historical_data": {
                "avg_requests_per_hour": 150,
                "uptime_days": 365,
                "error_rate": 0.001
            },
            "user_verification": True,
            "third_party_validation": True
        },
        priority="HIGH"
    )
    
    print(f"\n✓ Rescue Request Submitted:")
    print(f"   Message ID: {result['message']['message_id']}")
    print(f"   Node ID: {result['message']['node_id']}")
    print(f"   Priority: {result['message']['priority']}")
    
    print(f"\n✓ Rescue Response:")
    print(f"   Approved: {'YES' if result['response']['approved'] else 'NO'}")
    print(f"   Reason: {result['response']['reason']}")
    print(f"   Actions: {', '.join(result['response']['actions_taken'])}")
    
    # Show rescue channel statistics
    status = platform.rescue_channel.get_rescue_status()
    print(f"\n📈 Rescue Channel Statistics:")
    print(f"   Total requests: {status['statistics']['total_requests']}")
    print(f"   Approval rate: {status['statistics']['approval_rate'] * 100:.0f}%")
    print(f"   Auto-approve threshold: {status['config']['auto_approve_threshold']}")


def example_integrated_workflow():
    """Example: Complete integrated workflow"""
    print_header("Example 5: Complete Integrated Workflow")
    
    platform = LexAmorisSecurityPlatform()
    
    print("\n🔄 Processing requests through complete security stack...")
    
    # Simulate different types of requests
    test_cases = [
        {
            "name": "Normal API Request",
            "data": {"action": "fetch_data", "user": "alice"},
            "sender": "client-001",
            "ip": "203.0.113.1"
        },
        {
            "name": "High-Volume Request",
            "data": {"action": "bulk_export", "records": 10000},
            "sender": "client-002",
            "ip": "203.0.113.2"
        },
        {
            "name": "Sensitive Operation",
            "data": {"action": "delete_records", "count": 5},
            "sender": "admin-003",
            "ip": "203.0.113.3"
        }
    ]
    
    for test in test_cases:
        print(f"\n📦 Processing: {test['name']}")
        
        result = platform.process_request(
            request_data=test['data'],
            origin_ip=test['ip'],
            sender_id=test['sender']
        )
        
        status = "✓ ALLOWED" if result['allowed'] else "✗ BLOCKED"
        print(f"   Status: {status}")
        print(f"   Reason: {result['reason']}")
        print(f"   Security Level: {result['security_level']}")
        
        if not result['allowed'] and result.get('rescue_available'):
            print(f"   💡 Rescue channel available for appeal")
    
    # Show comprehensive platform status
    print(f"\n📊 Platform Status:")
    status = platform.get_platform_status()
    print(f"   Total requests: {status['statistics']['total_requests']}")
    print(f"   Blocked: {status['statistics']['total_blocked']}")
    print(f"   Rescued: {status['statistics']['total_rescued']}")
    print(f"   Block rate: {status['statistics']['block_rate'] * 100:.1f}%")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("  LEX AMORIS SECURITY PLATFORM - USAGE EXAMPLES")
    print("  Demonstrating Strategic Enhancements")
    print("=" * 70)
    
    try:
        example_rhythm_validation()
        example_lazy_security()
        example_ipfs_backup()
        example_rescue_channel()
        example_integrated_workflow()
        
        print("\n" + "=" * 70)
        print("  ✓ All examples completed successfully!")
        print("=" * 70)
        print("\n  The Lex Amoris Security Platform provides:")
        print("    🎵 Rhythm-based validation (432 Hz harmony)")
        print("    ⚡ Energy-efficient security (lazy activation)")
        print("    💾 Distributed IPFS backups")
        print("    🆘 Compassionate rescue channel")
        print("\n  Made with 🕊️ and ❤️ following Lex Amoris principles\n")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
