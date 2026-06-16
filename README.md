# 🔑 Secret Management POC (HashiCorp Vault Dynamic Database Secrets)

This branch (`feature/hashicorp-vault-dynamic-secrets`) implements a highly secure, modern secrets-management proof of concept demonstrating how to generate and use **Vault Dynamic Database Secrets** in a containerized Python application.

Instead of sharing or hardcoding static database passwords, this pattern enables the application to authenticate via **AppRole** and request dynamic, short-lived PostgreSQL credentials on-the-fly. Vault dynamically creates a temporary database role, provisions a unique password, hands it to the application, and automatically revokes it when the Time-To-Live (TTL) expires.

---

## 🏗️ Architecture & Workflow

The architecture orchestrates three services: the Vault Server (dev mode), a PostgreSQL Database, and the client Python Application.

```mermaid
flowchart TD
    subgraph local_env ["Docker Orchestration"]
        Docker["docker-compose.yml"]
        Vault["Vault Server (Dev Mode)"]
        Postgres["PostgreSQL Database"]
        App["Python App (app.py)"]
    end

    Docker -->|1. Inject AppRole Credentials via Env| App
    App -->|2. Authenticate: AppRole Login| Vault
    Vault -->|3. Validate & Return Client Token| App
    App -->|4. Read Dynamic Creds: database/creds/readonly| Vault
    Vault -->|5. Create Temp Postgres Role & Password| Postgres
    Vault -->|6. Return Dynamic DB Username & Password| App
    App -->|7. Connect & Authenticate| Postgres
```

---

## 📁 Directory Structure

```text
├── app/
│   ├── app.py                # App entrypoint: authenticates via AppRole, fetches dynamic DB creds, connects to Postgres
│   ├── config.py             # Config class mapping (defined for abstraction)
│   └── secret_provider.py    # Interface blueprint (SecretProvider ABC)
├── Dockerfile                # Packages the Python app and its dependencies
├── docker-compose.yml        # Orchestrates Vault, Postgres, and the client application
└── requirements.txt          # Python dependencies (hvac, psycopg2-binary)
```

---

## 🚀 Setup & Usage Guide

### Prerequisites
- Docker and Docker Compose installed and running.

---

### Step 1: Start Vault and PostgreSQL Services
Start the helper containers in the background and ensure they are healthy:

```bash
docker compose up -d vault postgres
```

---

### Step 2: Configure Vault AppRole & Database Secrets Engine
Because Vault's developer server runs completely in-memory, we must configure the database engine and authentication paths dynamically.

#### 1. Enter the Vault container shell
```bash
docker compose exec vault sh
```

#### 2. Configure Vault environment variables inside the container
```bash
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=root
```

#### 3. Enable the Database Secrets Engine
```bash
vault secrets enable database
```

#### 4. Configure Vault with PostgreSQL Connection Details
Configure Vault to connect to our PostgreSQL container using the administrator account (`postgres`/`postgres`):
```bash
vault write database/config/my-postgresql-database \
    plugin_name=postgresql-database-plugin \
    allowed_roles="readonly" \
    connection_url="postgresql://{{username}}:{{password}}@postgres:5432/myapp?sslmode=disable" \
    username="postgres" \
    password="postgres"
```

#### 5. Create a Vault Database Role
Create the database role mapping named `readonly`. Vault executes these statements to dynamically create PostgreSQL roles:
```bash
vault write database/roles/readonly \
    db_name=my-postgresql-database \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"
```

#### 6. Enable AppRole Authentication
```bash
vault auth enable approle
```

#### 7. Create the Read-Only Access Policy
Create a policy permitting read access to the dynamic credentials endpoint:
```bash
cat > myapp-policy.hcl <<EOF
path "database/creds/readonly" {
  capabilities = ["read"]
}
EOF
```
Save the policy to Vault under the name `myapp-policy`:
```bash
vault policy write myapp-policy myapp-policy.hcl
```

#### 8. Create the AppRole Role
Link the policy to the AppRole role named `myapp`:
```bash
vault write auth/approle/role/myapp token_policies="myapp-policy"
```

#### 9. Retrieve AppRole Credentials
Retrieve the **Role ID**:
```bash
vault read auth/approle/role/myapp/role-id
```
*(Save the returned `role_id` value, e.g., `12345678-abcd...`)*

Generate a new **Secret ID**:
```bash
vault write -f auth/approle/role/myapp/secret-id
```
*(Save the returned `secret_id` value, e.g., `98765432-xyz...`)*

#### 10. Exit the container shell
```bash
exit
```

---

### Step 3: Configure Environment Variables
Create a `.env` file in the root of the project (ignored by Git) and populate it with the retrieved credentials:

```env
VAULT_ROLE_ID=<your-retrieved-role-id>
VAULT_SECRET_ID=<your-retrieved-secret-id>
```

---

### Step 4: Run the Application
With Vault configured and credentials written to `.env`, build and launch the Python app:

```bash
docker compose up --build app
```

---

### Step 5: Verify Application Connection & Logs
Verify that the application successfully authenticated to Vault, requested dynamic database credentials, and successfully established a PostgreSQL connection:

```bash
docker compose logs app
```

Expected log output:
```text
ROLE_ID = '12345678-abcd...'
SECRET_ID = '98765432-xyz...'
Generated User: v-approle-readonly-xxxxxxxxx-xxxxxxxx
Connected successfully!
```

---

## 🛡️ Security Features Implemented
1. **Zero Standing Privileges**: No static database credentials are saved in the app code or environments.
2. **Just-in-Time Credentialing**: Unique PostgreSQL user accounts are created on-the-fly and deleted automatically.
3. **Automated Lifecycle Management (TTL)**: Dynamic credentials expire automatically after 1 hour (`default_ttl="1h"`). Vault instructs PostgreSQL to delete or revoke the user when the time expires.
4. **Least Privilege policies**: The AppRole has permission to *only* request database credentials at `database/creds/readonly` and cannot perform any other Vault administrative commands.
