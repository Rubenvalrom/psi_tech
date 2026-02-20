#!/usr/bin/env python3
"""
Test script: Verifica que el flujo de login OIDC con Keycloak esté funcionando
"""
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_services_running():
    """Verifica que Frontend, Backend y Keycloak estén corriendo"""
    print("\n" + "="*70)
    print("1️⃣  VERIFICANDO SERVICIOS")
    print("="*70)
    
    services = {
        "Frontend (http://localhost:3000)": "http://localhost:3000",
        "Backend (http://localhost:8000)": "http://localhost:8000/api/v1/health",
        "Keycloak (http://localhost:8080)": "http://localhost:8080",
    }
    
    all_running = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            if response.status_code in [200, 401, 403]:  # 401/403 son OK para salud
                print(f"✅ {name} - respondiendo")
            else:
                print(f"⚠️  {name} - status {response.status_code}")
        except requests.RequestException:
            print(f"❌ {name} - NO responde")
            all_running = False
    
    if not all_running:
        print("\n⚠️  NO TODOS LOS SERVICIOS ESTÁN CORRIENDO")
        print("   En Docker:")
        print("   $ docker compose up -d")
        print("\n   Localmente en 3 terminales:")
        print("   Terminal 1: cd backend && python main.py")
        print("   Terminal 2: cd frontend && npm run dev")
        print("   Terminal 3 (si no está activo): docker compose up keycloak db")
        return False
    
    print("✅ Todos los servicios están corriendo\n")
    return True


def check_backend_config():
    """Verifica que el backend está configurado con JWT_AUDIENCE correcto"""
    print("="*70)
    print("2️⃣  VERIFICANDO CONFIGURACIÓN DEL BACKEND")
    print("="*70)
    
    backend_env = Path("backend/.env")
    if not backend_env.exists():
        print("❌ backend/.env no existe")
        return False
    
    with open(backend_env) as f:
        content = f.read()
    
    if "JWT_AUDIENCE=olympus-frontend" in content:
        print("✅ JWT_AUDIENCE=olympus-frontend en backend/.env")
    else:
        print("❌ JWT_AUDIENCE no está configurado como 'olympus-frontend'")
        print("   Busca esta línea en backend/.env:")
        print("   JWT_AUDIENCE=olympus-frontend")
        return False
    
    return True


def check_keycloak_client():
    """Verifica que el cliente Keycloak está registrado y configurado"""
    print("\n" + "="*70)
    print("3️⃣  VERIFICANDO KEYCLOAK CLIENT")
    print("="*70)
    print("┌─ MANUAL CHECK ─────────────────────────────────────────┐")
    print("│ 1. Ve a http://localhost:8080/admin                    │")
    print("│ 2. Administración → Realms → 'olympus'                 │")
    print("│ 3. Clients → 'olympus-frontend'                        │")
    print("│ 4. Verifica:                                           │")
    print("│    ✓ Client ID: olympus-frontend                       │")
    print("│    ✓ Valid Redirect URIs: http://localhost:3000/*      │")
    print("│    ✓ Valid Post Logout URIs: http://localhost:3000/*   │")
    print("│    ✓ Web Origins: * (or http://localhost:3000)         │")
    print("│    ✓ Public Client: ON (si es Single Page App)         │")
    print("└────────────────────────────────────────────────────────┘")
    print("\n⚠️  Esta verificación es MANUAL. Consulta tu Admin Console de Keycloak.")
    return True


def print_test_instructions():
    """Imprime instrucciones para testear el flujo"""
    print("\n" + "="*70)
    print("4️⃣  INSTRUCCIONES PARA TESTEAR")
    print("="*70)
    print("""
    1. Abre http://localhost:3000 en el navegador
    
    2. Deberías ver:
       ✓ Pantalla de LOGIN con botón "Iniciar Sesión"
       ✓ NO deberías estar redirigido a /login automáticamente
    
    3. Haz clic en "Iniciar Sesión"
       ✓ Deberías ser redirigido a Keycloak
       ✓ Ves FORMULARIO DE LOGIN de Keycloak
    
    4. Inicia sesión con credenciales válidas en Keycloak
       Nota: Si no tienes usuario, crea uno:
       - Admin Console de Keycloak
       - Realms → olympus → Users → Create user
    
    5. DESPUÉS DEL LOGIN EN KEYCLOAK:
       ✓ ESPERADO: Redirección a http://localhost:3000/dashboard
       ✓ Dashboard carga correctamente
       ✓ Puedes ver datos (expedientes, presupuestos, etc.)
       ✓ Avatar/usuario aparece en top-right
    
    6. PROBLEMA SI:
       ❌ Se redirige a http://localhost:3000/login (SIN estar autenticado)
       ❌ Página está en blanco o congela
       ❌ Error de CORS en DevTools
       ❌ Error "Invalid audience" en backend logs
    
    ---
    
    DEBUGGEAR CON DEVTOOLS (F12):
    
    • Console:
      - ¿Hay errores de CORS?
      - ¿Hay errores de "Invalid audience"?
    
    • Network:
      - Busca llamadas a Keycloak: ¿Cuál es el status?
      - Busca llamadas al backend (/api/v1/*): ¿401 o 200?
    
    • Application → Storage:
      - sessionStorage debería tener:
        Clave: oidc.user:http://localhost:8080/realms/olympus:olympus-frontend
        Valor: {\"access_token\": \"...\", \"id_token\": \"...\"}
    
    ---
    
    BACKEND LOGS:
    
    • Busca líneas como:
      ✓ "JWT Verification Error" → audience mismatch
      ✓ "Auto-provisioning user admin" → usuario creado automáticamente
      ✓ "Failed to fetch JWKS" → Keycloak no responde
    """)


def main():
    print("\n" + "🔍 TEST: SETUP DE AUTENTICACIÓN OAUTH2/OIDC KEYCLOAK")
    print("="*70)
    
    # Check 1: Services
    if not check_services_running():
        sys.exit(1)
    
    # Check 2: Backend config
    if not check_backend_config():
        sys.exit(1)
    
    # Check 3: Keycloak (manual)
    check_keycloak_client()
    
    # Check 4: Test instructions
    print_test_instructions()
    
    print("\n" + "="*70)
    print("✅ VERIFICACIONES COMPLETADAS")
    print("="*70)
    print("""
Próximos pasos:
1. Asegúrate de que TODOS los servicios estén corriendo
2. Abre http://localhost:3000 y prueba el login
3. Si hay errores, revisa los logs del backend (línea: "JWT Verification Error")
4. Si "Invalid audience", revisa que JWT_AUDIENCE=olympus-frontend
5. Si Keycloak no responde, instancia puede estar caída
    """)


if __name__ == "__main__":
    main()
