class Config:

    def __init__(self, secret_provider):
        self.db_host = secret_provider.get_secret("DB_HOST")
        self.db_user = secret_provider.get_secret("DB_USER")
        self.db_password = secret_provider.get_secret("DB_PASSWORD")
        self.jwt_secret = secret_provider.get_secret("JWT_SECRET")