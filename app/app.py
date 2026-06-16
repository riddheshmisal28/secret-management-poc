import os
import hvac
import psycopg2

print("ROLE_ID =", repr(os.getenv("VAULT_ROLE_ID")))
print("SECRET_ID =", repr(os.getenv("VAULT_SECRET_ID")))

client = hvac.Client(
    url="http://vault:8200"
)

login = client.auth.approle.login(
    role_id=os.getenv("VAULT_ROLE_ID"),
    secret_id=os.getenv("VAULT_SECRET_ID")
)

client.token = login["auth"]["client_token"]

creds = client.read(
    "database/creds/readonly"
)

username = creds["data"]["username"]
password = creds["data"]["password"]

print("Generated User:", username)

conn = psycopg2.connect(
    host="postgres",
    database="myapp",
    user=username,
    password=password
)

print("Connected successfully!")

conn.close()