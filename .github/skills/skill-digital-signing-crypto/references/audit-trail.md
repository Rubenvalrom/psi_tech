# Audit Trail for Digital Signatures

## Audit Log Schema

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    action = Column(String(50))  # sign, verify, create, approve
    document_id = Column(String(100))
    document_hash = Column(String(64))  # SHA256 hash
    user_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    result = Column(String(20))  # success, failed
    details = Column(JSON)  # Additional context
```

## Audit Trail Implementation

```python
import logging
from functools import wraps
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

class AuditTrail:
    @staticmethod
    async def log_signing(
        db: AsyncSession,
        document_id: str,
        document_hash: str,
        user_id: int,
        ip_address: str,
        success: bool
    ):
        """Log document signing"""
        
        log_entry = AuditLog(
            action="sign",
            document_id=document_id,
            document_hash=document_hash,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            result="success" if success else "failed",
            details={
                "signature_algorithm": "RSA-SHA256",
                "certificate_used": "olympus-backend.crt"
            }
        )
        
        db.add(log_entry)
        await db.commit()
    
    @staticmethod
    async def log_verification(
        db: AsyncSession,
        document_id: str,
        document_hash: str,
        user_id: int,
        ip_address: str,
        is_valid: bool
    ):
        """Log signature verification"""
        
        log_entry = AuditLog(
            action="verify",
            document_id=document_id,
            document_hash=document_hash,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            result="success" if is_valid else "failed",
            details={
                "verification_result": "valid" if is_valid else "invalid"
            }
        )
        
        db.add(log_entry)
        await db.commit()
```

## FastAPI Integration

```python
from fastapi import Request

def audit_decorator(action: str):
    """Decorator for logging actions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request: Request = kwargs.get('request')
            db: AsyncSession = kwargs.get('db')
            
            result = await func(*args, **kwargs)
            
            # Log to audit trail
            await AuditTrail.log_signing(
                db=db,
                document_id=result.get("document_id"),
                document_hash=result.get("hash"),
                user_id=request.user.id,
                ip_address=request.client.host,
                success=result.get("success", True)
            )
            
            return result
        return wrapper
    return decorator

# Usage
@router.post("/sign")
@audit_decorator("sign")
async def sign_document(
    doc: DocumentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Sign document (with audit trail)"""
    # Implementation...
```

## Retrieving Audit History

```python
async def get_document_audit_history(
    db: AsyncSession,
    document_id: str,
    limit: int = 100
):
    """Get audit trail for a document"""
    
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.document_id == document_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
    )
    
    return result.scalars().all()
```

## Compliance & Retention

```python
# GDPR: Retain audit logs for 6 years (Spain's LAC)
AUDIT_RETENTION_DAYS = 365 * 6

async def cleanup_old_audit_logs(db: AsyncSession):
    """Remove audit logs older than retention period"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=AUDIT_RETENTION_DAYS)
    
    result = await db.execute(
        delete(AuditLog)
        .where(AuditLog.timestamp < cutoff_date)
    )
    
    await db.commit()
    return result.rowcount
```
