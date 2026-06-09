from config import Config


def mask(value):
    return "*" * len(value)


print("=== Configuration Loaded ===")
print(f"DB_HOST: {Config.DB_HOST}")
print(f"DB_USER: {Config.DB_USER}")
print(f"DB_PASSWORD: {mask(Config.DB_PASSWORD)}")
print(f"JWT_SECRET: {mask(Config.JWT_SECRET)}")