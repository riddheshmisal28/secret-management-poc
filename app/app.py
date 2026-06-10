import os
import hvac

client = hvac.Client(
    url=os.getenv("VAULT_ADDR"),
    token=os.getenv("VAULT_TOKEN")
)

secret = client.secrets.kv.v2.read_secret_version(
    path="myapp"
)

data = secret["data"]["data"]

print(data["DB_USER"])
print(data["DB_PASSWORD"])