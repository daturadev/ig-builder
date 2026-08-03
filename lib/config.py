"""Configuration loading.

Secrets come from the environment (or a local .env file), never from
command-line arguments — CLI args leak into shell history and process lists.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv is optional; env vars still work without it.
    pass


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


@dataclass(frozen=True)
class Config:
    """Runtime configuration resolved from the environment."""

    pexels_api_key: str | None
    ig_user_id: str | None
    ig_access_token: str | None
    graph_api_version: str = "v20.0"

    @classmethod
    def load(cls) -> "Config":
        return cls(
            pexels_api_key=os.getenv("PEXELS_API_KEY"),
            ig_user_id=os.getenv("IG_USER_ID"),
            ig_access_token=os.getenv("IG_ACCESS_TOKEN"),
            graph_api_version=os.getenv("GRAPH_API_VERSION", "v20.0"),
        )

    def require_pexels(self) -> str:
        if not self.pexels_api_key:
            raise ConfigError(
                "PEXELS_API_KEY is not set. Get a free key at "
                "https://www.pexels.com/api/ and add it to your .env file."
            )
        return self.pexels_api_key

    def require_publishing(self) -> tuple[str, str]:
        missing = [
            name
            for name, value in (
                ("IG_USER_ID", self.ig_user_id),
                ("IG_ACCESS_TOKEN", self.ig_access_token),
            )
            if not value
        ]
        if missing:
            raise ConfigError(
                "Publishing requires "
                + " and ".join(missing)
                + ". These come from a Business/Creator account you own, "
                "connected to a Facebook Page. See README for setup."
            )
        return self.ig_user_id, self.ig_access_token  # type: ignore[return-value]
