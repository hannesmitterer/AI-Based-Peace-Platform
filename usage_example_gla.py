import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature, decode_dss_signature
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# --- LogEntry structure with ECDSA Signature ---
@dataclass(frozen=True)
class LogEntry:
    timestamp: float = field(default_factory=time.time)
    agent_id: str
    event_details: str
    previous_hash: str
    entry_hash: Optional[str] = field(init=False, default=None)
    signature: Optional[str] = field(init=False, default=None)
    signature_verified: Optional[bool] = field(init=False, default=None)

    def calculate_hash(self) -> str:
        data_to_hash = {
            'timestamp': self.timestamp,
            'agent_id': self.agent_id,
            'event_details': self.event_details,
            'previous_hash': self.previous_hash
        }
        json_data = json.dumps(data_to_hash, sort_keys=True).encode('utf-8')
        return hashlib.sha256(json_data).hexdigest()

    def __post_init__(self):
        object.__setattr__(self, 'entry_hash', self.calculate_hash())

    def set_signature(self, signature_hex: str):
        object.__setattr__(self, 'signature', signature_hex)

    def set_signature_verified(self, verified: bool):
        object.__setattr__(self, 'signature_verified', verified)

    def get_signed_message_bytes(self) -> bytes:
        if not self.entry_hash:
            raise ValueError("Entry hash must be calculated before signing.")
        return self.entry_hash.encode('utf-8')


# --- Key Preparation and Signing/Verification Utilities ---
class ECDSASignatureAgent:
    def __init__(self):
        # Generate ECDSA key pair (secp256r1)
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def sign_message(self, message_bytes: bytes) -> str:
        signature = self.private_key.sign(
            message_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        # Use hex for transmission/storage
        return signature.hex()

    def verify_signature(self, message_bytes: bytes, signature_hex: str, public_key) -> bool:
        try:
            signature = bytes.fromhex(signature_hex)
            public_key.verify(signature, message_bytes, ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False


# --- Skeleton Key Registry (simulate key lookup) ---
class KeyRegistry:
    def __init__(self):
        self.keys = {}

    def register(self, agent_id, public_key):
        self.keys[agent_id] = public_key

    def get_public_key(self, agent_id):
        return self.keys[agent_id]


# --- Gateway Log Agent (GLA) with ECDSA Integration ---
class GatewayLogAgent:
    def __init__(self, agent_id, key_registry):
        self.agent_id = agent_id
        self.key_registry = key_registry
        self.log_chain = []
        self.current_hash = "GENESIS"

    def append_log_entry(self, event_details: str, signature_hex: str, signing_agent_id: str):
        log_entry = LogEntry(
            agent_id=signing_agent_id,
            event_details=event_details,
            previous_hash=self.current_hash
        )
        log_entry.set_signature(signature_hex)
        # Lookup public key from registry
        public_key = self.key_registry.get_public_key(signing_agent_id)
        verified = False
        if public_key:
            verified = ECDSASignatureAgent().verify_signature(
                log_entry.get_signed_message_bytes(),
                signature_hex,
                public_key
            )
        log_entry.set_signature_verified(verified)
        self.log_chain.append(log_entry)
        self.current_hash = log_entry.entry_hash
        return log_entry

    def verify_chain_integrity(self):
        for i, entry in enumerate(self.log_chain):
            # Hash chain check
            if i > 0 and entry.previous_hash != self.log_chain[i-1].entry_hash:
                print(f"Chain broken at entry {i}")
                return False
            # Signature verification check
            pubkey = self.key_registry.get_public_key(entry.agent_id)
            if not pubkey or not ECDSASignatureAgent().verify_signature(
                entry.get_signed_message_bytes(),
                entry.signature,
                pubkey
            ):
                print(f"Signature verification failed for entry {i}")
                return False
        return True


# --- Usage Example: Full Lifecycle ---
if __name__ == "__main__":
    # 1. Key & Message Preparation
    alice_agent = ECDSASignatureAgent()
    key_registry = KeyRegistry()
    key_registry.register("alice", alice_agent.public_key)

    # Alice creates a payload and signs it
    event_details = "Sensor reading: 42"
    dummy_log_entry = LogEntry(
        agent_id="alice",
        event_details=event_details,
        previous_hash="GENESIS"
    )
    payload_bytes = dummy_log_entry.get_signed_message_bytes()
    signature = alice_agent.sign_message(payload_bytes)
    print(f"Original signature: {signature}")

    # 2. GLA Integration (valid case)
    gla = GatewayLogAgent("gla", key_registry)
    log_entry1 = gla.append_log_entry(event_details, signature, "alice")
    print("Entry 1 signature verified:", log_entry1.signature_verified)

    # 2b. Tampered message (invalid case)
    tampered_event_details = "Sensor reading: 99"  # Tampered after signing!
    tampered_log_entry = LogEntry(
        agent_id="alice",
        event_details=tampered_event_details,
        previous_hash=log_entry1.entry_hash
    )
    tampered_payload_bytes = tampered_log_entry.get_signed_message_bytes()
    # Intentionally (wrongly) reuse the signature from the original, non-tampered message
    log_entry2 = gla.append_log_entry(tampered_event_details, signature, "alice")
    print("Entry 2 signature verified (should be False):", log_entry2.signature_verified)

    # 3. Verification
    print("\nVerifying entire log chain:")
    result = gla.verify_chain_integrity()
    print("Chain integrity valid:", result)