# JWT Validation in FastAPI

## Token Validation Flow

1. **Extract token from Authorization header**
   ```python
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   async def get_token(credentials = Depends(security)):
       return credentials.credentials
   ```

2. **Validate JWT signature and expiry**
   ```python
   from keycloak import KeycloakOpenID
   import jwt
   
   keycloak = KeycloakOpenID(
       server_url=KEYCLOAK_URL,
       realm_name=KEYCLOAK_REALM,
       client_id=KEYCLOAK_CLIENT_ID,
       client_secret_key=KEYCLOAK_CLIENT_SECRET
   )
   
   async def verify_token(token: str) -> dict:
       try:
           # Get public key from Keycloak (cached)
           public_key = keycloak.public_key()
           decoded = jwt.decode(
               token,
               public_key,
               algorithms=["RS256"],
               audience=KEYCLOAK_CLIENT_ID
           )
           return decoded
       except jwt.ExpiredSignatureError:
           raise HTTPException(status_code=401, detail="Token expired")
       except jwt.InvalidTokenError:
           raise HTTPException(status_code=401, detail="Invalid token")
   ```

3. **Extract claims (user, roles, scopes)**
   ```python
   def get_user_info(payload: dict) -> dict:
       return {
           "sub": payload.get("sub"),
           "preferred_username": payload.get("preferred_username"),
           "email": payload.get("email"),
           "roles": payload.get("realm_access", {}).get("roles", []),
       }
   ```

## Dependency Injection Pattern

```python
from fastapi import Depends

async def get_current_user(
    token: str = Depends(get_token)
) -> dict:
    """FastAPI dependency that returns authenticated user."""
    return await verify_token(token)

@app.get("/api/v1/me")
async def get_me(user = Depends(get_current_user)):
    return user
```

## Token Refresh Strategy

Keycloak public keys should be cached but refreshed on signature failures:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class KeycloakKeyCache:
    def __init__(self, ttl_hours=24):
        self.ttl = timedelta(hours=ttl_hours)
        self.cached_key = None
        self.cached_at = None
    
    def get_public_key(self, force_refresh=False):
        now = datetime.utcnow()
        if force_refresh or not self.cached_key or (now - self.cached_at) > self.ttl:
            self.cached_key = keycloak.public_key()
            self.cached_at = now
        return self.cached_key
```

## Error Handling

| Error | Status Code | Action |
|-------|-------------|--------|
| Token missing | 401 Unauthorized | Redirect to login |
| Token expired | 401 Unauthorized | Trigger token refresh (frontend) |
| Invalid signature | 401 Unauthorized | Force re-authentication |
| Wrong audience | 401 Unauthorized | Check client_id configuration |
| Malformed JWT | 400 Bad Request | Log + reject |

## Testing

```python
import pytest
from unittest.mock import patch, MagicMock

def test_valid_token():
    token = "valid.jwt.token"
    with patch('keycloak.KeycloakOpenID.public_key') as mock_key:
        mock_key.return_value = MOCK_PUBLIC_KEY
        user = asyncio.run(verify_token(token))
        assert user["sub"] == "user-123"

def test_expired_token():
    token = "expired.jwt.token"
    with patch('jwt.decode') as mock_decode:
        mock_decode.side_effect = jwt.ExpiredSignatureError()
        with pytest.raises(HTTPException) as exc:
            asyncio.run(verify_token(token))
        assert exc.value.status_code == 401
```
