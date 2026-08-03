"""Source royalty-free media from the Pexels API.

Pexels media is free to use under the Pexels License, but attribution is
appreciated and, for many uses, expected. Every result carries the
photographer/creator credit so you can attribute properly.
"""

from __future__ import annotations

from dataclasses import dataclass

import requests

PEXELS_PHOTO_URL = "https://api.pexels.com/v1/search"
PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"
DEFAULT_TIMEOUT = 30


@dataclass(frozen=True)
class MediaAsset:
    """A single sourced piece of media, ready to review before posting."""

    kind: str  # "photo" or "video"
    url: str  # public, hostable URL of the asset
    preview_url: str  # small image to eyeball in a review step
    creator: str  # who made it — attribute them
    source_page: str  # link back to the asset on Pexels

    def attribution(self) -> str:
        return f"Photo/Video by {self.creator} on Pexels ({self.source_page})"


class MediaError(RuntimeError):
    """Raised when media sourcing fails."""


def _get(url: str, api_key: str, params: dict) -> dict:
    resp = requests.get(
        url,
        headers={"Authorization": api_key},
        params=params,
        timeout=DEFAULT_TIMEOUT,
    )
    if resp.status_code == 401:
        raise MediaError("Pexels rejected the API key (401). Check PEXELS_API_KEY.")
    resp.raise_for_status()
    return resp.json()


def search_photo(keyword: str, api_key: str) -> MediaAsset:
    data = _get(PEXELS_PHOTO_URL, api_key, {"query": keyword, "per_page": 1})
    photos = data.get("photos") or []
    if not photos:
        raise MediaError(f"No Pexels photos found for keyword {keyword!r}.")
    p = photos[0]
    return MediaAsset(
        kind="photo",
        url=p["src"]["large2x"],
        preview_url=p["src"]["medium"],
        creator=p.get("photographer", "Unknown"),
        source_page=p.get("url", ""),
    )


def search_video(keyword: str, api_key: str) -> MediaAsset:
    data = _get(PEXELS_VIDEO_URL, api_key, {"query": keyword, "per_page": 1})
    videos = data.get("videos") or []
    if not videos:
        raise MediaError(f"No Pexels videos found for keyword {keyword!r}.")
    v = videos[0]
    files = sorted(
        v.get("video_files", []),
        key=lambda f: (f.get("width") or 0),
        reverse=True,
    )
    if not files:
        raise MediaError(f"Pexels video for {keyword!r} had no downloadable files.")
    return MediaAsset(
        kind="video",
        url=files[0]["link"],
        preview_url=v.get("image", ""),
        creator=v.get("user", {}).get("name", "Unknown"),
        source_page=v.get("url", ""),
    )
