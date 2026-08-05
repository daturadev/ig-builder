"""Fan a single post out to multiple platforms.

Each platform is only attempted if its credentials are present, so you can set
up one platform at a time. Per-platform failures are captured in the report —
one platform failing never stops the others.
"""

from __future__ import annotations

from . import publisher, threads, tiktok, youtube
from .config import Config, ConfigError
from .models import PostRequest, PublishReport, PublishResult

ALL_PLATFORMS = ("instagram", "threads", "youtube", "tiktok")


def _skip(platform: str, reason: str) -> PublishResult:
    return PublishResult(platform, ok=False, detail=reason, skipped=True)


def post_to_instagram(config: Config, post: PostRequest) -> PublishResult:
    try:
        user_id, token = config.require_instagram()
    except ConfigError as exc:
        return _skip("instagram", str(exc))
    return publisher.publish(user_id, token, post, version=config.graph_api_version)


def post_to_threads(config: Config, post: PostRequest) -> PublishResult:
    try:
        user_id, token = config.require_threads()
    except ConfigError as exc:
        return _skip("threads", str(exc))
    return threads.publish(user_id, token, post)


def post_to_youtube(config: Config, post: PostRequest) -> PublishResult:
    try:
        client_id, client_secret, refresh_token = config.require_youtube()
    except ConfigError as exc:
        return _skip("youtube", str(exc))
    return youtube.publish(client_id, client_secret, refresh_token, post)


def post_to_tiktok(config: Config, post: PostRequest) -> PublishResult:
    try:
        token = config.require_tiktok()
    except ConfigError as exc:
        return _skip("tiktok", str(exc))
    return tiktok.publish(token, post, direct_post=config.tiktok_direct_post)


_DISPATCH = {
    "instagram": post_to_instagram,
    "threads": post_to_threads,
    "youtube": post_to_youtube,
    "tiktok": post_to_tiktok,
}


def crosspost(
    config: Config, post: PostRequest, platforms: tuple[str, ...] = ALL_PLATFORMS
) -> PublishReport:
    report = PublishReport()
    for name in platforms:
        handler = _DISPATCH.get(name)
        if handler is None:
            report.add(_skip(name, f"Unknown platform {name!r}."))
            continue
        report.add(handler(config, post))
    return report
