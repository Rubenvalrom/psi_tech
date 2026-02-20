---
name: skill-digital-signing-crypto
description: Implement electronic signatures and cryptographic validation for Spanish government documents. Includes X.509 certificate handling, sign/verify operations, audit trails, and compliance with eIDAS regulations. Use when documents require legal digital signatures for corporate transactions.
---

# Digital Signing & Cryptography (eIDAS)

## Quick Start

```python
from app.crypto.signer import DocumentSigner

signer = DocumentSigner(keycloak_manager=keycloak)

# Sign
signature = signer.sign_document(
    document_id=123,
    user_cert=user_certificate,
    timestamp=datetime.utcnow()
)

# Verify
is_valid = signer.verify_signature(
    document_id=123,
    signature=signature,
    user_cert=user_certificate
)
```

## Key Concepts

See [references/x509-certs.md](references/x509-certs.md):
- Load X.509 certificates from Keycloak
- Validate certificate chain
- Check expiration/revocation

See [references/signature-workflows.md](references/signature-workflows.md):
- Single signature (one user)
- Countersignature (multiple approvals)
- Audit trail persistence

See [references/audit-trail.md](references/audit-trail.md):
- Log all sign operations
- Store signature metadata
- Compliance with Spanish legal requirements

## Scripts

```bash
python scripts/crypto_utils.py --sign doc.pdf --key private.pem
python scripts/validate_certs.py --cert cert.pem
```
