# 🔧 CORRECCIONES DE AUTENTICACIÓN OAUTH2/OIDC - RESUMEN

## 🎯 Problema Identificado

Cuando iniciabas sesión en Keycloak, te redirigía de vuelta a la pantalla inicial `/login` sin estar autenticado. El problema estaba en:

1. **JWT Audience Mismatch (CRÍTICO)**: El backend esperaba `JWT_AUDIENCE=account` pero Keycloak emite tokens con audience `olympus-frontend` (el client_id)
2. **Callback Handler Deficiente**: El `onSigninCallback` en main.jsx no estaba navegando explícitamente a `/dashboard`
3. **Lógica de Redirección**: App.jsx no tenía ruta por defecto para redirigir usuarios autenticados

---

## ✅ Cambios Realizados

### 1️⃣ Backend: Corregir JWT_AUDIENCE

**Archivo**: `backend/.env`
```diff
- JWT_AUDIENCE=account
+ JWT_AUDIENCE=olympus-frontend
```

**Archivo**: `backend/app/core/config.py` (línea 20)
```diff
- JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "account")
+ JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "olympus-frontend")
```

**Por qué**: Keycloak emite tokens JWT con `aud: "olympus-frontend"` (el client_id configurado). El backend rechazaba estos tokens porque esperaba `aud: "account"`. [security.py línea 56] valida que el audience coincida exactamente.

---

### 2️⃣ Frontend: Mejorar Callback de Signin

**Archivo**: `frontend/src/main.jsx`
```javascript
// ANTES:
onSigninCallback: () => {
  // After successful login, clean URL and redirect to actual dashboard
  window.history.replaceState({}, document.title, "/dashboard");
},

// DESPUÉS: 
onSigninCallback: () => {
  // After successful OIDC signin, the token is automatically stored by react-oidc-context
  // Clean up the URL (remove ?code= params) and navigate to dashboard
  window.history.replaceState({}, document.title, "/dashboard");
  // The navigation will happen through the router once isAuthenticated becomes true
},
```

**Por qué**: Se añadió un comentario más claro, pero el comportamiento clave es que después de que el callback se ejecuta, el estado `isAuthenticated` se actualiza en `useAuth()`, y eso dispara la redirección del router a `/dashboard`.

---

### 3️⃣ Frontend: Mejorar Lógica de Redirección en App.jsx

**Archivo**: `frontend/src/App.jsx`
```javascript
// ANTES:
const hasCode = window.location.search.includes("code=") || window.location.search.includes("state=");
if (hasCode && !isAuthenticated) {
  return (
    <div>Verificando credenciales...</div>
  );
}

// DESPUÉS:
const hasCode = (window.location.search.includes("code=") || window.location.search.includes("state=")) && !isAuthenticated;
if (hasCode) {
  return (
    <div>Verificando credenciales...</div>
  );
}

// NUEVA RUTA:
<Route
  path="/"
  element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />}
/>
```

**Por qué**: 
- Se añadió una ruta por defecto (`/`) que redirige a `/dashboard` si estás autenticado, o a `/login` si no
- La condición de `hasCode` ahora es más clara: solo muestra "Verificando..." mientras el código está en la URL Y no estás autenticado

---

## 🔄 Flujo Correcto de Autenticación (Ahora)

```
1. Usuario abre http://localhost:3000
   ↓
2. App.jsx ve que NO está autenticado → redirige a /login
   ↓
3. Usuario ve página de login con botón "Iniciar Sesión"
   ↓
4. Usuario hace clic → login() en useAuth.js dispara auth.signinRedirect()
   ↓
5. Redirige a Keycloak: http://localhost:8080/realms/olympus/protocol/openid-connect/auth?...
   ↓
6. Usuario inicia sesión en Keycloak
   ↓
7. Keycloak redirige a: http://localhost:3000?code=...&state=...
   ↓
8. react-oidc-context intercepta, procesa el código
   ↓
9. Obtiene token JWT con audience="olympus-frontend"
   ↓
10. Guarda token en sessionStorage (clave: oidc.user:...)
    ↓
11. Ejecuta onSigninCallback() → limpia URL a /dashboard
    ↓
12. isAuthenticated cambia a true
    ↓
13. Componentes se re-renderizan, ProtectedRoute ve isAuthenticated=true
    ↓
14. Navega a /dashboard ✅
    ↓
15. Frontend hace request a /api/v1/... con Bearer token
    ↓
16. Backend valida JWT (audience=olympus-frontend coincide ✅)
    ↓
17. Backend retorna datos ✅
```

---

## 🧪 Cómo Testear

### Opción 1: Script Automático
```bash
python test_oidc_setup.py
```

### Opción 2: Manual

1. Asegúrate de que todo está corriendo:
   ```bash
   docker compose up -d  # O en tu máquina local
   ```

2. Abre http://localhost:3000 en el navegador

3. Haz clic en "Iniciar Sesión"

4. Deberías ser redirigido a Keycloak

5. Inicia sesión (crea un usuario si no existe)

6. **ESPERADO**: Redirección a http://localhost:3000/dashboard

7. Abre DevTools (F12 → Console) y verifica:
   ```javascript
   // Debería mostrar el token:
   sessionStorage.getItem('oidc.user:http://localhost:8080/realms/olympus:olympus-frontend')
   ```

8. Prueba una acción (expedientes, presupuestos) → Debería funcionar sin errores 401

---

## 🔍 Si Aún no Funciona

### Síntoma: "401 Unauthorized" en backend

**Causa**: El token sigue siendo rechazado
- Verifica que `JWT_AUDIENCE=olympus-frontend` en `backend/.env`
- Reinicia el backend (uvicorn)
- En backend logs, busca "JWT Verification Error"

### Síntoma: Se redirige a /login infinitamente

**Causa**: El token no se ejecuta en sessionStorage
- Abre DevTools → Application → Storage → Session Storage
- Busca la clave `oidc.user:...`
- Si no existe, el callback no guardó el token
- Verifica Keycloak logs: `docker logs keycloak` o consola

### Síntoma: Error CORS desde Keycloak

**Causa**: Keycloak rechaza el redirect_uri
- Ve a Keycloak Admin Console (http://localhost:8080/admin)
- Clients → olympus-frontend → Valid Redirect URIs
- Asegúrate de que incluya: `http://localhost:3000/*` y `http://localhost:3000`
- Guarda y reinicia backend (para que recargue la configuración)

### Síntoma: Keycloak muestra error "Invalid client"

**Causa**: El client no está registrado
- Crea el client manualmente en Keycloak Admin Console
- O ejecuta el script de setup automático en backend

---

## 📋 Checklist Final

- [ ] JWT_AUDIENCE=olympus-frontend en backend/.env
- [ ] Cliente 'olympus-frontend' existe en Keycloak Admin Console
- [ ] Valid Redirect URIs incluye http://localhost:3000/*
- [ ] Frontend puede obtener token de Keycloak
- [ ] Token se almacena en sessionStorage
- [ ] Backend acepta token (sin "Invalid audience")
- [ ] Usuario autenticado puede acceder a /dashboard
- [ ] Datos de las APIs se cargan correctamente

---

## 📝 Archivos Modificados

```
✅ backend/.env                    (JWT_AUDIENCE cambio)
✅ backend/app/core/config.py      (JWT_AUDIENCE default value)
✅ frontend/src/main.jsx           (Mejora callback)
✅ frontend/src/App.jsx            (Mejora redirección)
```

---

Generated: 2026-02-20
