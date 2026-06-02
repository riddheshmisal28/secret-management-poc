from abc import ABC, abstractmethod
import os


class SecretProvider(ABC):

    @abstractmethod
    def get_secret(self, key: str) -> str:
        pass


class EnvSecretProvider(SecretProvider):

    def get_secret(self, key: str) -> str:
        value = os.getenv(key)

        if not value:
            raise ValueError(
                f"Missing environment variable: {key}"
            )

        return value