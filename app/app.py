from config import Config


def main(secret_provider):
    config = Config(secret_provider)

    print(f"DB Host: {config.db_host}")
    print(f"DB User: {config.db_user}")
    print(
        f"DB Password: {'*' * len(config.db_password)}"
    )


if __name__ == "__main__":
    raise Exception(
        "No secret provider configured"
    )