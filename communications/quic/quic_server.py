#!/usr/bin/env python3
"""
QUIC Protocol Implementation with TLS 1.3
Secure, low-latency communication protocol for decentralized operations
"""

import os
import ssl
import asyncio
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from aioquic.asyncio import serve
    from aioquic.asyncio.protocol import QuicConnectionProtocol
    from aioquic.quic.configuration import QuicConfiguration
    from aioquic.quic.events import QuicEvent, StreamDataReceived
except ImportError:
    logging.warning("aioquic not installed. Install with: pip install aioquic")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('QUICServer')

# Configuration
QUIC_HOST = os.getenv('QUIC_HOST', '0.0.0.0')
QUIC_PORT = int(os.getenv('QUIC_PORT', '4433'))
CERT_FILE = Path(os.getenv('QUIC_CERT', '/etc/ssl/certs/quic-cert.pem'))
KEY_FILE = Path(os.getenv('QUIC_KEY', '/etc/ssl/private/quic-key.pem'))


class SecureQuicProtocol(QuicConnectionProtocol):
    """Secure QUIC protocol handler with TLS 1.3"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.streams = {}
        
    def quic_event_received(self, event: QuicEvent) -> None:
        """Handle QUIC events"""
        if isinstance(event, StreamDataReceived):
            self.handle_stream_data(event)
    
    def handle_stream_data(self, event: StreamDataReceived) -> None:
        """Handle incoming stream data"""
        stream_id = event.stream_id
        data = event.data
        end_stream = event.end_stream
        
        logger.info(f"Received data on stream {stream_id}: {len(data)} bytes")
        
        # Process data
        try:
            message = data.decode('utf-8')
            logger.info(f"Message: {message}")
            
            # Send response
            response = self.process_message(message)
            self.send_response(stream_id, response)
            
        except Exception as e:
            logger.error(f"Error processing stream data: {e}")
            self.send_error(stream_id, str(e))
    
    def process_message(self, message: str) -> str:
        """Process incoming message"""
        # Implement message processing logic here
        timestamp = datetime.now().isoformat()
        return f"{{\"status\": \"ok\", \"timestamp\": \"{timestamp}\", \"echo\": \"{message}\"}}"
    
    def send_response(self, stream_id: int, response: str) -> None:
        """Send response to client"""
        logger.info(f"Sending response on stream {stream_id}")
        
        data = response.encode('utf-8')
        self._quic.send_stream_data(stream_id, data, end_stream=True)
        self.transmit()
    
    def send_error(self, stream_id: int, error: str) -> None:
        """Send error response"""
        logger.error(f"Sending error on stream {stream_id}: {error}")
        
        response = f"{{\"status\": \"error\", \"message\": \"{error}\"}}"
        data = response.encode('utf-8')
        self._quic.send_stream_data(stream_id, data, end_stream=True)
        self.transmit()


class QUICServer:
    """QUIC server with TLS 1.3 encryption"""
    
    def __init__(self, host: str = QUIC_HOST, port: int = QUIC_PORT):
        self.host = host
        self.port = port
        self.configuration = self.create_configuration()
    
    def create_configuration(self) -> QuicConfiguration:
        """Create QUIC configuration with TLS 1.3"""
        logger.info("Creating QUIC configuration with TLS 1.3")
        
        configuration = QuicConfiguration(
            is_client=False,
            alpn_protocols=["h3", "hq-interop"],
        )
        
        # Load SSL certificate and key
        if CERT_FILE.exists() and KEY_FILE.exists():
            logger.info(f"Loading certificate: {CERT_FILE}")
            logger.info(f"Loading key: {KEY_FILE}")
            
            configuration.load_cert_chain(
                str(CERT_FILE),
                str(KEY_FILE)
            )
        else:
            logger.warning("Certificate files not found, generating self-signed certificate")
            self.generate_self_signed_cert()
            configuration.load_cert_chain(
                str(CERT_FILE),
                str(KEY_FILE)
            )
        
        # Enforce TLS 1.3
        configuration.verify_mode = ssl.CERT_NONE  # For testing, should be CERT_REQUIRED in production
        
        # Security settings
        configuration.max_datagram_frame_size = 1280
        configuration.idle_timeout = 60.0
        
        logger.info("✓ QUIC configuration created with TLS 1.3")
        return configuration
    
    def generate_self_signed_cert(self) -> None:
        """Generate self-signed certificate for testing"""
        logger.warning("Generating self-signed certificate (for testing only)")
        
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Decentralized Peace Platform"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Save certificate and key
        CERT_FILE.parent.mkdir(parents=True, exist_ok=True)
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CERT_FILE, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(KEY_FILE, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))
        
        logger.info(f"✓ Self-signed certificate created: {CERT_FILE}")
    
    async def start(self) -> None:
        """Start QUIC server"""
        logger.info(f"Starting QUIC server on {self.host}:{self.port}")
        logger.info("Protocol: QUIC with TLS 1.3")
        
        await serve(
            self.host,
            self.port,
            configuration=self.configuration,
            create_protocol=SecureQuicProtocol,
        )
        
        logger.info(f"✓ QUIC server running on {self.host}:{self.port}")
        
        # Keep server running
        await asyncio.Future()


def main():
    """Main entry point"""
    logger.info("QUIC Server with TLS 1.3 starting...")
    
    server = QUICServer()
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")


if __name__ == '__main__':
    main()
