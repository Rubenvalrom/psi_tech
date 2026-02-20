# Keycloak Client Setup

## Realm & Client Creation

### Step 1: Create Realm "olympus" (Manual or Script)

In Keycloak Admin Console:
1. Click "Add Realm"
2. Name: `olympus`
3. Enabled: ON
4. Save

Or via Keycloak API:
```bash
curl -X POST \
  http://keycloak:8080/admin/realms \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "realm": "olympus",
    "enabled": true,
    "displayName": "Olimpia Smart Government"
  }'
```

### Step 2: Create Client "olympus-backend"

**Admin Console**:
1. Realm: olympus → Clients → Create
2. Client ID: `olympus-backend`
3. Client Protocol: `openid-connect`
4. Access Type: `confidential`
5. Standard Flow Enabled: OFF
6. Service Accounts Enabled: ON
7. Valid Redirect URIs: `http://localhost:8000/*` (development)

**API Equivalente**:
```bash
curl -X POST \
  http://keycloak:8080/admin/realms/olympus/clients \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "olympus-backend",
    "name": "Olympus Backend API",
    "protocol": "openid-connect",
    "publicClient": false,
    "serviceAccountsEnabled": true,
    "standardFlowEnabled": true,
    "implicitFlowEnabled": false,
    "directAccessGrantsEnabled": true,
    "redirectUris": ["http://localhost:8000/*"],
    "webOrigins": ["*"]
  }'
```

### Step 3: Get Client Secret

In Admin Console:
1. Clients → olympus-backend → Credentials tab
2. Copy `Secret`

Store in `.env`:
```
KEYCLOAK_CLIENT_SECRET=<copied-secret>
```

## Roles Definition

Create realm roles for Olympus:

```bash
# ADMIN role
curl -X POST \
  http://keycloak:8080/admin/realms/olympus/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ADMIN",
    "description": "System administrators"
  }'

# FUNCIONARIO role
curl -X POST \
  http://keycloak:8080/admin/realms/olympus/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "FUNCIONARIO",
    "description": "Government employees"
  }'

# GESTOR_FINANCIERO role
curl -X POST \
  http://keycloak:8080/admin/realms/olympus/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GESTOR_FINANCIERO",
    "description": "Finance managers"
  }'

# VIEWER role
curl -X POST \
  http://keycloak:8080/admin/realms/olympus/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "VIEWER",
    "description": "Read-only access"
  }'
```

## Test User Creation

Create test users for QA:

```bash
# Admin user
curl -X POST \
  http://keycloak:8080/admin/realms/olympus/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@olympus.gov",
    "firstName": "Admin",
    "lastName": "User",
    "enabled": true,
    "credentials": [{
      "type": "password",
      "value": "admin123!",
      "temporary": false
    }]
  }'

# Funcionario user
curl -X POST \
  http://keycloak:8080/admin/realms/olympus/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "funcionario",
    "email": "func@olympus.gov",
    "firstName": "Jose",
    "lastName": "Funcionario",
    "enabled": true,
    "credentials": [{
      "type": "password",
      "value": "func123!",
      "temporary": false
    }]
  }'
```

Then assign roles to users:

```bash
# Get user ID
USER_ID=$(curl -s \
  http://keycloak:8080/admin/realms/olympus/users?username=admin \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[0].id')

# Get role ID
ROLE_ID=$(curl -s \
  http://keycloak:8080/admin/realms/olympus/roles/ADMIN \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.id')

# Assign role to user
curl -X POST \
  http://keycloak:8080/admin/realms/olympus/users/$USER_ID/role-mappings/realm \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"id": "'$ROLE_ID'", "name": "ADMIN"}]'
```

## JWT Token Structure

Example JWT decoded payload:

```json
{
  "exp": 1708444800,
  "iat": 1708358400,
  "jti": "abc123...",
  "iss": "http://keycloak:8080/realms/olympus",
  "aud": "olympus-backend",
  "sub": "user-uuid-1234",
  "typ": "Bearer",
  "azp": "olympus-backend",
  "preferred_username": "admin",
  "email": "admin@olympus.gov",
  "realm_access": {
    "roles": ["ADMIN", "default-roles-olympus"]
  }
}
```

**Key fields for authorization**:
- `sub`: User ID (use for resource ownership checks)
- `preferred_username`: Username
- `email`: Email address
- `realm_access.roles`: List of roles (check in decorators)

## Configuration Map

| Setting | Dev Value | Prod Value | Notes |
|---------|-----------|-----------|-------|
| KEYCLOAK_URL | http://keycloak:8080 | https://keycloak.olympus.gov | Use HTTPS in prod |
| KEYCLOAK_REALM | olympus | olympus | Same in all envs |
| KEYCLOAK_CLIENT_ID | olympus-backend | olympus-backend | Consistent naming |
| KEYCLOAK_CLIENT_SECRET | <generated> | <vault> | Store in secrets manager |
| JWT_ALGORITHM | RS256 | RS256 | RSA signature |
| TOKEN_EXPIRE_MINUTES | 60 | 15 | Shorter in prod |
