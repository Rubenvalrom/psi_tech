from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError
import time
import os
import logging

logger = logging.getLogger(__name__)

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
KEYCLOAK_ADMIN_USER = os.getenv("KEYCLOAK_ADMIN_USER", "admin")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin_password")
REALM_NAME = "olympus"

def setup_keycloak():
    """Setup Keycloak realm, clients, and test user."""
    # Wait for Keycloak to be ready
    logger.info("Waiting for Keycloak...")
    time.sleep(15) 

    try:
        keycloak_admin = KeycloakAdmin(server_url=f"{KEYCLOAK_URL}/",
                                     username=KEYCLOAK_ADMIN_USER,
                                     password=KEYCLOAK_ADMIN_PASSWORD,
                                     realm_name="master",
                                     verify=True)
    except Exception as e:
        logger.error(f"Failed to connect to Keycloak: {e}")
        return

    # Create Realm if not exists
    try:
        realms = keycloak_admin.get_realms()
        realm_names = [realm['realm'] for realm in realms]
        if REALM_NAME not in realm_names:
            logger.info(f"Creating realm '{REALM_NAME}'...")
            keycloak_admin.create_realm(payload={"realm": REALM_NAME, "enabled": True})
        else:
            logger.info(f"Realm '{REALM_NAME}' already exists.")
    except KeycloakError as e:
        logger.error(f"Error checking/creating realm: {e}")

    # Switch to realm
    keycloak_admin.realm_name = REALM_NAME

    # Create Clients
    clients = keycloak_admin.get_clients()
    client_ids = [client.get('clientId') for client in clients]
    
    # 1. Backend Client (Confidential) - though frontend calls it directly? 
    # Usually frontend calls API with token. Backend verifies token.
    # Frontend needs a public client.
    
    frontend_client_id = "olympus-frontend"
    if frontend_client_id not in client_ids:
        logger.info(f"Creating public client '{frontend_client_id}'...")
        keycloak_admin.create_client(payload={
            "clientId": frontend_client_id,
            "enabled": True,
            "publicClient": True,
            "redirectUris": ["http://localhost:3000/*", "http://frontend:3000/*"],
            "webOrigins": ["+"],
            "standardFlowEnabled": True,
            "directAccessGrantsEnabled": True
        })

    # Create Roles
    roles = ["admin", "funcionario", "gestor_financiero"]
    existing_roles = [role['name'] for role in keycloak_admin.get_realm_roles()]
    
    for role in roles:
        if role not in existing_roles:
            keycloak_admin.create_realm_role(payload={"name": role})

    # Create User
    test_user_username = "funcionario1"
    users = keycloak_admin.get_users({"username": test_user_username})
    
    if not users:
        logger.info(f"Creating test user '{test_user_username}'...")
        new_user_id = keycloak_admin.create_user(payload={
            "username": test_user_username,
            "email": "funcionario1@olympus.gov",
            "firstName": "Juan",
            "lastName": "Funcionario",
            "enabled": True,
            "emailVerified": True
        })
        keycloak_admin.set_user_password(user_id=new_user_id, password="password123", temporary=False)
        
        # Assign Role
        role = keycloak_admin.get_realm_role("funcionario")
        keycloak_admin.assign_realm_roles(user_id=new_user_id, roles=[role])

    logger.info("Keycloak setup complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    setup_keycloak()
