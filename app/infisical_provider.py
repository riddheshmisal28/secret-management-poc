import requests

from secret_provider import SecretProvider


class InfisicalSecretProvider(SecretProvider):

    def __init__(
        self,
        host,
        client_id,
        client_secret,
        project_id,
        environment="dev"
    ):
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.project_id = project_id
        self.environment = environment

        self.access_token = self._login()

    def _login(self):

        response = requests.post(
            f"{self.host}/api/v1/auth/universal-auth/login",
            json={
                "clientId": self.client_id,
                "clientSecret": self.client_secret
            }
        )

        print("LOGIN STATUS:", response.status_code)
        print("LOGIN RESPONSE:", response.text)

        response.raise_for_status()

        return response.json()["accessToken"]

    def _load_secrets(self):

        response = requests.get(
            f"{self.host}/api/v3/secrets/raw",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            params={
                "workspaceId": self.project_id,
                "environment": self.environment
            }
        )

        print("SECRETS STATUS:", response.status_code)
        print("SECRETS RESPONSE:", response.text)

        response.raise_for_status()

        return {
            secret["secretKey"]: secret["secretValue"]
            for secret in response.json()["secrets"]
        }

    def get_secret(self, key):

        secrets = self._load_secrets()

        return secrets.get(key)