#!/bin/bash
# VPN Router Activation Script
# Automatically activates VPN routing when suspicious activity is detected

set -e

LOG_FILE="/var/log/security/vpn_activation.log"
VPN_CONFIG="${VPN_CONFIG:-default}"
VPN_TYPE="${VPN_TYPE:-openvpn}"  # openvpn or wireguard

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

activate_openvpn() {
    log "Activating OpenVPN routing with config: $VPN_CONFIG..."
    
    # Check if OpenVPN is installed
    if ! command -v openvpn &> /dev/null; then
        log "ERROR: OpenVPN is not installed. Installing..."
        apt-get update && apt-get install -y openvpn
    fi
    
    # Start OpenVPN service
    systemctl start openvpn@$VPN_CONFIG
    systemctl enable openvpn@$VPN_CONFIG
    
    # Wait for VPN connection
    sleep 5
    
    # Check VPN interface
    if ip link show tun0 &> /dev/null; then
        log "SUCCESS: VPN interface tun0 is up"
    else
        log "ERROR: VPN interface not found"
        return 1
    fi
    
    # Route all traffic through VPN
    log "Configuring routing table for VPN..."
    
    # Get VPN gateway
    VPN_GATEWAY=$(ip route | grep tun0 | awk '{print $1}' | head -1)
    
    # Add default route through VPN
    ip route add default via $VPN_GATEWAY dev tun0
    
    log "OpenVPN routing activated successfully"
}

activate_wireguard() {
    log "Activating WireGuard VPN with config: $VPN_CONFIG..."
    
    # Check if WireGuard is installed
    if ! command -v wg &> /dev/null; then
        log "ERROR: WireGuard is not installed. Installing..."
        apt-get update && apt-get install -y wireguard
    fi
    
    # Start WireGuard interface
    wg-quick up $VPN_CONFIG
    
    log "WireGuard VPN activated successfully"
}

deactivate_vpn() {
    log "Deactivating VPN routing..."
    
    if [ "$VPN_TYPE" = "wireguard" ]; then
        wg-quick down $VPN_CONFIG || true
    else
        systemctl stop openvpn@$VPN_CONFIG || true
    fi
    
    # Restore default routing
    ip route del default via tun0 2>/dev/null || true
    
    log "VPN routing deactivated"
}

check_vpn_status() {
    if [ "$VPN_TYPE" = "wireguard" ]; then
        if wg show $VPN_CONFIG &> /dev/null; then
            log "WireGuard VPN is ACTIVE"
            wg show $VPN_CONFIG
            return 0
        fi
    else
        if systemctl is-active --quiet openvpn@$VPN_CONFIG; then
            log "OpenVPN is ACTIVE"
            return 0
        fi
    fi
    
    log "VPN is INACTIVE"
    return 1
}

case "$1" in
    start|activate)
        if [ "$VPN_TYPE" = "wireguard" ]; then
            activate_wireguard
        else
            activate_openvpn
        fi
        ;;
    stop|deactivate)
        deactivate_vpn
        ;;
    status)
        check_vpn_status
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        echo "Environment variables:"
        echo "  VPN_CONFIG - VPN configuration name (default: default)"
        echo "  VPN_TYPE - VPN type: openvpn or wireguard (default: openvpn)"
        exit 1
        ;;
esac
