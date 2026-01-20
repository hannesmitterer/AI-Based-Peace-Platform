#!/usr/bin/env python3
"""
Secure Firmware Update Manager
Implements secure firmware updates with checksum verification and cryptographic signatures
"""

import os
import hashlib
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import gnupg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/firmware/update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FirmwareUpdate')

# Configuration
FIRMWARE_DIR = Path('/opt/firmware')
UPDATE_DIR = Path('/opt/firmware/updates')
BACKUP_DIR = Path('/opt/firmware/backups')
GPG_HOME = Path.home() / '.gnupg'
TRUSTED_KEY_ID = os.getenv('FIRMWARE_GPG_KEY', 'firmware-signing-key')


class FirmwareUpdateManager:
    """Manages secure firmware updates with verification"""
    
    def __init__(self):
        self.gpg = gnupg.GPG(gnupghome=str(GPG_HOME))
        self.current_version = self.get_current_version()
        
        # Ensure directories exist
        FIRMWARE_DIR.mkdir(parents=True, exist_ok=True)
        UPDATE_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_current_version(self) -> str:
        """Get current firmware version"""
        version_file = FIRMWARE_DIR / 'version.json'
        if version_file.exists():
            with open(version_file, 'r') as f:
                data = json.load(f)
                return data.get('version', '0.0.0')
        return '0.0.0'
    
    def calculate_checksum(self, file_path: Path, algorithm='sha256') -> str:
        """Calculate file checksum"""
        logger.info(f"Calculating {algorithm} checksum for {file_path}")
        
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        
        checksum = hash_func.hexdigest()
        logger.info(f"Checksum: {checksum}")
        return checksum
    
    def verify_checksum(self, file_path: Path, expected_checksum: str, algorithm='sha256') -> bool:
        """Verify file checksum"""
        logger.info(f"Verifying checksum for {file_path}")
        
        actual_checksum = self.calculate_checksum(file_path, algorithm)
        
        if actual_checksum == expected_checksum:
            logger.info("✓ Checksum verification PASSED")
            return True
        else:
            logger.error(f"✗ Checksum verification FAILED")
            logger.error(f"  Expected: {expected_checksum}")
            logger.error(f"  Actual:   {actual_checksum}")
            return False
    
    def verify_signature(self, file_path: Path, signature_path: Path) -> bool:
        """Verify cryptographic signature using GPG"""
        logger.info(f"Verifying GPG signature for {file_path}")
        
        try:
            with open(signature_path, 'rb') as sig_file:
                verified = self.gpg.verify_file(sig_file, str(file_path))
            
            if verified:
                logger.info(f"✓ Signature verification PASSED")
                logger.info(f"  Signed by: {verified.username}")
                logger.info(f"  Key ID: {verified.key_id}")
                logger.info(f"  Timestamp: {verified.timestamp}")
                return True
            else:
                logger.error("✗ Signature verification FAILED")
                logger.error(f"  Status: {verified.status}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
    
    def create_signature(self, file_path: Path, key_id: str) -> Path:
        """Create cryptographic signature for firmware file"""
        logger.info(f"Creating signature for {file_path}")
        
        signature_path = Path(str(file_path) + '.sig')
        
        with open(file_path, 'rb') as f:
            signed_data = self.gpg.sign_file(
                f,
                keyid=key_id,
                detach=True,
                output=str(signature_path)
            )
        
        if signed_data:
            logger.info(f"✓ Signature created: {signature_path}")
            return signature_path
        else:
            logger.error("✗ Failed to create signature")
            raise Exception("Signature creation failed")
    
    def backup_current_firmware(self) -> Path:
        """Create backup of current firmware"""
        logger.info("Creating backup of current firmware...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = BACKUP_DIR / f"firmware_v{self.current_version}_{timestamp}.tar.gz"
        
        # Create tar archive
        subprocess.run([
            'tar', 'czf', str(backup_file),
            '-C', str(FIRMWARE_DIR.parent),
            FIRMWARE_DIR.name
        ], check=True)
        
        logger.info(f"✓ Backup created: {backup_file}")
        return backup_file
    
    def rollback(self, backup_file: Optional[Path] = None) -> bool:
        """Rollback to previous firmware version"""
        logger.warning("ROLLING BACK firmware...")
        
        if backup_file is None:
            # Find latest backup
            backups = sorted(BACKUP_DIR.glob('firmware_*.tar.gz'), reverse=True)
            if not backups:
                logger.error("No backup available for rollback")
                return False
            backup_file = backups[0]
        
        logger.info(f"Rolling back to: {backup_file}")
        
        try:
            # Extract backup
            subprocess.run([
                'tar', 'xzf', str(backup_file),
                '-C', str(FIRMWARE_DIR.parent),
                '--overwrite'
            ], check=True)
            
            logger.info("✓ Rollback successful")
            return True
            
        except Exception as e:
            logger.error(f"✗ Rollback failed: {e}")
            return False
    
    def apply_update(self, update_package: Path, manifest: Dict) -> bool:
        """Apply firmware update with verification"""
        logger.info(f"Applying firmware update: {update_package}")
        
        try:
            # 1. Verify checksum
            expected_checksum = manifest.get('checksum')
            if not self.verify_checksum(update_package, expected_checksum):
                logger.error("Update rejected: Checksum verification failed")
                return False
            
            # 2. Verify signature
            signature_file = Path(str(update_package) + '.sig')
            if not signature_file.exists():
                logger.error("Update rejected: Signature file not found")
                return False
            
            if not self.verify_signature(update_package, signature_file):
                logger.error("Update rejected: Signature verification failed")
                return False
            
            # 3. Create backup
            backup_file = self.backup_current_firmware()
            
            # 4. Extract update
            logger.info("Extracting firmware update...")
            subprocess.run([
                'tar', 'xzf', str(update_package),
                '-C', str(FIRMWARE_DIR),
                '--overwrite'
            ], check=True)
            
            # 5. Verify installation
            new_version = self.get_current_version()
            logger.info(f"Updated from version {self.current_version} to {new_version}")
            
            # 6. Run post-install checks
            if not self.verify_installation():
                logger.error("Post-installation verification failed, rolling back...")
                self.rollback(backup_file)
                return False
            
            logger.info("✓ Firmware update applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            logger.error("Rolling back...")
            self.rollback(backup_file)
            return False
    
    def verify_installation(self) -> bool:
        """Verify firmware installation integrity"""
        logger.info("Verifying firmware installation...")
        
        # Check critical files exist
        critical_files = ['version.json', 'manifest.json']
        for filename in critical_files:
            file_path = FIRMWARE_DIR / filename
            if not file_path.exists():
                logger.error(f"Critical file missing: {filename}")
                return False
        
        logger.info("✓ Installation verification passed")
        return True
    
    def check_for_updates(self, update_server: str) -> Optional[Dict]:
        """Check for available firmware updates"""
        logger.info(f"Checking for updates from: {update_server}")
        
        # This would typically make an API call to the update server
        # For now, check local update directory
        
        manifest_files = list(UPDATE_DIR.glob('manifest_*.json'))
        if not manifest_files:
            logger.info("No updates available")
            return None
        
        # Load latest manifest
        latest_manifest = sorted(manifest_files)[-1]
        with open(latest_manifest, 'r') as f:
            manifest = json.load(f)
        
        update_version = manifest.get('version')
        if update_version and update_version > self.current_version:
            logger.info(f"Update available: {update_version}")
            return manifest
        
        logger.info("No newer version available")
        return None


def main():
    """Main entry point"""
    logger.info("Firmware Update Manager starting...")
    
    # Create log directory
    Path('/var/log/firmware').mkdir(parents=True, exist_ok=True)
    
    manager = FirmwareUpdateManager()
    
    # Check for updates
    manifest = manager.check_for_updates('https://updates.example.com')
    
    if manifest:
        update_file = UPDATE_DIR / manifest['filename']
        if update_file.exists():
            logger.info(f"Applying update: {manifest['version']}")
            success = manager.apply_update(update_file, manifest)
            
            if success:
                logger.info("✓ Update completed successfully")
            else:
                logger.error("✗ Update failed")


if __name__ == '__main__':
    main()
