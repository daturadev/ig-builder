"""Publish to Threads via the official Threads API.

Threads publishing mirrors Instagram's two-step flow: create a media
container, then publish it. Text-only posts are supported (no media needed).
Docs: https://developers.facebook.com/docs/threads/posts
"""

from __future__ import annotations

import requests

from .models import PostRequest, PublishResult

THREADS_BASE = "https://graph.threads.net/v1.0"
DEFAULT_TIMEOUT = 60


class ThreadsError(RuntimeError):
    """Raised when the Threads API rejects a step."""


def _check(resp: requests.Response, step: str) -> dict:
    try:
        payload = resp.json()
    except ValueError:
        payload = {}
    if resp.status_code >= 400 or "error" in payload:
        msg = payload.get("error", {}).get("message", resp.text)
        raise ThreadsError(f"{step} failed ({resp.status_code}): {msg}")
    return payload


def _create_container(user_id: str, token: str, post: PostRequest) -> str:
    params: dict[str, str] = {"text": post.body, "access_token": token}
    if post.has_video:
        params["media_type"] = "VIDEO"
        params["video_url"] = post.media_url  # type: ignore[assignment]
    elif post.has_photo:
        params["media_type"] = "IMAGE"
        params["image_url"] = post.media_url  # type: ignore[assignment]
    else:
        params["media_type"] = "TEXT"

    resp = requests.post(
        f"{THREADS_BASE}/{user_id}/threads", data=params, timeout=DEFAULT_TIMEOUT
    )
    payload = _check(resp, "Threads container creation")
    container_id = payload.get("id")
    if not container_id:
        raise ThreadsError(f"Container creation returned no id: {payload}")
    return container_id


def _publish_container(user_id: str, token: str, container_id: str) -> str:
    resp = requests.post(
        f"{THREADS_BASE}/{user_id}/threads_publish",
        data={"creation_id": container_id, "access_token": token},
        timeout=DEFAULT_TIMEOUT,
    )
    payload = _check(resp, "Threads publish")
    media_id = payload.get("id")
    if not media_id:
        raise ThreadsError(f"Publish returned no id: {payload}")
    return media_id


def publish(user_id: str, token: str, post: PostRequest) -> PublishResult:
    """Publish a post to Threads. Returns a PublishResult (never raises)."""
    try:
        container_id = _create_container(user_id, token, post)
        media_id = _publish_container(user_id, token, container_id)
        return PublishResult("threads", ok=True, detail=media_id)
    except (ThreadsError, requests.RequestException) as exc:
        return PublishResult("threads", ok=False, detail=str(exc))
