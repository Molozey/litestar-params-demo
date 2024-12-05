from pydantic import BaseConfig


class Configuration(BaseConfig):
    PORT: int = 24500

    VERSION: str = "v0.0.1"
