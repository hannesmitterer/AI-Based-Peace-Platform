from dataclasses import dataclass

@dataclass(frozen=True)
class LogEntry:
    timestamp: str
    level: str
    message: str

class SignatureAgent:
    def __init__(self, private_key: str):
        self.private_key = private_key

    def sign(self, log_entry: LogEntry) -> str:
        # Implementation for signing the log entry
        pass

class GatewayLogAgent:
    def __init__(self, signature_agent: SignatureAgent):
        self.signature_agent = signature_agent
        self.logs = []

    def log(self, level: str, message: str):
        log_entry = LogEntry(timestamp='2023-10-01T00:00:00Z', level=level, message=message)
        signature = self.signature_agent.sign(log_entry)
        self.logs.append((log_entry, signature))

    def get_logs(self):
        return self.logs
