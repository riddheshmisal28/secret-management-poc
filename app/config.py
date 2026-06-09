import os

from infisical_provider import InfisicalSecretProvider


provider = InfisicalSecretProvider(
    host=os.getenv("INFISICAL_HOST"),
    client_id=os.getenv("INFISICAL_CLIENT_ID"),
    client_secret=os.getenv("INFISICAL_CLIENT_SECRET"),
    project_id=os.getenv("INFISICAL_PROJECT_ID"),
    environment=os.getenv("INFISICAL_ENV", "dev")
)


class Config:

    DB_HOST = provider.get_secret("DB_HOST")
    DB_USER = provider.get_secret("DB_USER")
    DB_PASSWORD = provider.get_secret("DB_PASSWORD")
    JWT_SECRET = provider.get_secret("JWT_SECRET")