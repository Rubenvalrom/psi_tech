# X.509 Certificate Handling

```python
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime

def load_certificate(cert_data: bytes) -> x509.Certificate:
    """Load X.509 certificate."""
    return x509.load_pem_x509_certificate(cert_data, default_backend())

def validate_certificate(cert: x509.Certificate) -> bool:
    """Validate certificate not expired."""
    now = datetime.utcnow()
    return cert.not_valid_before <= now <= cert.not_valid_after

def get_cert_subject(cert: x509.Certificate) -> dict:
    """Extract certificate subject information."""
    subject = cert.subject
    return {
        "cn": subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value,
        "o": subject.get_attributes_for_oid(x509.oid.NameOID.ORGANIZATION_NAME)[0].value,
        "c": subject.get_attributes_for_oid(x509.oid.NameOID.COUNTRY_NAME)[0].value,
    }

def get_cert_from_keycloak_user(user_id: str, keycloak_manager) -> bytes:
    """Retrieve user's certificate from Keycloak."""
    user_attrs = keycloak_manager.get_user_attributes(user_id)
    return user_attrs.get("certificate_pem").encode()
```
