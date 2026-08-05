"""Publish videos to TikTok via the Content Posting API.

Two modes, because TikTok gates public posting behind an app audit:

* Inbox draft (default): sends the video to your TikTok inbox as a draft;
  you open the app and tap "Post". Works before your app is audited.
* Direct post (opt-in via TIKTOK_DIRECT_POST=1): publishes straight to your
  profile. TikTok only allows this once your app passes their audit; before
  that, direct posts are forced to private ("SELF_ONLY").

Also note: PULL_FROM_URL requires the source URL's domain to be verified in
your TikTok developer portal (or the call is rejected). If your media is on an
unverified host, use owned/verified hosting. Docs:
https://developers.tiktok.com/doc/content-posting-api-reference-upload-video
"""

from __future__ import annotations

import json

import requests

from .models import PostRequest, PublishResult

INBOX_INIT = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
DIRECT_INIT = "https://open.tiktokapis.com/v2/post/publish/video/init/"
DEFAULT_TIMEOUT = 120


class TikTokError(RuntimeError):
    """Raised when the TikTok API rejects a step."""


def _post(url: str, token: str, body: dict) -> dict:
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        data=json.dumps(body),
        timeout=DEFAULT_TIMEOUT,
    )
    payload = resp.json() if resp.content else {}
    err = (payload.get("error") or {})
    # TikTok returns error.code == "ok" on success.
    if resp.status_code >= 400 or (err.get("code") not in (None, "ok")):
        raise TikTokError(
            f"TikTok init failed ({resp.status_code}): "
            f"{err.get('message') or resp.text}"
        )
    return payload


def publish(token: str, post: PostRequest, direct_post: bool = False) -> PublishResult:
    """Send a video to TikTok. Returns a PublishResult (never raises)."""
    if not post.has_video:
        return PublishResult(
            "tiktok", ok=False, detail="TikTok needs a video; none provided.", skipped=True
        )
    try:
        source_info = {"source": "PULL_FROM_URL", "video_url": post.media_url}
        if direct_post:
            body = {
                "post_info": {
                    "title": post.body[:150],
                    # Audited apps can set PUBLIC_TO_EVERYONE; unaudited apps
                    # are forced to SELF_ONLY by TikTok regardless.
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_comment": False,
                },
                "source_info": source_info,
            }
            payload = _post(DIRECT_INIT, token, body)
            mode = "direct post"
        else:
            payload = _post(INBOX_INIT, token, {"source_info": source_info})
            mode = "sent to inbox (open TikTok and tap Post)"

        publish_id = (payload.get("data") or {}).get("publish_id", "unknown")
        return PublishResult("tiktok", ok=True, detail=f"{mode} — id {publish_id}")
    except (TikTokError, requests.RequestException) as exc:
        return PublishResult("tiktok", ok=False, detail=str(exc))
