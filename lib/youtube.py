"""Upload videos to YouTube via the Data API v3 (resumable upload).

Uses an OAuth2 refresh token to mint short-lived access tokens, then performs
a resumable upload of the video bytes. YouTube's API uploads raw bytes (not a
URL), so the source video is streamed down first.

Note: uploads from a newly created API project may be forced to `private`
until the associated channel is verified — that's a YouTube abuse-prevention
limit, not a bug here. Docs:
https://developers.google.com/youtube/v3/guides/uploading_a_video
"""

from __future__ import annotations

import json

import requests

from .models import PostRequest, PublishResult

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
DEFAULT_TIMEOUT = 300


class YouTubeError(RuntimeError):
    """Raised when a YouTube API step fails."""


def _access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=60,
    )
    payload = resp.json() if resp.content else {}
    token = payload.get("access_token")
    if not token:
        raise YouTubeError(
            f"Token refresh failed ({resp.status_code}): "
            f"{payload.get('error_description', resp.text)}"
        )
    return token


def _download(media_url: str) -> bytes:
    resp = requests.get(media_url, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    return resp.content


def _upload(
    access_token: str,
    video_bytes: bytes,
    title: str,
    description: str,
    privacy: str,
) -> str:
    metadata = {
        "snippet": {"title": title, "description": description},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }
    # Step 1: start a resumable session.
    init = requests.post(
        UPLOAD_URL,
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/*",
        },
        data=json.dumps(metadata),
        timeout=60,
    )
    if init.status_code >= 400:
        raise YouTubeError(f"Upload init failed ({init.status_code}): {init.text}")
    session_url = init.headers.get("Location")
    if not session_url:
        raise YouTubeError("Upload init returned no resumable session URL.")

    # Step 2: upload the bytes.
    put = requests.put(
        session_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "video/*",
        },
        data=video_bytes,
        timeout=DEFAULT_TIMEOUT,
    )
    payload = put.json() if put.content else {}
    if put.status_code >= 400 or "id" not in payload:
        raise YouTubeError(
            f"Upload failed ({put.status_code}): {payload.get('error', put.text)}"
        )
    return payload["id"]


def publish(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    post: PostRequest,
    privacy: str = "public",
) -> PublishResult:
    """Upload a video to YouTube. Returns a PublishResult (never raises)."""
    if not post.has_video:
        return PublishResult(
            "youtube", ok=False, detail="YouTube needs a video; none provided.", skipped=True
        )
    try:
        token = _access_token(client_id, client_secret, refresh_token)
        video_bytes = _download(post.media_url)  # type: ignore[arg-type]
        video_id = _upload(
            token,
            video_bytes,
            title=post.title or (post.body[:95] or "New upload"),
            description=post.body,
            privacy=privacy,
        )
        return PublishResult(
            "youtube", ok=True, detail=f"https://youtu.be/{video_id}"
        )
    except (YouTubeError, requests.RequestException) as exc:
        return PublishResult("youtube", ok=False, detail=str(exc))
