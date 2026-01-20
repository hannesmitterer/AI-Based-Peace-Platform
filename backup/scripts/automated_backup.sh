#!/bin/bash
# Automated Backup Script for IPFS
# Runs scheduled encrypted backups to IPFS

set -e

LOG_FILE="/var/log/backup/automated_backup.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_MANAGER="$SCRIPT_DIR/../ipfs_backup_manager.py"
BACKUP_CONFIG="${BACKUP_CONFIG:-/etc/backup/backup_config.json}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if IPFS daemon is running
check_ipfs() {
    if ! ipfs swarm peers > /dev/null 2>&1; then
        log "ERROR: IPFS daemon is not running"
        log "Starting IPFS daemon..."
        ipfs daemon &
        sleep 5
    fi
    log "✓ IPFS daemon is running"
}

# Load backup configuration
load_config() {
    if [ ! -f "$BACKUP_CONFIG" ]; then
        log "ERROR: Backup configuration not found: $BACKUP_CONFIG"
        exit 1
    fi
    
    log "Loading backup configuration..."
}

# Perform backup
perform_backup() {
    local backup_name=$1
    local backup_paths=$2
    
    log "Starting backup: $backup_name"
    log "Paths: $backup_paths"
    
    # Run Python backup manager
    python3 "$BACKUP_MANAGER" --backup \
        --name "$backup_name" \
        --paths "$backup_paths" \
        --description "Automated backup on $(date)"
    
    if [ $? -eq 0 ]; then
        log "✓ Backup completed successfully"
    else
        log "✗ Backup failed"
        exit 1
    fi
}

# Verify backups
verify_backups() {
    log "Verifying backups..."
    
    python3 "$BACKUP_MANAGER" --verify-all
    
    if [ $? -eq 0 ]; then
        log "✓ All backups verified"
    else
        log "⚠ Some backups could not be verified"
    fi
}

# Clean old backups
cleanup_old_backups() {
    local retention_days=${RETENTION_DAYS:-30}
    
    log "Cleaning backups older than $retention_days days..."
    
    find /opt/backups -name "*.tar.gz" -mtime +$retention_days -delete
    find /opt/backups -name "*.gpg" -mtime +$retention_days -delete
    
    log "✓ Cleanup completed"
}

main() {
    log "=== Automated Backup Starting ==="
    
    # Check prerequisites
    check_ipfs
    
    # Load configuration
    load_config
    
    # Perform backups based on config
    # Example: backup critical directories
    perform_backup "system_config" "/etc /opt/config"
    perform_backup "application_data" "/opt/data /var/lib/app"
    
    # Verify backups
    verify_backups
    
    # Cleanup old backups
    cleanup_old_backups
    
    log "=== Automated Backup Completed ==="
}

# Run main function
main
