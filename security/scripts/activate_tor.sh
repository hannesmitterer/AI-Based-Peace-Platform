#!/bin/bash
# Tor Router Activation Script
# Automatically activates Tor routing when suspicious activity is detected

set -e

LOG_FILE="/var/log/security/tor_activation.log"
TOR_CONFIG="/etc/tor/torrc"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

activate_tor() {
    log "Activating Tor routing..."
    
    # Check if Tor is installed
    if ! command -v tor &> /dev/null; then
        log "ERROR: Tor is not installed. Installing..."
        apt-get update && apt-get install -y tor
    fi
    
    # Configure Tor
    if [ ! -f "$TOR_CONFIG" ]; then
        log "Creating Tor configuration..."
        cat > "$TOR_CONFIG" << EOF
# Tor Configuration for Forensic Response
SocksPort 9050
DNSPort 53
TransPort 9040
Log notice file /var/log/tor/notices.log
AutomapHostsOnResolve 1
ExitPolicy reject *:*
EOF
    fi
    
    # Start Tor service
    log "Starting Tor service..."
    systemctl start tor
    systemctl enable tor
    
    # Wait for Tor to establish connection
    sleep 5
    
    # Backup existing iptables rules
    log "Backing up existing iptables rules..."
    iptables-save > /tmp/iptables.backup
    
    # Configure iptables to route traffic through Tor
    log "Configuring iptables for Tor routing..."
    
    # Create new nat chain for Tor
    iptables -t nat -N TOR || true
    
    # Allow established connections
    iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    
    # Allow localhost
    iptables -A INPUT -i lo -j ACCEPT
    
    # Redirect DNS to Tor
    iptables -t nat -A TOR -p udp --dport 53 -j REDIRECT --to-ports 53
    
    # Redirect TCP traffic to Tor (transparent proxy port)
    iptables -t nat -A TOR -p tcp --syn -j REDIRECT --to-ports 9040
    
    # Apply TOR chain to OUTPUT
    iptables -t nat -A OUTPUT -j TOR
    
    # Save iptables rules
    iptables-save > /etc/iptables/rules.v4
    
    log "Tor routing activated successfully"
    log "All traffic is now being routed through Tor network"
    
    # Verify Tor connection
    if curl --socks5 localhost:9050 --socks5-hostname localhost:9050 -s https://check.torproject.org/ | grep -q "Congratulations"; then
        log "SUCCESS: Tor connection verified"
    else
        log "WARNING: Could not verify Tor connection"
    fi
}

deactivate_tor() {
    log "Deactivating Tor routing..."
    
    # Restore iptables rules from backup
    if [ -f /tmp/iptables.backup ]; then
        log "Restoring iptables rules from backup..."
        iptables-restore < /tmp/iptables.backup
    else
        # Fallback: remove Tor chain
        iptables -t nat -D OUTPUT -j TOR 2>/dev/null || true
        iptables -t nat -F TOR 2>/dev/null || true
        iptables -t nat -X TOR 2>/dev/null || true
    fi
    
    # Stop Tor service
    systemctl stop tor
    
    log "Tor routing deactivated"
}

case "$1" in
    start|activate)
        activate_tor
        ;;
    stop|deactivate)
        deactivate_tor
        ;;
    status)
        if systemctl is-active --quiet tor; then
            log "Tor is ACTIVE"
            exit 0
        else
            log "Tor is INACTIVE"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac
