#!/usr/bin/env python3
"""
Distributed Encrypted Backup Manager
Manages automated encrypted backups using IPFS and GnuPG
"""

import os
import json
import logging
import subprocess
import gnupg
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/backup/backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BackupManager')

# Configuration
BACKUP_DIR = Path('/opt/backups')
IPFS_DIR = Path('/opt/ipfs')
GPG_HOME = Path.home() / '.gnupg'
GPG_KEY_ID = os.getenv('BACKUP_GPG_KEY', 'backup-key')
IPFS_API = os.getenv('IPFS_API', '/ip4/127.0.0.1/tcp/5001')


class IPFSBackupManager:
    """Manages distributed encrypted backups using IPFS"""
    
    def __init__(self):
        self.gpg = gnupg.GPG(gnupghome=str(GPG_HOME))
        self.backup_index = self.load_backup_index()
        
        # Ensure directories exist
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        IPFS_DIR.mkdir(parents=True, exist_ok=True)
    
    def load_backup_index(self) -> Dict:
        """Load backup index from file"""
        index_file = BACKUP_DIR / 'backup_index.json'
        if index_file.exists():
            with open(index_file, 'r') as f:
                return json.load(f)
        return {'backups': []}
    
    def save_backup_index(self):
        """Save backup index to file"""
        index_file = BACKUP_DIR / 'backup_index.json'
        with open(index_file, 'w') as f:
            json.dump(self.backup_index, f, indent=2)
    
    def encrypt_file(self, file_path: Path, recipient: str = None) -> Path:
        """Encrypt file using GnuPG"""
        logger.info(f"Encrypting file: {file_path}")
        
        if recipient is None:
            recipient = GPG_KEY_ID
        
        encrypted_path = Path(str(file_path) + '.gpg')
        
        with open(file_path, 'rb') as f:
            encrypted_data = self.gpg.encrypt_file(
                f,
                recipients=[recipient],
                output=str(encrypted_path),
                armor=False,
                always_trust=True
            )
        
        if encrypted_data.ok:
            logger.info(f"✓ File encrypted: {encrypted_path}")
            return encrypted_path
        else:
            logger.error(f"✗ Encryption failed: {encrypted_data.status}")
            raise Exception(f"Encryption failed: {encrypted_data.status}")
    
    def decrypt_file(self, encrypted_path: Path, output_path: Optional[Path] = None) -> Path:
        """Decrypt file using GnuPG"""
        logger.info(f"Decrypting file: {encrypted_path}")
        
        if output_path is None:
            output_path = Path(str(encrypted_path).replace('.gpg', ''))
        
        with open(encrypted_path, 'rb') as f:
            decrypted_data = self.gpg.decrypt_file(
                f,
                output=str(output_path)
            )
        
        if decrypted_data.ok:
            logger.info(f"✓ File decrypted: {output_path}")
            return output_path
        else:
            logger.error(f"✗ Decryption failed: {decrypted_data.status}")
            raise Exception(f"Decryption failed: {decrypted_data.status}")
    
    def create_archive(self, source_paths: List[Path], archive_name: str) -> Path:
        """Create tar.gz archive from source paths"""
        logger.info(f"Creating archive: {archive_name}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_path = BACKUP_DIR / f"{archive_name}_{timestamp}.tar.gz"
        
        # Build tar command
        cmd = ['tar', 'czf', str(archive_path)]
        for path in source_paths:
            cmd.extend(['-C', str(path.parent), path.name])
        
        subprocess.run(cmd, check=True)
        
        logger.info(f"✓ Archive created: {archive_path} ({archive_path.stat().st_size} bytes)")
        return archive_path
    
    def add_to_ipfs(self, file_path: Path) -> str:
        """Add file to IPFS network"""
        logger.info(f"Adding to IPFS: {file_path}")
        
        try:
            # Use ipfs add command
            result = subprocess.run(
                ['ipfs', 'add', '-q', str(file_path)],
                capture_output=True,
                text=True,
                check=True
            )
            
            cid = result.stdout.strip()
            logger.info(f"✓ Added to IPFS: {cid}")
            
            # Pin the CID to ensure persistence
            subprocess.run(['ipfs', 'pin', 'add', cid], check=True)
            logger.info(f"✓ Pinned CID: {cid}")
            
            return cid
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ IPFS add failed: {e.stderr}")
            raise
    
    def get_from_ipfs(self, cid: str, output_path: Path) -> Path:
        """Retrieve file from IPFS network"""
        logger.info(f"Retrieving from IPFS: {cid}")
        
        try:
            subprocess.run(
                ['ipfs', 'get', cid, '-o', str(output_path)],
                check=True
            )
            
            logger.info(f"✓ Retrieved from IPFS: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ IPFS get failed: {e}")
            raise
    
    def create_backup(self, source_paths: List[str], backup_name: str, description: str = "") -> Dict:
        """Create encrypted distributed backup"""
        logger.info(f"Creating backup: {backup_name}")
        
        try:
            # Convert to Path objects
            paths = [Path(p) for p in source_paths]
            
            # 1. Create archive
            archive = self.create_archive(paths, backup_name)
            
            # 2. Encrypt archive
            encrypted = self.encrypt_file(archive)
            
            # 3. Add to IPFS
            cid = self.add_to_ipfs(encrypted)
            
            # 4. Record backup metadata
            backup_record = {
                'name': backup_name,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'cid': cid,
                'encrypted_file': str(encrypted.name),
                'original_size': archive.stat().st_size,
                'encrypted_size': encrypted.stat().st_size,
                'source_paths': source_paths
            }
            
            self.backup_index['backups'].append(backup_record)
            self.save_backup_index()
            
            # 5. Clean up local files (optional)
            # archive.unlink()  # Keep for now
            
            logger.info(f"✓ Backup completed: {backup_name}")
            logger.info(f"  CID: {cid}")
            logger.info(f"  Size: {encrypted.stat().st_size} bytes")
            
            return backup_record
            
        except Exception as e:
            logger.error(f"✗ Backup failed: {e}")
            raise
    
    def restore_backup(self, cid: str, restore_path: Path) -> bool:
        """Restore backup from IPFS"""
        logger.info(f"Restoring backup from CID: {cid}")
        
        try:
            # 1. Retrieve from IPFS
            encrypted_file = BACKUP_DIR / f"restore_{cid}.gpg"
            self.get_from_ipfs(cid, encrypted_file)
            
            # 2. Decrypt
            decrypted_file = self.decrypt_file(encrypted_file)
            
            # 3. Extract archive
            logger.info(f"Extracting to: {restore_path}")
            subprocess.run([
                'tar', 'xzf', str(decrypted_file),
                '-C', str(restore_path)
            ], check=True)
            
            # 4. Clean up
            encrypted_file.unlink()
            decrypted_file.unlink()
            
            logger.info("✓ Backup restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"✗ Restore failed: {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        logger.info("Listing backups...")
        
        backups = self.backup_index.get('backups', [])
        
        for i, backup in enumerate(backups, 1):
            logger.info(f"{i}. {backup['name']}")
            logger.info(f"   Timestamp: {backup['timestamp']}")
            logger.info(f"   CID: {backup['cid']}")
            logger.info(f"   Size: {backup['encrypted_size']} bytes")
            logger.info(f"   Description: {backup.get('description', 'N/A')}")
            logger.info("")
        
        return backups
    
    def verify_backup(self, cid: str) -> bool:
        """Verify backup integrity on IPFS"""
        logger.info(f"Verifying backup: {cid}")
        
        try:
            # Check if CID is pinned
            result = subprocess.run(
                ['ipfs', 'pin', 'ls', cid],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✓ Backup verified on IPFS")
                return True
            else:
                logger.warning("⚠ Backup not found on IPFS")
                return False
                
        except Exception as e:
            logger.error(f"✗ Verification failed: {e}")
            return False


def main():
    """Main entry point"""
    logger.info("IPFS Backup Manager starting...")
    
    # Create log directory
    Path('/var/log/backup').mkdir(parents=True, exist_ok=True)
    
    manager = IPFSBackupManager()
    
    # Example usage
    # Create a backup
    # backup = manager.create_backup(
    #     source_paths=['/opt/data', '/etc/config'],
    #     backup_name='daily_backup',
    #     description='Daily automated backup'
    # )
    
    # List backups
    manager.list_backups()


if __name__ == '__main__':
    main()
