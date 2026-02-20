#!/usr/bin/env python3
"""
Initialize Keycloak with realms, roles, clients, and test users.
Usage: python keycloak_init.py [--get-token --user admin --password admin]
"""

import os
import json
import requests
import sys
from typing import Optional

# Configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_ADMIN_USER = os.getenv("KEYCLOAK_ADMIN", "admin")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")
REALM_NAME = "olympus"
CLIENT_ID = "olympus-backend"


class KeycloakManager:
    def __init__(self, keycloak_url: str, admin_user: str, admin_password: str):
        self.keycloak_url = keycloak_url
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.admin_token = None
        self.authenticate()

    def authenticate(self):
        """Get admin access token."""
        token_url = f"{self.keycloak_url}/realms/master/protocol/openid-connect/token"
        payload = {
            "client_id": "admin-cli",
            "username": self.admin_user,
            "password": self.admin_password,
            "grant_type": "password",
        }
        
        try:
            response = requests.post(token_url, data=payload, timeout=10)
            response.raise_for_status()
            self.admin_token = response.json()["access_token"]
            print("✓ Authenticated to Keycloak")
        except Exception as e:
            print(f"✗ Failed to authenticate: {e}")
            sys.exit(1)

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json",
        }

    def create_realm(self, realm_name: str):
        """Create a new realm."""
        url = f"{self.keycloak_url}/admin/realms"
        payload = {
            "realm": realm_name,
            "enabled": True,
            "displayName": "Olimpia Smart Government",
        }
        
        response = requests.post(url, json=payload, headers=self.get_headers(), timeout=10)
        if response.status_code == 201:
            print(f"✓ Created realm '{realm_name}'")
        elif response.status_code == 409:
            print(f"✓ Realm '{realm_name}' already exists")
        else:
            print(f"✗ Failed to create realm: {response.text}")

    def create_roles(self, realm_name: str, roles: list):
        """Create roles."""
        for role_name, description in roles:
            url = f"{self.keycloak_url}/admin/realms/{realm_name}/roles"
            payload = {"name": role_name, "description": description}
            
            response = requests.post(url, json=payload, headers=self.get_headers(), timeout=10)
            if response.status_code in [201, 409]:
                print(f"✓ Role '{role_name}' ready")
            else:
                print(f"✗ Failed to create role '{role_name}': {response.text}")

    def create_client(self, realm_name: str, client_id: str) -> Optional[str]:
        """Create client and return client secret."""
        url = f"{self.keycloak_url}/admin/realms/{realm_name}/clients"
        payload = {
            "clientId": client_id,
            "name": "Olympus Backend API",
            "protocol": "openid-connect",
            "publicClient": False,
            "serviceAccountsEnabled": True,
            "standardFlowEnabled": True,
            "implicitFlowEnabled": False,
            "directAccessGrantsEnabled": True,
            "redirectUris": ["http://localhost:8000/*", "http://localhost:3000/*"],
            "webOrigins": ["*"],
        }
        
        response = requests.post(url, json=payload, headers=self.get_headers(), timeout=10)
        if response.status_code == 201:
            client_uuid = response.json()["id"]
            print(f"✓ Created client '{client_id}'")
            
            # Get client secret
            secret_url = f"{self.keycloak_url}/admin/realms/{realm_name}/clients/{client_uuid}/client-secret"
            secret_response = requests.get(secret_url, headers=self.get_headers(), timeout=10)
            if secret_response.status_code == 200:
                secret = secret_response.json()["value"]
                print(f"  Client Secret: {secret[:20]}...")
                return secret
        elif response.status_code == 409:
            print(f"✓ Client '{client_id}' already exists")
        else:
            print(f"✗ Failed to create client: {response.text}")
        
        return None

    def create_user(self, realm_name: str, username: str, email: str, password: str, roles: list):
        """Create user and assign roles."""
        url = f"{self.keycloak_url}/admin/realms/{realm_name}/users"
        payload = {
            "username": username,
            "email": email,
            "firstName": username.title(),
            "lastName": "TestUser",
            "enabled": True,
            "credentials": [{"type": "password", "value": password, "temporary": False}],
        }
        
        response = requests.post(url, json=payload, headers=self.get_headers(), timeout=10)
        if response.status_code == 201:
            user_id = response.json()["id"]
            print(f"✓ Created user '{username}'")
            
            # Assign roles
            for role_name in roles:
                self.assign_role_to_user(realm_name, user_id, role_name)
        elif response.status_code == 409:
            print(f"✓ User '{username}' already exists")
        else:
            print(f"✗ Failed to create user: {response.text}")

    def assign_role_to_user(self, realm_name: str, user_id: str, role_name: str):
        """Assign a realm role to a user."""
        # Get role ID
        role_url = f"{self.keycloak_url}/admin/realms/{realm_name}/roles/{role_name}"
        role_response = requests.get(role_url, headers=self.get_headers(), timeout=10)
        
        if role_response.status_code != 200:
            print(f"  ✗ Role '{role_name}' not found")
            return
        
        role_id = role_response.json()["id"]
        
        # Assign role to user
        assign_url = f"{self.keycloak_url}/admin/realms/{realm_name}/users/{user_id}/role-mappings/realm"
        assign_payload = [{"id": role_id, "name": role_name}]
        
        assign_response = requests.post(
            assign_url,
            json=assign_payload,
            headers=self.get_headers(),
            timeout=10
        )
        
        if assign_response.status_code in [200, 204]:
            print(f"  ✓ Assigned role '{role_name}' to '{user_id[:8]}...'")
        else:
            print(f"  ✗ Failed to assign role: {assign_response.text}")

    def get_user_token(self, realm_name: str, username: str, password: str) -> Optional[str]:
        """Get access token for a user."""
        token_url = f"{self.keycloak_url}/realms/{realm_name}/protocol/openid-connect/token"
        payload = {
            "client_id": CLIENT_ID,
            "username": username,
            "password": password,
            "grant_type": "password",
        }
        
        try:
            response = requests.post(token_url, data=payload, timeout=10)
            response.raise_for_status()
            return response.json()["access_token"]
        except Exception as e:
            print(f"✗ Failed to get token for user '{username}': {e}")
            return None


def main():
    manager = KeycloakManager(KEYCLOAK_URL, KEYCLOAK_ADMIN_USER, KEYCLOAK_ADMIN_PASSWORD)
    
    # Check for --get-token flag
    if "--get-token" in sys.argv:
        username = "admin"
        password = "admin"
        
        for i, arg in enumerate(sys.argv):
            if arg == "--user" and i + 1 < len(sys.argv):
                username = sys.argv[i + 1]
            elif arg == "--password" and i + 1 < len(sys.argv):
                password = sys.argv[i + 1]
        
        token = manager.get_user_token(REALM_NAME, username, password)
        if token:
            print(f"\nToken for '{username}':")
            print(token)
        return
    
    # Initialize realm, roles, client, users
    print("\n=== Initializing Keycloak ===\n")
    
    manager.create_realm(REALM_NAME)
    
    roles = [
        ("ADMIN", "System administrators"),
        ("FUNCIONARIO", "Government employees"),
        ("GESTOR_FINANCIERO", "Finance managers"),
        ("VIEWER", "Read-only access"),
    ]
    manager.create_roles(REALM_NAME, roles)
    
    client_secret = manager.create_client(REALM_NAME, CLIENT_ID)
    
    print("\nCreating test users...")
    manager.create_user(REALM_NAME, "admin", "admin@olympus.gov", "admin123!", ["ADMIN"])
    manager.create_user(REALM_NAME, "funcionario", "func@olympus.gov", "func123!", ["FUNCIONARIO"])
    manager.create_user(REALM_NAME, "financiero", "fin@olympus.gov", "fin123!", ["GESTOR_FINANCIERO"])
    manager.create_user(REALM_NAME, "viewer", "viewer@olympus.gov", "view123!", ["VIEWER"])
    
    print("\n=== Initialization Complete ===\n")
    
    if client_secret:
        print("Add to .env:")
        print(f'KEYCLOAK_CLIENT_SECRET={client_secret}')


if __name__ == "__main__":
    main()
