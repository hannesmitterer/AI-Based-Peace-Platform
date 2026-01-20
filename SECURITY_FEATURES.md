# Security and Resilience Features for Decentralized Operations

This repository implements comprehensive security and resilience features for decentralized peace platform operations, including real-time monitoring, forensic response automation, secure firmware updates, distributed backups, and hardened communication protocols.

## Features Implemented

### 1. Real-time Monitoring Dashboard (Grafana + Loki)

A complete monitoring stack for visualizing node status, latency, and intrusion detection logs.

**Components:**
- **Grafana**: Dashboard for real-time visualization
- **Loki**: Log aggregation and management
- **Prometheus**: Metrics collection and alerting
- **Promtail**: Log shipping to Loki

**Files:**
- `monitoring/grafana/` - Grafana configuration and dashboards
- `monitoring/loki/` - Loki configuration
- `monitoring/prometheus/` - Prometheus configuration and alerts
- `monitoring/promtail/` - Promtail configuration
- `docker-compose.monitoring.yml` - Docker Compose for monitoring stack

**Usage:**
```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana dashboard
open http://localhost:3001
# Default credentials: admin / (set in environment)

# Access Prometheus
open http://localhost:9090
```

**Dashboards:**
- Node Status Overview
- Network Latency Metrics
- Intrusion Detection Logs
- Failed Authentication Attempts
- Network Traffic Analysis

---

### 2. Forensic Response Automation

Automated security response system that monitors logs for suspicious activity and activates Tor/VPN routing when threats are detected.

**Components:**
- **Log Watcher**: Python-based log monitoring with threat detection
- **Tor Activation**: Automatic Tor routing for anonymization
- **VPN Activation**: Automatic VPN routing for secure communication
- **IP Blocking**: Automatic blocking of suspicious IP addresses

**Files:**
- `security/forensics/log_watcher.py` - Main log monitoring script
- `security/forensics/forensic_config.json` - Threat detection configuration
- `security/scripts/activate_tor.sh` - Tor routing activation script
- `security/scripts/activate_vpn.sh` - VPN routing activation script

**Usage:**
```bash
# Start forensic log watcher
python3 security/forensics/log_watcher.py

# Activate Tor routing manually
./security/scripts/activate_tor.sh start

# Activate VPN routing manually
./security/scripts/activate_vpn.sh start

# Check status
./security/scripts/activate_tor.sh status
./security/scripts/activate_vpn.sh status
```

**Threat Detection Patterns:**
- Brute force attacks
- Port scanning
- Intrusion attempts
- Suspicious login activity
- Malware detection
- DDoS attacks

**Automated Responses:**
- Activate Tor routing for critical threats
- Activate VPN routing for secure communication
- Block suspicious IP addresses
- Send security alerts
- Log all security events

---

### 3. Secure Firmware Updates

Secure firmware update mechanism with cryptographic signature verification and checksum validation.

**Components:**
- **Firmware Update Manager**: Python-based update system
- **Checksum Verification**: SHA-256 checksum validation
- **Signature Verification**: GPG cryptographic signature verification
- **Rollback Capability**: Automatic rollback on failure
- **Backup System**: Automatic backup before updates

**Files:**
- `firmware/firmware_updater.py` - Firmware update manager
- `firmware/updates/manifest_v1.0.0.json` - Update manifest template

**Usage:**
```bash
# Check for updates
python3 firmware/firmware_updater.py

# Apply update
python3 firmware/firmware_updater.py --apply --manifest firmware/updates/manifest_v1.0.0.json

# Rollback to previous version
python3 firmware/firmware_updater.py --rollback
```

**Security Features:**
- SHA-256 checksum verification
- GPG signature verification
- Automatic backup creation
- Post-installation verification
- Automatic rollback on failure
- Signed update manifests

---

### 4. Distributed Encrypted Backups (IPFS + GnuPG)

Autonomous encrypted backup system using IPFS for distributed storage and GnuPG for encryption.

**Components:**
- **IPFS Backup Manager**: Python-based backup system
- **GnuPG Encryption**: Automatic file encryption
- **IPFS Storage**: Distributed backup storage
- **Automated Scheduling**: Scheduled backup execution
- **Backup Verification**: Integrity checking

**Files:**
- `backup/ipfs_backup_manager.py` - IPFS backup manager
- `backup/scripts/automated_backup.sh` - Automated backup script
- `backup/ipfs/backup_config.json` - Backup configuration

**Usage:**
```bash
# Create manual backup
python3 backup/ipfs_backup_manager.py \
  --backup \
  --name "daily_backup" \
  --paths "/opt/data /etc/config" \
  --description "Daily backup"

# List backups
python3 backup/ipfs_backup_manager.py --list

# Restore backup
python3 backup/ipfs_backup_manager.py \
  --restore \
  --cid <IPFS_CID> \
  --output /opt/restore

# Run automated backup
./backup/scripts/automated_backup.sh
```

**Features:**
- GnuPG encryption before upload
- IPFS distributed storage
- Automatic CID pinning
- Backup verification
- Automated cleanup of old backups
- Configurable retention policies

**Backup Sets:**
- System configuration files
- Application data and databases
- Security and audit logs

---

### 5. Communication Protocol Hardening (QUIC + TLS 1.3)

Enhanced communication security using QUIC protocol with TLS 1.3 encryption, disabling all unencrypted communications.

**Components:**
- **QUIC Server**: Secure QUIC protocol server
- **TLS 1.3 Enforcer**: System-wide TLS 1.3 enforcement
- **Unencrypted Blocking**: Block HTTP and unencrypted protocols

**Files:**
- `communications/quic/quic_server.py` - QUIC server with TLS 1.3
- `communications/tls/tls13_enforcer.py` - TLS 1.3 enforcement
- `communications/tls/tls_config.toml` - TLS configuration

**Usage:**
```bash
# Start QUIC server
python3 communications/quic/quic_server.py

# Enforce TLS 1.3 system-wide
python3 communications/tls/tls13_enforcer.py

# Configure environment
export QUIC_HOST="0.0.0.0"
export QUIC_PORT="4433"
export QUIC_CERT="/etc/ssl/certs/quic-cert.pem"
export QUIC_KEY="/etc/ssl/private/quic-key.pem"
```

**Security Features:**
- TLS 1.3 only (older protocols disabled)
- Secure cipher suites:
  - TLS_AES_256_GCM_SHA384
  - TLS_CHACHA20_POLY1305_SHA256
  - TLS_AES_128_GCM_SHA256
- HTTP ports blocked
- HSTS enabled
- Certificate pinning support
- Forward secrecy
- No session tickets (prevents replay attacks)

---

## Installation

### Prerequisites

```bash
# System packages
sudo apt-get update
sudo apt-get install -y \
  python3 \
  python3-pip \
  docker.io \
  docker-compose \
  tor \
  openvpn \
  gnupg \
  ipfs \
  iptables

# Python packages
pip install -r requirements.txt
```

### Configuration

1. **Monitoring Stack:**
   ```bash
   # Set Grafana admin password
   export GRAFANA_ADMIN_PASSWORD="secure_password"
   export GRAFANA_SECRET_KEY="random_secret_key"
   
   # Start monitoring
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

2. **Forensic Response:**
   ```bash
   # Configure threat detection
   cp security/forensics/forensic_config.json /etc/security/forensic_config.json
   
   # Edit configuration
   nano /etc/security/forensic_config.json
   
   # Start log watcher
   python3 security/forensics/log_watcher.py
   ```

3. **Firmware Updates:**
   ```bash
   # Set up GPG keys
   gpg --gen-key
   export FIRMWARE_GPG_KEY="your_key_id"
   ```

4. **Backups:**
   ```bash
   # Start IPFS daemon
   ipfs daemon &
   
   # Set up GPG for backups
   export BACKUP_GPG_KEY="your_backup_key"
   
   # Configure backup schedule
   cp backup/ipfs/backup_config.json /etc/backup/backup_config.json
   ```

5. **QUIC/TLS:**
   ```bash
   # Generate certificates or use existing ones
   export QUIC_CERT="/path/to/cert.pem"
   export QUIC_KEY="/path/to/key.pem"
   
   # Start QUIC server
   python3 communications/quic/quic_server.py
   ```

---

## Security Considerations

### Threat Model

**Protected Against:**
- Network intrusion attempts
- Brute force attacks
- Man-in-the-middle attacks
- Protocol downgrade attacks
- Unencrypted data transmission
- Unauthorized firmware updates
- Data loss through distributed backups
- DDoS attacks

**Security Layers:**
1. Network layer: QUIC + TLS 1.3
2. Application layer: Authenticated APIs
3. Data layer: Encrypted backups
4. Monitoring layer: Real-time threat detection
5. Response layer: Automated forensic responses

### Best Practices

1. **Monitoring:**
   - Review Grafana dashboards daily
   - Set up alert notifications
   - Monitor failed authentication attempts
   - Check for anomalies in network traffic

2. **Backups:**
   - Run automated backups daily
   - Verify backups weekly
   - Test restore procedures monthly
   - Maintain 30-day retention

3. **Updates:**
   - Apply security updates promptly
   - Verify signatures before installing
   - Always backup before updates
   - Test rollback procedures

4. **Communications:**
   - Use TLS 1.3 exclusively
   - Rotate certificates regularly
   - Monitor for downgrade attempts
   - Disable all unencrypted endpoints

---

## Monitoring and Alerts

### Grafana Dashboards

Access: `http://localhost:3001`

**Available Dashboards:**
- Decentralized Node Monitoring
- Security Events
- Network Performance
- Backup Status

### Prometheus Alerts

**Critical Alerts:**
- Node down
- High authentication failures
- Suspicious intrusion activity
- Backup failures
- Certificate expiration

**Notification Channels:**
- Email
- Slack (optional)
- PagerDuty (optional)

---

## Maintenance

### Daily Tasks
- [ ] Review security logs
- [ ] Check monitoring dashboards
- [ ] Verify backup completion

### Weekly Tasks
- [ ] Verify backup integrity
- [ ] Review threat detection logs
- [ ] Update security configurations

### Monthly Tasks
- [ ] Rotate API keys
- [ ] Update certificates
- [ ] Test disaster recovery
- [ ] Review and update security policies

---

## Troubleshooting

### Monitoring Stack Not Starting

```bash
# Check Docker status
sudo systemctl status docker

# View logs
docker-compose -f docker-compose.monitoring.yml logs

# Restart services
docker-compose -f docker-compose.monitoring.yml restart
```

### Forensic Log Watcher Not Detecting Threats

```bash
# Check log file permissions
ls -la /var/log/auth.log

# Verify configuration
cat /etc/security/forensic_config.json

# Check Python dependencies
pip install -r requirements.txt
```

### IPFS Backup Failing

```bash
# Check IPFS daemon
ipfs swarm peers

# Restart IPFS
killall ipfs
ipfs daemon &

# Verify GPG key
gpg --list-keys
```

### TLS 1.3 Connection Issues

```bash
# Verify certificate
openssl x509 -in /etc/ssl/certs/quic-cert.pem -text

# Check TLS version
openssl s_client -connect localhost:4433 -tls1_3
```

---

## License

MIT License - See LICENSE file for details

---

## Contributing

Contributions are welcome! Please follow security best practices and test all changes thoroughly.

---

## Support

For issues and questions, please open a GitHub issue or contact the security team at security@example.com.
