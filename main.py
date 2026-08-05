#!/usr/bin/env python3
"""InstaForm — draft (and optionally publish) Instagram posts for an account you own.

Default behavior is to build a *draft* and save it for your review. Publishing
to Instagram happens only when you pass --publish and have valid credentials
for a Business/Creator account you control.

Examples:
    # Draft a photo post about "sunrise" (no posting, just a reviewable draft)
    python3 main.py --keyword sunrise --body "Chasing first light this morning."

    # Draft a video (reel) instead
    python3 main.py --keyword coffee --body "Slow mornings." --media video

    # Draft AND publish (requires IG_USER_ID + IG_ACCESS_TOKEN in your env)
    python3 main.py --keyword sunrise --body "First light." --publish

Secrets are read from the environment / a local .env file, never CLI flags.
"""

from __future__ import annotations

import argparse
import sys

from lib import captions, crosspost, drafts, media
from lib.config import Config, ConfigError
from lib.models import PostRequest


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="instaform",
        description="Draft and optionally publish posts across platforms for accounts you own.",
    )
    p.add_argument("--keyword", required=True, help="Topic used to source media (e.g. 'sunrise').")
    p.add_argument(
        "--body",
        required=True,
        help="Your own caption text. This tool arranges it and adds hashtags; it does not write it for you.",
    )
    p.add_argument(
        "--media",
        choices=("photo", "video"),
        default="photo",
        help="Media type to source from Pexels (default: photo).",
    )
    p.add_argument(
        "--title",
        default=None,
        help="Optional video title (used by YouTube; ignored elsewhere).",
    )
    p.add_argument(
        "--publish",
        action="store_true",
        help="Publish after drafting (requires per-platform credentials). Off by default.",
    )
    p.add_argument(
        "--platforms",
        default="instagram",
        help="Comma-separated targets for --publish: "
        + ",".join(crosspost.ALL_PLATFORMS)
        + " (default: instagram). Platforms without credentials are skipped.",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = Config.load()

    try:
        pexels_key = config.require_pexels()
    except ConfigError as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 2

    # 1. Source media.
    try:
        if args.media == "video":
            asset = media.search_video(args.keyword, pexels_key)
        else:
            asset = media.search_photo(args.keyword, pexels_key)
    except media.MediaError as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 1

    # 2. Compose caption from your words + curated hashtags + attribution.
    caption = captions.compose(
        body=args.body,
        keyword=args.keyword,
        attribution=asset.attribution(),
    )

    # 3. Save a reviewable draft.
    draft = drafts.build_draft(args.keyword, asset, caption)
    path = drafts.save_draft(draft)
    print(f"[+] Draft saved to {path}")
    print(f"    Media:   {asset.kind} by {asset.creator}")
    print(f"    Preview: {asset.preview_url}")
    print("    Caption:")
    for line in caption.render().splitlines():
        print(f"      {line}")

    if not args.publish:
        print("\n[i] Review the draft, then re-run with --publish to post it.")
        return 0

    # 4. Publish (opt-in) — fan out to the selected platforms.
    platforms = tuple(p.strip() for p in args.platforms.split(",") if p.strip())
    post = PostRequest(
        body=caption.render(),
        media_url=asset.url,
        media_kind=asset.kind,
        title=args.title,
    )
    report = crosspost.crosspost(config, post, platforms=platforms)
    print("\n[i] Publish results:")
    print(report.render())
    return 1 if report.any_failed else 0


if __name__ == "__main__":
    raise SystemExit(run())
