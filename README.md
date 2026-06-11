# 🔑 Secret Management POC (HashiCorp Vault AppRole)

This branch (`feature/hashicorp-vault-approle`) implements a secure secrets-management proof of concept demonstrating how to authenticate and fetch secrets dynamically using **HashiCorp Vault**'s **AppRole** authentication method in a containerized Python application.

AppRole is a secure machine-to-machine authentication mechanism in Vault, ideal for APIs, microservices, and containerized workloads. It requires a paired **Role ID** and **Secret ID** to authorize the application and issue a client token.

---

## 🏗️ Architecture & Workflow

The architecture utilizes a Python client container configured with `hvac` (HashiCorp Vault API Client) and a Vault container running in Developer mode.

```mermaid
flowchart TD
    subgraph local_env ["Docker Orchestration"]
        Docker["docker-compose.yml"]
        Vault["Vault Server (Dev Mode)"]
        App["Python App (app.py)"]
    end

    Docker -->|1. Inject AppRole credentials as Env| App
    App -->|2. Authenticate: AppRole Login (role_id and secret_id)| Vault
    Vault -->|3. Validate & Return Client Token| App
    App -->|4. Read Secrets: KV v2 (path: myapp)| Vault
    Vault -->|5. Return Secrets (DB_USER, DB_PASSWORD)| App
```

---

## 📁 Directory Structure

```text
├── app/
│   ├── app.py                # App entrypoint: authenticates using AppRole and prints secrets
│   ├── config.py             # Config class mapping retrieved secrets
│   └── secret_provider.py    # Interface blueprint (SecretProvider ABC)
├── Dockerfile                # Packages the Python app and its dependencies
├── docker-compose.yml        # Orchestrates the local Vault instance and the client application
└── requirements.txt          # Python dependencies (hvac)
```

---

## 🚀 Setup & Usage Guide

### Prerequisites
- Docker and Docker Compose installed and running.

---

### Step 1: Start the Vault Service
Before starting the application, spin up the Vault container in the background to ensure it is healthy and ready to be configured:

```bash
docker compose up -d vault
```

---

### Step 2: Configure Vault AppRole & Secrets
Vault's Developer server runs completely in-memory and starts fresh and unconfigured. To set up the AppRole authentication dynamically, enter the Vault container and configure it:

#### 1. Enter the Vault container shell
```bash
docker compose exec vault sh
```

#### 2. Configure Vault environment variables inside the container
```bash
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=root
```

#### 3. Enable the AppRole authentication method
First, check existing auth methods:
```bash
vault auth list
```
Enable the AppRole auth method:
```bash
vault auth enable approle
```
Verify it was successfully enabled:
```bash
vault auth list
```
*(You should see `approle/` listed in the output.)*

#### 4. Create the read-only policy
Write a policy template defining read-only permissions for `secret/data/myapp`:
```bash
cat > myapp-policy.hcl <<EOF
path "secret/data/myapp" {
  capabilities = ["read"]
}
EOF
```
Write this policy to Vault under the name `myapp-policy`:
```bash
vault policy write myapp-policy myapp-policy.hcl
```
Verify the policy was correctly written:
```bash
vault policy read myapp-policy
```

#### 5. Create the AppRole role
Create a role named `myapp` and map it to your policy:
```bash
vault write auth/approle/role/myapp token_policies="myapp-policy"
```

#### 6. Retrieve the AppRole Credentials
Read the generated **Role ID**:
```bash
vault read auth/approle/role/myapp/role-id
```
*(Save the returned `role_id` value, e.g., `12345678-abcd...`)*

Generate a new **Secret ID**:
```bash
vault write -f auth/approle/role/myapp/secret-id
```
*(Save the returned `secret_id` value, e.g., `98765432-xyz...`)*

#### 7. Seed the application secrets
Populate the Key-Value (KV v2) store at `secret/myapp` with database credentials:
```bash
vault kv put secret/myapp DB_USER="vault_user" DB_PASSWORD="vault_password123"
```

#### 8. Exit the container shell
```bash
exit
```

---

### Step 3: Configure environment variables
Create a `.env` file in the root of the project (which is ignored by Git via `.gitignore`) and insert the credentials you retrieved in Step 6:

```env
VAULT_ROLE_ID=<your-retrieved-role-id>
VAULT_SECRET_ID=<your-retrieved-secret-id>
```

---

### Step 4: Run the Application
With Vault configured and credentials written to `.env`, build and run the Python application container:

```bash
docker compose up --build app
```

---

### Step 5: Verify Application Output
Verify that the application successfully authenticated, retrieved, and printed the secret values:

```bash
docker compose logs app
```

Expected log output:
```text
vault_user
vault_password123
```

---

## 🛡️ Security Features Implemented
1. **Machine-to-Machine Authentication**: Uses AppRole instead of exposing hardcoded root tokens to the application runtime.
2. **Short-Lived Tokens**: Tokens generated via AppRole are configured with automatic TTL and usage limits (e.g., `token_num_uses=10`, `token_ttl=20m`) to minimize attack surface in case of leakage.
3. **Least Privilege access controls**: The `myapp-policy` strictly limits the AppRole permissions to reading only the secrets it needs (`secret/data/myapp`), blocking administrative commands or access to other paths.
