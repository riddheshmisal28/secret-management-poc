from config import Config
from secret_provider import EnvSecretProvider


def main():
    provider = EnvSecretProvider()

    config = Config(provider)

    print("=== Configuration Loaded ===")
    print(f"DB_HOST: {config.db_host}")
    print(f"DB_USER: {config.db_user}")
    print(f"DB_PASSWORD: {'*' * len(config.db_password)}")
    print(f"JWT_SECRET: {'*' * len(config.jwt_secret)}")


if __name__ == "__main__":
    main()