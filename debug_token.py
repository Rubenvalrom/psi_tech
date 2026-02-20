#!/usr/bin/env python3
"""
Debug script: Obtiene un token de Keycloak y verifica el 'audience' para diagnóstico
"""
import requests
import json
import sys
from base64 import urlsafe_b64decode

def decode_token_payload(token: str):
    """Decode JWT token WITHOUT verification to inspect payload."""
    try:
        # JWT format: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            print("❌ Token format invalid (expected 3 parts separated by '.')")
            return None
        
        # Decode payload (add padding if needed)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = json.loads(urlsafe_b64decode(payload))
        return decoded
    except Exception as e:
        print(f"❌ Error decoding token: {e}")
        return None

def main():
    print("🔍 DIAGNÓSTICO: JWT Audience desde Keycloak\n")
    
    keycloak_url = "http://localhost:8080"
    realm = "olympus"
    client_id = "olympus-frontend"
    
    # Step 1: Obtener token con password flow (usuario existente)
    print(f"📌 Conectando a Keycloak en {keycloak_url}/realms/{realm}")
    token_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"
    
    # Credenciales para obtener token (usa test user que teóricamente existe)
    # Si no existe, intentamos con admin
    test_credentials = [
        {"username": "admin", "password": "admin_password", "client_id": "admin-cli"},
        {"username": "testuser", "password": "password123", "client_id": client_id},
    ]
    
    token_response = None
    for creds in test_credentials:
        print(f"\n🔐 Intentando login con usuario: {creds['username']}")
        try:
            response = requests.post(
                token_url,
                data={
                    'grant_type': 'password',
                    'client_id': creds['client_id'],
                    'username': creds['username'],
                    'password': creds['password']
                },
                timeout=5
            )
            
            if response.status_code == 200:
                token_response = response.json()
                print(f"✅ Token obtenido para: {creds['username']}")
                break
            else:
                print(f"❌ Error {response.status_code}: {response.text[:100]}")
        except requests.RequestException as e:
            print(f"❌ Error de conexión: {e}")
    
    if not token_response:
        print("\n❌ No se pudo obtener token de Keycloak.")
        print("   Verifica que:")
        print("   - Keycloak está corriendo en http://localhost:8080")
        print("   - El cliente 'olympus-frontend' existe")
        print("   - Los usuarios existen")
        sys.exit(1)
    
    # Step 2: Decodificar y analizar el token
    access_token = token_response.get('access_token')
    if not access_token:
        print("❌ No se recibió access_token en la respuesta")
        sys.exit(1)
    
    payload = decode_token_payload(access_token)
    if not payload:
        sys.exit(1)
    
    # Step 3: Mostrar información crítica
    print("\n" + "="*70)
    print("📋 JWT PAYLOAD DECODIFICADO:")
    print("="*70)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    # Step 4: Análisis de audience
    aud = payload.get('aud')
    backend_expected_aud = "account"  # Por defecto en config.py
    
    print("\n" + "="*70)
    print("🎯 ANÁLISIS DE AUDIENCE:")
    print("="*70)
    print(f"Audience en el token (aud):     {aud}")
    print(f"Audience esperado en backend:   {backend_expected_aud}")
    
    if isinstance(aud, list):
        if backend_expected_aud in aud:
            print(f"✅ '{backend_expected_aud}' está en la lista de audiences")
        else:
            print(f"❌ MISMATCH: '{backend_expected_aud}' NO está en la lista")
            print(f"   El backend rechazará este token")
    elif isinstance(aud, str):
        if aud == backend_expected_aud:
            print(f"✅ Audience coincide perfectamente")
        else:
            print(f"❌ MISMATCH: '{aud}' != '{backend_expected_aud}'")
            print(f"   El backend rechazará este token")
    
    print("\n" + "="*70)
    print("✅ RECOMENDACIONES:")
    print("="*70)
    if not (isinstance(aud, list) and backend_expected_aud in aud) and aud != backend_expected_aud:
        print(f"1. Cambia backend/app/core/config.py línea 20:")
        print(f"   Antes: JWT_AUDIENCE = \"account\"")
        print(f"   Después: JWT_AUDIENCE = \"{aud}\"")
        print(f"\n2. O configura Keycloak para emitir audience 'account'")
    else:
        print("El audience está correctamente configurado ✅")

if __name__ == "__main__":
    main()
