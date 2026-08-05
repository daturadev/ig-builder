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

    # Media sourcing.
    pexels_api_key: str | None

    # Instagram (Graph Content Publishing API).
    ig_user_id: str | None
    ig_access_token: str | None
    graph_api_version: str = "v20.0"

    # Threads (Meta Threads API).
    threads_user_id: str | None = None
    threads_access_token: str | None = None

    # YouTube (Data API v3, OAuth2 refresh-token flow).
    youtube_client_id: str | None = None
    youtube_client_secret: str | None = None
    youtube_refresh_token: str | None = None

    # TikTok (Content Posting API).
    tiktok_access_token: str | None = None
    tiktok_direct_post: bool = False

    @classmethod
    def load(cls) -> "Config":
        return cls(
            pexels_api_key=os.getenv("PEXELS_API_KEY"),
            ig_user_id=os.getenv("IG_USER_ID"),
            ig_access_token=os.getenv("IG_ACCESS_TOKEN"),
            graph_api_version=os.getenv("GRAPH_API_VERSION", "v20.0"),
            threads_user_id=os.getenv("THREADS_USER_ID"),
            threads_access_token=os.getenv("THREADS_ACCESS_TOKEN"),
            youtube_client_id=os.getenv("YOUTUBE_CLIENT_ID"),
            youtube_client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
            youtube_refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
            tiktok_access_token=os.getenv("TIKTOK_ACCESS_TOKEN"),
            tiktok_direct_post=os.getenv("TIKTOK_DIRECT_POST", "").lower()
            in ("1", "true", "yes"),
        )

    # --- Per-capability credential guards -------------------------------

    def require_pexels(self) -> str:
        if not self.pexels_api_key:
            raise ConfigError(
                "PEXELS_API_KEY is not set. Get a free key at "
                "https://www.pexels.com/api/ and add it to your .env file."
            )
        return self.pexels_api_key

    def require_instagram(self) -> tuple[str, str]:
        return self._require(
            ("IG_USER_ID", self.ig_user_id),
            ("IG_ACCESS_TOKEN", self.ig_access_token),
            hint="from a Business/Creator account you own, connected to a "
            "Facebook Page. See docs/SETUP_APIS.md.",
        )

    def require_threads(self) -> tuple[str, str]:
        return self._require(
            ("THREADS_USER_ID", self.threads_user_id),
            ("THREADS_ACCESS_TOKEN", self.threads_access_token),
            hint="from the Threads API app you created. See docs/SETUP_APIS.md.",
        )

    def require_youtube(self) -> tuple[str, str, str]:
        return self._require(
            ("YOUTUBE_CLIENT_ID", self.youtube_client_id),
            ("YOUTUBE_CLIENT_SECRET", self.youtube_client_secret),
            ("YOUTUBE_REFRESH_TOKEN", self.youtube_refresh_token),
            hint="from a Google Cloud OAuth client. See docs/SETUP_APIS.md.",
        )

    def require_tiktok(self) -> str:
        (token,) = self._require(
            ("TIKTOK_ACCESS_TOKEN", self.tiktok_access_token),
            hint="from your TikTok developer app. See docs/SETUP_APIS.md.",
        )
        return token

    @staticmethod
    def _require(*pairs: tuple[str, str | None], hint: str) -> tuple:
        missing = [name for name, value in pairs if not value]
        if missing:
            raise ConfigError(
                "Missing " + ", ".join(missing) + " — these come " + hint
            )
        return tuple(value for _, value in pairs)
