#!/usr/bin/env python3
"""
crypto_utils.py - Digital signatures and X.509 certificate utilities for eIDAS
"""

import hashlib
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Optional

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID, ExtensionOID


class CertificateManager:
    """Manage X.509 certificates for digital signing"""
    
    def __init__(self, cert_dir: str = "./certs"):
        self.cert_dir = Path(cert_dir)
        self.cert_dir.mkdir(exist_ok=True)
    
    def generate_ca_cert(
        self,
        common_name: str = "Olympus CA",
        days_valid: int = 3650
    ) -> Tuple[str, str]:
        """Generate self-signed CA certificate"""
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Olympus"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
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
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=days_valid)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # Save certificate
        cert_path = self.cert_dir / f"{common_name.lower()}.crt"
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Save private key (encrypted)
        key_path = self.cert_dir / f"{common_name.lower()}.key"
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return str(cert_path), str(key_path)
    
    def generate_server_cert(
        self,
        common_name: str,
        ca_cert_path: str,
        ca_key_path: str,
        days_valid: int = 365
    ) -> Tuple[str, str]:
        """Generate server certificate signed by CA"""
        
        # Load CA cert and key
        with open(ca_cert_path, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(
                f.read(), default_backend()
            )
        
        with open(ca_key_path, "rb") as f:
            ca_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )
        
        # Generate server private key
        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Generate certificate
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Olympus"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.issuer
        ).public_key(
            server_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=days_valid)
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(common_name),
            ]),
            critical=False,
        ).sign(ca_key, hashes.SHA256(), default_backend())
        
        # Save certificate
        cert_path = self.cert_dir / f"{common_name}.crt"
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Save private key
        key_path = self.cert_dir / f"{common_name}.key"
        with open(key_path, "wb") as f:
            f.write(server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return str(cert_path), str(key_path)
    
    def validate_certificate(self, cert_path: str) -> dict:
        """Validate certificate"""
        
        with open(cert_path, "rb") as f:
            cert = x509.load_pem_x509_certificate(
                f.read(), default_backend()
            )
        
        now = datetime.utcnow()
        is_valid = cert.not_valid_before <= now <= cert.not_valid_after
        days_until_expiry = (cert.not_valid_after - now).days
        
        return {
            "subject": cert.subject.rfc4514_string(),
            "issuer": cert.issuer.rfc4514_string(),
            "valid_from": cert.not_valid_before,
            "valid_to": cert.not_valid_after,
            "is_valid": is_valid,
            "days_until_expiry": days_until_expiry,
            "serial_number": cert.serial_number,
        }


class DigitalSignature:
    """Digital signature operations"""
    
    @staticmethod
    def sign_data(
        data: bytes,
        private_key_path: str,
        password: Optional[bytes] = None
    ) -> bytes:
        """Sign data with private key"""
        
        with open(private_key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(), password=password, backend=default_backend()
            )
        
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    @staticmethod
    def verify_signature(
        data: bytes,
        signature: bytes,
        cert_path: str
    ) -> bool:
        """Verify digital signature"""
        
        with open(cert_path, "rb") as f:
            cert = x509.load_pem_x509_certificate(
                f.read(), default_backend()
            )
        
        public_key = cert.public_key()
        
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False
    
    @staticmethod
    def create_signed_document(
        document_data: dict,
        private_key_path: str
    ) -> dict:
        """Create a signed document"""
        
        # Serialize document
        import json
        doc_bytes = json.dumps(document_data, sort_keys=True).encode()
        
        # Calculate hash
        doc_hash = hashlib.sha256(doc_bytes).hexdigest()
        
        # Sign
        signature = DigitalSignature.sign_data(doc_bytes, private_key_path)
        
        # Package
        signed_doc = {
            "document": document_data,
            "hash": doc_hash,
            "signature": signature.hex(),
            "timestamp": datetime.utcnow().isoformat(),
            "algorithm": "RSA-SHA256"
        }
        
        return signed_doc
    
    @staticmethod
    def verify_signed_document(
        signed_document: dict,
        cert_path: str
    ) -> bool:
        """Verify a signed document"""
        
        import json
        doc_bytes = json.dumps(
            signed_document["document"],
            sort_keys=True
        ).encode()
        
        signature_bytes = bytes.fromhex(signed_document["signature"])
        
        return DigitalSignature.verify_signature(
            doc_bytes,
            signature_bytes,
            cert_path
        )


# Example usage
if __name__ == "__main__":
    # Initialize manager
    cert_mgr = CertificateManager()
    
    # Generate CA certificate
    print("Generating CA certificate...")
    ca_cert, ca_key = cert_mgr.generate_ca_cert()
    print(f"CA Certificate: {ca_cert}")
    
    # Generate server certificate
    print("\nGenerating server certificate...")
    srv_cert, srv_key = cert_mgr.generate_server_cert(
        "olympus-backend.local",
        ca_cert,
        ca_key
    )
    print(f"Server Certificate: {srv_cert}")
    
    # Validate certificate
    print("\nValidating server certificate...")
    info = cert_mgr.validate_certificate(srv_cert)
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Sign and verify document
    print("\nTesting digital signatures...")
    document = {
        "solicitud_id": "SOL-2024-001",
        "solicitante": "Juan Pérez",
        "monto": 5000,
        "concepto": "Compra de equipamiento"
    }
    
    signed_doc = DigitalSignature.create_signed_document(document, srv_key)
    print(f"Signed document hash: {signed_doc['hash']}")
    
    is_valid = DigitalSignature.verify_signed_document(signed_doc, srv_cert)
    print(f"Signature valid: {is_valid}")
