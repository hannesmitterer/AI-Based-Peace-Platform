import json
from datetime import datetime

class EuystacioAuditLogger:
    def __init__(self, log_file='council_ledger.log'):
        self.log_file = log_file

    def log_event(self, event_type, data):
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'type': event_type,
            'data': data
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def get_integrity_hash(self):
        import hashlib
        hasher = hashlib.sha256()
        with open(self.log_file, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
