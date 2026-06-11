import os
import hvac

client = hvac.Client(
    url="http://vault:8200"
)

login = client.auth.approle.login(
    role_id=os.getenv("VAULT_ROLE_ID"),
    secret_id=os.getenv("VAULT_SECRET_ID")
)

client.token = login["auth"]["client_token"]

secret = client.secrets.kv.v2.read_secret_version(
    path="myapp",
    raise_on_deleted_version=True
)

data = secret["data"]["data"]

print(data["DB_USER"])
print(data["DB_PASSWORD"])