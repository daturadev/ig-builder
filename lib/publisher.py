"""Publish to Instagram through the official Graph Content Publishing API.

This is opt-in and requires credentials for a Business/Creator account *you
own*. Publishing is a two-step flow: create a media container from a public
asset URL, then publish that container. See:
https://developers.facebook.com/docs/instagram-api/guides/content-publishing
"""

from __future__ import annotations

import requests

from .models import PostRequest, PublishResult

DEFAULT_TIMEOUT = 60


class PublishError(RuntimeError):
    """Raised when the Graph API rejects a publish step."""


def _graph_base(version: str) -> str:
    return f"https://graph.facebook.com/{version}"


def _check(resp: requests.Response, step: str) -> dict:
    try:
        payload = resp.json()
    except ValueError:
        payload = {}
    if resp.status_code >= 400 or "error" in payload:
        err = payload.get("error", {})
        msg = err.get("message", resp.text)
        raise PublishError(f"{step} failed ({resp.status_code}): {msg}")
    return payload


def create_container(
    ig_user_id: str,
    access_token: str,
    media_url: str,
    caption: str,
    kind: str = "photo",
    version: str = "v20.0",
) -> str:
    """Create a media container and return its id."""
    params = {"caption": caption, "access_token": access_token}
    if kind == "video":
        params["media_type"] = "REELS"
        params["video_url"] = media_url
    else:
        params["image_url"] = media_url

    resp = requests.post(
        f"{_graph_base(version)}/{ig_user_id}/media",
        data=params,
        timeout=DEFAULT_TIMEOUT,
    )
    payload = _check(resp, "Container creation")
    container_id = payload.get("id")
    if not container_id:
        raise PublishError(f"Container creation returned no id: {payload}")
    return container_id


def publish_container(
    ig_user_id: str,
    access_token: str,
    container_id: str,
    version: str = "v20.0",
) -> str:
    """Publish a previously created container and return the media id."""
    resp = requests.post(
        f"{_graph_base(version)}/{ig_user_id}/media_publish",
        data={"creation_id": container_id, "access_token": access_token},
        timeout=DEFAULT_TIMEOUT,
    )
    payload = _check(resp, "Publish")
    media_id = payload.get("id")
    if not media_id:
        raise PublishError(f"Publish returned no media id: {payload}")
    return media_id


def publish(
    ig_user_id: str,
    access_token: str,
    post: PostRequest,
    version: str = "v20.0",
) -> PublishResult:
    """Publish a post to Instagram. Returns a PublishResult (never raises).

    Instagram requires media — a text-only post is skipped.
    """
    if not (post.has_photo or post.has_video):
        return PublishResult(
            "instagram", ok=False, detail="Instagram needs media; none provided.", skipped=True
        )
    kind = "video" if post.has_video else "photo"
    try:
        container_id = create_container(
            ig_user_id, access_token, post.media_url, post.body, kind=kind, version=version
        )
        media_id = publish_container(ig_user_id, access_token, container_id, version=version)
        return PublishResult("instagram", ok=True, detail=media_id)
    except (PublishError, requests.RequestException) as exc:
        return PublishResult("instagram", ok=False, detail=str(exc))
