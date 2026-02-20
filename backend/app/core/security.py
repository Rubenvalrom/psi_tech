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

# Retrieve JWKS (Public Keys)
# TODO: Implement caching for JWKS to avoid fetch on every request (use Redis or in-memory cache)
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token")

logger = logging.getLogger(__name__)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> DBUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Fetch public keys from Keycloak
        try:
            response = requests.get(JWKS_URL, verify=VERIFY_SSL, timeout=5)
            if response.status_code != 200:
                logger.error(f"Failed to fetch JWKS from {JWKS_URL}. Status: {response.status_code}")
                raise credentials_exception
            jwks = response.json()
        except requests.RequestException as e:
            logger.error(f"Error connecting to Keycloak JWKS at {JWKS_URL}: {e}")
            raise credentials_exception
        
        # Verify JWT signature and claims
        try:
            # python-jose automatically finds the key in jwks matching the 'kid' in header
            payload = jwt.decode(
                token,
                jwks,
                algorithms=ALGORITHMS,
                audience=JWT_AUDIENCE,
                options={"verify_aud": True}  # Always verify audience
            )
        except JWTError as e:
            logger.error(f"JWT Verification Error: {e}")
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
