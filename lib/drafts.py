"""Save drafts to disk so a human reviews before anything is published.

The review step is deliberate: a person should look at every post before it
goes out. Drafts are written as JSON to a `drafts/` directory.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from .captions import Caption
from .media import MediaAsset

DRAFTS_DIR = "drafts"


@dataclass(frozen=True)
class Draft:
    created_at: str
    keyword: str
    media: MediaAsset
    caption: Caption

    def to_dict(self) -> dict:
        return {
            "created_at": self.created_at,
            "keyword": self.keyword,
            "media": asdict(self.media),
            "caption": {
                "text": self.caption.text,
                "hashtags": self.caption.hashtags,
                "rendered": self.caption.render(),
            },
        }


def build_draft(keyword: str, media: MediaAsset, caption: Caption) -> Draft:
    return Draft(
        created_at=datetime.now(timezone.utc).isoformat(),
        keyword=keyword,
        media=media,
        caption=caption,
    )


def save_draft(draft: Draft, drafts_dir: str = DRAFTS_DIR) -> str:
    os.makedirs(drafts_dir, exist_ok=True)
    stamp = draft.created_at.replace(":", "").replace("-", "").replace(".", "")
    filename = f"{stamp}_{draft.keyword.replace(' ', '-')}.json"
    path = os.path.join(drafts_dir, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(draft.to_dict(), fh, indent=2)
    return path
