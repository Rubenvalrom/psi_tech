from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Optional, List
import requests
import os
import logging

from app.core.database import get_db
from app.models.user import User as DBUser

# Keycloak Config
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
REALM = os.getenv("KEYCLOAK_REALM", "olympus")
# Use environment variable to determine if we should verify SSL (for self-signed certs in dev)
VERIFY_SSL = os.getenv("VERIFY_SSL", "False").lower() == "true" 
ALGORITHMS = ["RS256"]

# Retrieve JWKS (Public Keys)
# In production, cache this or use a background task to refresh periodically.
# Note: In docker network, 'keycloak' hostname resolves. 
# If running locally, you might need localhost port forwarding.
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
        # Fetch public keys
        # TODO: Implement caching for JWKS to avoid fetch on every request
        try:
            # We use verify=False by default for dev environment self-signed certs
            response = requests.get(JWKS_URL, verify=VERIFY_SSL, timeout=5)
            if response.status_code != 200:
                logger.error(f"Failed to fetch JWKS from {JWKS_URL}. Status: {response.status_code}")
                # Fallback to allow dev without keycloak if really broken? No, security first.
                raise credentials_exception
            jwks = response.json()
        except requests.RequestException as e:
            logger.error(f"Error connecting to Keycloak JWKS at {JWKS_URL}: {e}")
            raise credentials_exception
        
        # Verify signature
        try:
            # python-jose automatically finds the key in jwks matching the 'kid' in header
            payload = jwt.decode(
                token,
                jwks,
                algorithms=ALGORITHMS,
                audience="account", # Default audience in Keycloak tokens unless configured otherwise
                options={"verify_aud": False} 
            )
        except JWTError as e:
            logger.error(f"JWT Verification Error: {e}")
            raise credentials_exception
        
        username: str = payload.get("preferred_username")
        email: str = payload.get("email")
        sub: str = payload.get("sub") # Keycloak User ID (UUID)
        
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
                # Auto-provision user
                logger.info(f"Auto-provisioning user {username} from Keycloak token.")
                user = DBUser(
                    keycloak_id=sub,
                    username=username,
                    email=email if email else f"{username}@example.com",
                    nombre_completo=payload.get("name", username),
                    password_hash="managed_by_keycloak", # Not used
                    roles=roles,
                    activo=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
        
        return user
        
    except Exception as e:
        logger.error(f"Auth Exception: {e}")
        raise credentials_exception
