"""Compose captions and curated hashtag sets.

Hashtags are drawn from a local, curated file you control (`lib/hashtags.txt`),
grouped by niche. No scraping of third-party sites at import time — that was
fragile and opaque about where the tags came from. You own your tag lists.
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass

HASHTAGS_FILE = os.path.join(os.path.dirname(__file__), "hashtags.txt")

# Instagram allows up to 30 hashtags; a curated 8–15 tends to read better than
# a wall of 30. We cap conservatively.
MAX_HASHTAGS = 15


@dataclass(frozen=True)
class Caption:
    text: str
    hashtags: list[str]

    def render(self) -> str:
        tag_line = " ".join(self.hashtags)
        return f"{self.text}\n\n{tag_line}".strip()


def load_hashtags(path: str = HASHTAGS_FILE) -> list[str]:
    """Load curated hashtags. Blank lines and `#` comment lines are ignored."""
    if not os.path.exists(path):
        return []
    tags: list[str] = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("# "):
                continue
            tags.append(line if line.startswith("#") else f"#{line}")
    return tags


def pick_hashtags(
    tags: list[str], count: int = MAX_HASHTAGS, rng: random.Random | None = None
) -> list[str]:
    """Pick up to `count` distinct hashtags, preserving no particular order."""
    rng = rng or random.Random()
    count = max(0, min(count, MAX_HASHTAGS, len(tags)))
    return rng.sample(tags, count) if count else []


def compose(
    body: str,
    keyword: str,
    attribution: str | None = None,
    hashtags_path: str = HASHTAGS_FILE,
    rng: random.Random | None = None,
) -> Caption:
    """Build a caption from a human-written body plus curated hashtags.

    `body` is your own writing — this tool arranges and decorates it, it does
    not fabricate a voice for you. That keeps the account genuinely yours.
    """
    tags = pick_hashtags(load_hashtags(hashtags_path), rng=rng)
    text = body.strip()
    if attribution:
        text = f"{text}\n\n{attribution}"
    return Caption(text=text, hashtags=tags)
