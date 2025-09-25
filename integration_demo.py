"""
Euystacio Integration Example - Demonstrates the complete self-defense system

This example shows how all modules work together to provide comprehensive
protection for the euystacio-helmi-ai kernel system.
"""

from euystacio_core import get_current_state, update_kernel_state, validate_input_integrity
from euystacio_response import activate_safe_mode, send_alert, get_system_status
from euystacio_audit_log import log_event, verify_audit_integrity, get_audit_report
from euystacio_helmi_guardian import EuystacioHelmiGuardian
import time
import json

def demonstrate_integration():
    """Comprehensive demonstration of the integrated self-defense system"""
    
    print("=== Euystacio Unified Self-Defense Integration Demonstration ===\n")
    
    # Initialize guardian system
    guardian = EuystacioHelmiGuardian()
    print("1. Guardian system initialized")
    
    # Start monitoring
    guardian.start_monitoring() 
    print("2. Guardian monitoring started")
    
    # Demonstrate normal operation
    print("\n--- Normal Operation ---")
    initial_state = get_current_state()
    print(f"Initial state: Trust={initial_state['trust']}, Harmony={initial_state['harmony']}")
    
    # Test valid input processing
    valid_input = {'emotion': 'Love', 'context': 'Peaceful'}
    if guardian.validate_input(valid_input):
        update_kernel_state({'trust': 0.9, 'harmony': 0.95}, 'demonstration')
        print(f"✓ Valid input processed successfully")
    
    # Demonstrate threat detection
    print("\n--- Threat Detection Simulation ---")
    
    # Simulate suspicious input
    suspicious_input = {'emotion': 'Anger', 'context': 'Calm'}
    if not guardian.validate_input(suspicious_input):
        print("⚠ Suspicious input detected and quarantined")
    
    # Simulate anomalous state
    update_kernel_state({'trust': 0.2, 'harmony': 0.1}, 'threat_simulation')
    print("⚠ Simulated threat state: Low trust and harmony")
    
    # Allow guardian to detect and respond
    time.sleep(2)
    
    # Check system status
    status = get_system_status()
    print(f"System status: {status['alert_level']}, Safe mode: {status['safe_mode_active']}")
    
    # Demonstrate audit capabilities
    print("\n--- Audit System Verification ---")
    integrity_report = verify_audit_integrity()
    print(f"Audit integrity status: {integrity_report['status']}")
    
    audit_report = get_audit_report()
    print(f"Recent events (24h): {audit_report['recent_activity_summary']['total_events_24h']}")
    
    # Guardian status
    guardian_status = guardian.get_guardian_status()
    print(f"Guardian monitoring: {guardian_status['monitoring_active']}")
    print(f"Recent anomalies: {guardian_status['recent_anomalies']}")
    
    # Stop monitoring
    guardian.stop_monitoring()
    print("\n3. Guardian monitoring stopped")
    
    print("\n=== Integration Demonstration Complete ===")

def run_security_tests():
    """Run comprehensive security validation tests"""
    
    print("\n=== Security Validation Tests ===\n")
    
    guardian = EuystacioHelmiGuardian()
    test_results = []
    
    # Test 1: Input validation
    print("Test 1: Input Validation")
    test_inputs = [
        ({'emotion': 'Love', 'context': 'Calm'}, True, "Valid input"),
        ({'emotion': 'InvalidEmotion', 'context': 'Calm'}, False, "Invalid emotion"),
        ({'emotion': 'Anger'}, False, "Missing context field"),
        ({'emotion': 'Love', 'context': 'Crisis'}, False, "Suspicious combination")
    ]
    
    for input_data, expected, description in test_inputs:
        result = guardian.validate_input(input_data)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"  {description}: {status}")
        test_results.append(result == expected)
    
    # Test 2: State integrity
    print("\nTest 2: State Integrity")
    initial_state = get_current_state()
    update_result = update_kernel_state({'trust': 0.5}, 'security_test')
    integrity_valid = initial_state is not None and update_result
    status = "✓ PASS" if integrity_valid else "✗ FAIL"
    print(f"  State integrity: {status}")
    test_results.append(integrity_valid)
    
    # Test 3: Audit logging
    print("\nTest 3: Audit Logging")
    log_event("security_test", {"test": "audit_functionality"}, "high")
    audit_integrity = verify_audit_integrity()
    audit_valid = audit_integrity['status'] in ['verified', 'empty']
    status = "✓ PASS" if audit_valid else "✗ FAIL"
    print(f"  Audit integrity: {status}")
    test_results.append(audit_valid)
    
    # Test 4: Guardian monitoring
    print("\nTest 4: Guardian Monitoring")
    guardian_status = guardian.get_guardian_status()
    monitoring_valid = 'monitoring_active' in guardian_status
    status = "✓ PASS" if monitoring_valid else "✗ FAIL"
    print(f"  Guardian status: {status}")
    test_results.append(monitoring_valid)
    
    # Results summary
    passed = sum(test_results)
    total = len(test_results)
    print(f"\n=== Test Results: {passed}/{total} tests passed ===")
    
    return all(test_results)

if __name__ == "__main__":
    # Run integration demonstration
    demonstrate_integration()
    
    # Run security tests
    all_tests_passed = run_security_tests()
    
    if all_tests_passed:
        print("\n🎉 All integration tests passed! System ready for deployment.")
    else:
        print("\n⚠️  Some tests failed. Please review system configuration.")