#!/usr/bin/env python3
"""
Forensic Log Watcher
Monitors security logs for suspicious activity and triggers automated responses
including Tor/VPN routing activation.
"""

import os
import re
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/security/forensic_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ForensicWatcher')

# Configuration
CONFIG_FILE = os.getenv('FORENSIC_CONFIG', '/etc/security/forensic_config.json')
LOG_PATHS = [
    '/var/log/auth.log',
    '/var/log/security/intrusion.log',
    '/var/log/syslog'
]

# Threat patterns
THREAT_PATTERNS = {
    'brute_force': r'Failed password for .* from ([\d.]+)',
    'port_scan': r'Port scan detected from ([\d.]+)',
    'intrusion_attempt': r'Intrusion attempt.*from ([\d.]+)',
    'suspicious_login': r'Suspicious login.*from ([\d.]+)',
    'malware_detection': r'Malware detected',
    'ddos_attack': r'DDoS.*from ([\d.]+)',
}

# Track suspicious IPs
suspicious_ips: Set[str] = set()
threat_counter: Dict[str, int] = {}


class ForensicResponse:
    """Handles automated forensic responses to security threats"""
    
    def __init__(self):
        self.tor_enabled = False
        self.vpn_enabled = False
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if Path(CONFIG_FILE).exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.tor_enabled = config.get('enable_tor', False)
                    self.vpn_enabled = config.get('enable_vpn', False)
            else:
                logger.warning(f"Config file not found: {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    def activate_tor_routing(self):
        """Activate Tor routing for anonymization"""
        if not self.tor_enabled:
            logger.info("Tor routing is disabled in configuration")
            return False
        
        try:
            logger.warning("ACTIVATING TOR ROUTING - Threat detected")
            
            # Start Tor service
            subprocess.run(['systemctl', 'start', 'tor'], check=False)
            time.sleep(2)
            
            # Configure iptables to route through Tor
            commands = [
                ['iptables', '-t', 'nat', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '80', '-j', 'REDIRECT', '--to-ports', '9050'],
                ['iptables', '-t', 'nat', '-A', 'OUTPUT', '-p', 'tcp', '--dport', '443', '-j', 'REDIRECT', '--to-ports', '9050'],
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Failed to configure Tor routing: {result.stderr}")
            
            logger.info("Tor routing activated successfully")
            return True
        except Exception as e:
            logger.error(f"Error activating Tor routing: {e}")
            return False
    
    def activate_vpn_routing(self, vpn_config='default'):
        """Activate VPN routing for secure communication"""
        if not self.vpn_enabled:
            logger.info("VPN routing is disabled in configuration")
            return False
        
        try:
            logger.warning("ACTIVATING VPN ROUTING - Threat detected")
            
            # Start OpenVPN or WireGuard
            subprocess.run(['systemctl', 'start', f'openvpn@{vpn_config}'], check=False)
            
            logger.info(f"VPN routing activated with config: {vpn_config}")
            return True
        except Exception as e:
            logger.error(f"Error activating VPN routing: {e}")
            return False
    
    def block_ip(self, ip_address: str):
        """Block suspicious IP address"""
        try:
            logger.warning(f"BLOCKING IP: {ip_address}")
            
            # Add to iptables DROP chain
            subprocess.run(
                ['iptables', '-A', 'INPUT', '-s', ip_address, '-j', 'DROP'],
                check=False
            )
            
            # Add to fail2ban
            subprocess.run(
                ['fail2ban-client', 'set', 'sshd', 'banip', ip_address],
                check=False
            )
            
            suspicious_ips.add(ip_address)
            logger.info(f"IP {ip_address} blocked successfully")
            return True
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address}: {e}")
            return False
    
    def send_alert(self, threat_type: str, details: str):
        """Send security alert to monitoring system"""
        try:
            alert_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'threat_type': threat_type,
                'details': details,
                'severity': 'critical',
                'action_taken': 'Automated response activated'
            }
            
            # Log to security log
            logger.critical(f"SECURITY ALERT: {json.dumps(alert_data)}")
            
            # Could integrate with external alerting systems here
            # e.g., Slack, PagerDuty, email, etc.
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")


class LogWatcher:
    """Monitors log files for suspicious activity"""
    
    def __init__(self, log_paths: List[str]):
        self.log_paths = log_paths
        self.file_positions: Dict[str, int] = {}
        self.response = ForensicResponse()
        
        # Initialize file positions
        for log_path in log_paths:
            if Path(log_path).exists():
                self.file_positions[log_path] = 0
    
    def check_threat_threshold(self, threat_type: str) -> bool:
        """Check if threat threshold is exceeded"""
        threat_counter[threat_type] = threat_counter.get(threat_type, 0) + 1
        
        # Thresholds for different threat types
        thresholds = {
            'brute_force': 5,
            'port_scan': 3,
            'intrusion_attempt': 1,
            'suspicious_login': 3,
            'malware_detection': 1,
            'ddos_attack': 1,
        }
        
        return threat_counter[threat_type] >= thresholds.get(threat_type, 5)
    
    def analyze_log_line(self, line: str) -> None:
        """Analyze a log line for threats"""
        for threat_type, pattern in THREAT_PATTERNS.items():
            match = re.search(pattern, line)
            if match:
                logger.warning(f"Threat detected: {threat_type} - {line.strip()}")
                
                # Extract IP if available
                ip_address = match.group(1) if match.groups() else None
                
                # Check if threshold exceeded
                if self.check_threat_threshold(threat_type):
                    logger.critical(f"THREAT THRESHOLD EXCEEDED: {threat_type}")
                    
                    # Take automated action
                    if threat_type in ['intrusion_attempt', 'malware_detection', 'ddos_attack']:
                        self.response.activate_tor_routing()
                        self.response.activate_vpn_routing()
                    
                    if ip_address:
                        self.response.block_ip(ip_address)
                    
                    self.response.send_alert(threat_type, line.strip())
    
    def watch_logs(self):
        """Continuously monitor log files"""
        logger.info("Starting forensic log watcher...")
        logger.info(f"Monitoring: {', '.join(self.log_paths)}")
        
        while True:
            try:
                for log_path in self.log_paths:
                    if not Path(log_path).exists():
                        continue
                    
                    with open(log_path, 'r') as f:
                        # Seek to last known position
                        f.seek(self.file_positions.get(log_path, 0))
                        
                        # Read new lines
                        for line in f:
                            self.analyze_log_line(line)
                        
                        # Update position
                        self.file_positions[log_path] = f.tell()
                
                time.sleep(1)  # Check logs every second
                
            except KeyboardInterrupt:
                logger.info("Forensic log watcher stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in log watcher: {e}")
                time.sleep(5)


def main():
    """Main entry point"""
    logger.info("Forensic Log Watcher starting...")
    
    # Create log directories if they don't exist
    Path('/var/log/security').mkdir(parents=True, exist_ok=True)
    
    # Start watching logs
    watcher = LogWatcher(LOG_PATHS)
    watcher.watch_logs()


if __name__ == '__main__':
    main()
