import requests
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración interna (Docker network)
BASE = 'http://keycloak:8080'
ADMIN_USER = 'admin'
ADMIN_PASSWORD = 'admin_password'
REALM = 'olympus'
CLIENT_ID = 'olympus-frontend'

def run():
    print("Iniciando reparación de Keycloak...")
    
    # 1. Obtener Token
    token = None
    for i in range(10):
        try:
            r = requests.post(f'{BASE}/realms/master/protocol/openid-connect/token', 
                             data={'grant_type': 'password', 'client_id': 'admin-cli', 
                                   'username': ADMIN_USER, 'password': ADMIN_PASSWORD},
                             timeout=5)
            token = r.json()['access_token']
            break
        except Exception:
            print("Esperando a Keycloak...")
            time.sleep(5)

    if not token:
        print("❌ No se pudo conectar con Keycloak")
        return

    h = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    # 2. Crear Realm
    requests.post(f'{BASE}/admin/realms', json={'realm': REALM, 'enabled': True}, headers=h)

    # 3. Configurar Cliente
    clients = requests.get(f'{BASE}/admin/realms/{REALM}/clients', headers=h).json()
    client = next((c for c in clients if c['clientId'] == CLIENT_ID), None)
    
    payload = {
        'clientId': CLIENT_ID,
        'enabled': True,
        'publicClient': True,
        'protocol': 'openid-connect',
        'standardFlowEnabled': True,
        'directAccessGrantsEnabled': True,
        'redirectUris': ['http://localhost:3000/*', 'http://127.0.0.1:3000/*'],
        'webOrigins': ['*']
    }

    if client:
        requests.put(f'{BASE}/admin/realms/{REALM}/clients/{client["id"]}', json=payload, headers=h)
    else:
        requests.post(f'{BASE}/admin/realms/{REALM}/clients', json=payload, headers=h)

    # 4. Usuario
    requests.post(f'{BASE}/admin/realms/{REALM}/users', 
                 json={'username': 'funcionario1', 'enabled': True, 'email': 'f1@olympus.gov'}, headers=h)
    
    users = requests.get(f'{BASE}/admin/realms/{REALM}/users?username=funcionario1', headers=h).json()
    if users:
        uid = users[0]['id']
        requests.put(f'{BASE}/admin/realms/{REALM}/users/{uid}/reset-password', 
                     json={'type': 'password', 'value': 'password123', 'temporary': False}, headers=h)

    print("✅ KEYCLOAK REPARADO: Entra en http://localhost:3000")

if __name__ == "__main__":
    run()
