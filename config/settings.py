"""Configuration comes from the environment or an untracked .env file."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    movies_url: str
    auth_url: str
    timeout: float
    admin_email: str = field(repr=False)
    admin_password: str = field(repr=False)
    admin_token: str = field(repr=False)

    @classmethod
    def from_env(cls):
        load_dotenv(Path(__file__).resolve().parents[1] / ".env")
        timeout = float(os.getenv("REQUEST_TIMEOUT", "30"))
        if timeout <= 0:
            raise ValueError("REQUEST_TIMEOUT must be positive")
        return cls(
            movies_url=os.getenv(
                "MOVIES_BASE_URL", "https://api.dev-cinescope.coconutqa.ru"
            ),
            auth_url=os.getenv(
                "AUTH_BASE_URL", "https://auth.dev-cinescope.coconutqa.ru"
            ),
            timeout=timeout,
            admin_email=os.getenv("ADMIN_EMAIL", ""),
            admin_password=os.getenv("ADMIN_PASSWORD", ""),
            admin_token=os.getenv("ADMIN_TOKEN", ""),
        )
