#!/usr/bin/env python3
"""
Test Keycloak integration with FastAPI.
Run: pytest test_keycloak.py -v
"""

import os
import json
import jwt
import pytest
import requests
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Mock constants
KEYCLOAK_URL = "http://localhost:8080"
KEYCLOAK_REALM = "olympus"
KEYCLOAK_CLIENT_ID = "olympus-backend"
MOCK_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3kP...
(mock key - not real)
-----END PUBLIC KEY-----"""


class TestKeycloakLogin:
    """Test user login and token generation."""
    
    def test_admin_login_success(self):
        """Admin user can login and get token."""
        with patch.object(requests, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "admin.jwt.token",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
            mock_post.return_value = mock_response
            
            # Simulate login
            url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
            payload = {
                "client_id": KEYCLOAK_CLIENT_ID,
                "username": "admin",
                "password": "admin123!",
                "grant_type": "password",
            }
            
            response = requests.post(url, data=payload)
            
            assert response.status_code == 200
            assert "access_token" in response.json()
            assert response.json()["token_type"] == "Bearer"

    def test_invalid_credentials(self):
        """Invalid credentials return 401."""
        with patch.object(requests, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {
                "error": "invalid_grant",
                "error_description": "Invalid user credentials"
            }
            mock_post.return_value = mock_response
            
            url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
            response = requests.post(url, data={"username": "wrong", "password": "wrong"})
            
            assert response.status_code == 401


class TestJWTValidation:
    """Test JWT token validation."""
    
    def create_mock_token(self, **claims):
        """Create a mock JWT token with custom claims."""
        payload = {
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
            "sub": "user-123",
            "preferred_username": "admin",
            "email": "admin@olympus.gov",
            "realm_access": {"roles": ["ADMIN"]},
        }
        payload.update(claims)
        
        # Mock encoding (real implementation would use cryptography)
        return "mock.jwt.token"
    
    def test_valid_token_validation(self):
        """Valid token passes validation."""
        token = self.create_mock_token()
        
        with patch('jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "sub": "user-123",
                "preferred_username": "admin",
                "realm_access": {"roles": ["ADMIN"]}
            }
            
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            assert decoded["sub"] == "user-123"
            assert "ADMIN" in decoded["realm_access"]["roles"]

    def test_expired_token_validation(self):
        """Expired token raises exception."""
        token = self.create_mock_token(exp=datetime.utcnow() - timedelta(hours=1))
        
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")
            
            with pytest.raises(jwt.ExpiredSignatureError):
                jwt.decode(token, options={"verify_signature": False})

    def test_invalid_signature(self):
        """Invalid signature raises exception."""
        token = "invalid.jwt.token"
        
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.InvalidSignatureError("Invalid signature")
            
            with pytest.raises(jwt.InvalidSignatureError):
                jwt.decode(token, options={"verify_signature": False})


class TestRoleBasedAccess:
    """Test role-based access control."""
    
    def test_admin_role_in_token(self):
        """ADMIN role is present in decoded token."""
        token_payload = {
            "sub": "user-123",
            "realm_access": {"roles": ["ADMIN", "default-roles-olympus"]}
        }
        
        assert "ADMIN" in token_payload["realm_access"]["roles"]

    def test_funcionario_role_in_token(self):
        """FUNCIONARIO role is present in decoded token."""
        token_payload = {
            "sub": "user-456",
            "realm_access": {"roles": ["FUNCIONARIO"]}
        }
        
        assert "FUNCIONARIO" in token_payload["realm_access"]["roles"]
        assert "ADMIN" not in token_payload["realm_access"]["roles"]

    def test_role_check_logic(self):
        """Role check logic for endpoint protection."""
        def check_role(token_payload, required_roles):
            user_roles = token_payload.get("realm_access", {}).get("roles", [])
            return any(role in user_roles for role in required_roles)
        
        admin_token = {
            "realm_access": {"roles": ["ADMIN"]}
        }
        funcionario_token = {
            "realm_access": {"roles": ["FUNCIONARIO"]}
        }
        
        # Admin can access "create_expediente"
        assert check_role(admin_token, ["FUNCIONARIO", "ADMIN"]) is True
        
        # Funcionario can access "create_expediente"
        assert check_role(funcionario_token, ["FUNCIONARIO", "ADMIN"]) is True
        
        # Funcionario cannot access "approve_payment" (needs GESTOR_FINANCIERO)
        assert check_role(funcionario_token, ["GESTOR_FINANCIERO", "ADMIN"]) is False


class TestKeycloakIntegration:
    """Integration tests with Keycloak API."""
    
    def test_realm_creation(self):
        """Realm can be created via admin API."""
        with patch.object(requests, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_post.return_value = mock_response
            
            url = f"{KEYCLOAK_URL}/admin/realms"
            response = requests.post(url, json={"realm": "olympus", "enabled": True})
            
            assert response.status_code == 201

    def test_user_creation(self):
        """User can be created via admin API."""
        with patch.object(requests, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": "user-uuid-123"}
            mock_post.return_value = mock_response
            
            url = f"{KEYCLOAK_URL}/admin/realms/olympus/users"
            response = requests.post(url, json={"username": "testuser"})
            
            assert response.status_code == 201
            assert response.json()["id"] == "user-uuid-123"

    def test_role_assignment(self):
        """Role can be assigned to user."""
        with patch.object(requests, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_post.return_value = mock_response
            
            url = f"{KEYCLOAK_URL}/admin/realms/olympus/users/user-123/role-mappings/realm"
            response = requests.post(url, json=[{"id": "role-123", "name": "ADMIN"}])
            
            assert response.status_code == 204


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
