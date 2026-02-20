from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Optional, List
import requests
import logging

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User as DBUser

# Keycloak Config from settings
KEYCLOAK_URL = settings.KEYCLOAK_URL
REALM = settings.KEYCLOAK_REALM
VERIFY_SSL = settings.VERIFY_SSL
JWT_AUDIENCE = settings.JWT_AUDIENCE
ALGORITHMS = ["RS256"]

import requests
import logging
import time

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User as DBUser

# Keycloak Config from settings
KEYCLOAK_URL = settings.KEYCLOAK_URL
REALM = settings.KEYCLOAK_REALM
VERIFY_SSL = settings.VERIFY_SSL
JWT_AUDIENCE = settings.JWT_AUDIENCE
ALGORITHMS = ["RS256"]

# Retrieve JWKS (Public Keys)
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"

# JWKS Cache
_jwks_cache = None
_jwks_last_fetch = 0
JWKS_CACHE_TTL = 3600  # 1 hora

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token")

logger = logging.getLogger(__name__)

def get_jwks():
    """Fetch JWKS from Keycloak with caching."""
    global _jwks_cache, _jwks_last_fetch
    
    current_time = time.time()
    if _jwks_cache and (current_time - _jwks_last_fetch < JWKS_CACHE_TTL):
        return _jwks_cache
        
    try:
        logger.info(f"Fetching JWKS from {JWKS_URL}")
        response = requests.get(JWKS_URL, verify=VERIFY_SSL, timeout=5)
        if response.status_code == 200:
            _jwks_cache = response.json()
            _jwks_last_fetch = current_time
            return _jwks_cache
        else:
            logger.error(f"Failed to fetch JWKS. Status: {response.status_code}")
            if _jwks_cache: return _jwks_cache # Fallback to old cache if available
    except Exception as e:
        logger.error(f"Error fetching JWKS: {e}")
        if _jwks_cache: return _jwks_cache
    
    return None

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> DBUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get JWKS from cache or fetch it
        jwks = get_jwks()
        if not jwks:
            raise credentials_exception
        
        # Verify JWT signature and claims
        try:
            # Determine which audience to expect
            # We can accept both the client_id and 'account' which is Keycloak default
            expected_audiences = [JWT_AUDIENCE, "account", "olympus-frontend", "olympus-backend"]
            
            # python-jose automatically finds the key in jwks matching the 'kid' in header
            payload = jwt.decode(
                token,
                jwks,
                algorithms=ALGORITHMS,
                audience=expected_audiences,
                options={
                    "verify_aud": True,
                    "verify_iss": False, 
                    "verify_at_hash": False,
                    "verify_sub": True
                }
            )
        except JWTError as e:
            logger.error(f"JWT Verification Error Details: {str(e)}")
            # Try to decode without verification just to log what's inside (DEBUG ONLY)
            try:
                unverified_payload = jwt.get_unverified_claims(token)
                logger.debug(f"Unverified Payload: {unverified_payload}")
                logger.debug(f"Expected Audience: {JWT_AUDIENCE}")
            except:
                pass
            raise credentials_exception
        
        username: str = payload.get("preferred_username")
        email: str = payload.get("email")
        sub: str = payload.get("sub")  # Keycloak User ID (UUID)
        
        if username is None:
            raise credentials_exception
            
        roles = payload.get("realm_access", {}).get("roles", [])
        
        # Check if user exists in DB
        user = db.query(DBUser).filter(DBUser.keycloak_id == sub).first()
        
        if not user:
            # Fallback check by username (migration/legacy)
            user = db.query(DBUser).filter(DBUser.username == username).first()
            if user:
                # Update keycloak_id if missing
                if not user.keycloak_id:
                    user.keycloak_id = sub
                    db.commit()
            else:
                # Auto-provision user from Keycloak token
                logger.info(f"Auto-provisioning user {username} from Keycloak token.")
                user = DBUser(
                    keycloak_id=sub,
                    username=username,
                    email=email if email else f"{username}@example.com",
                    nombre_completo=payload.get("name", username),
                    password_hash="managed_by_keycloak",  # Not used, auth via Keycloak
                    roles=roles,
                    activo=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected auth exception: {e}")
        raise credentials_exception
