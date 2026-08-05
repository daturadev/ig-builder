import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import youtube  # noqa: E402
from lib.models import PostRequest  # noqa: E402


class FakeResp:
    def __init__(self, status_code=200, payload=None, headers=None, content=b"bytes"):
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = headers or {}
        self.text = str(self._payload)
        self.content = content

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_youtube_skips_when_no_video():
    result = youtube.publish("id", "secret", "refresh", PostRequest(body="x", media_kind="photo", media_url="u"))
    assert result.skipped and not result.ok


def test_youtube_happy_path():
    post = PostRequest(body="my clip", media_kind="video", media_url="https://v/x.mp4", title="Clip")

    def fake_post(url, **kwargs):
        if "oauth2" in url:
            return FakeResp(200, {"access_token": "at"})
        # resumable init
        return FakeResp(200, {}, headers={"Location": "https://upload/session"})

    def fake_get(url, **kwargs):
        return FakeResp(200, content=b"videobytes")

    def fake_put(url, **kwargs):
        return FakeResp(200, {"id": "vid123"})

    with mock.patch("lib.youtube.requests.post", side_effect=fake_post), \
         mock.patch("lib.youtube.requests.get", side_effect=fake_get), \
         mock.patch("lib.youtube.requests.put", side_effect=fake_put):
        result = youtube.publish("id", "secret", "refresh", post)

    assert result.ok and "vid123" in result.detail


def test_youtube_token_failure_surfaces():
    post = PostRequest(body="clip", media_kind="video", media_url="https://v/x.mp4")
    with mock.patch("lib.youtube.requests.post", return_value=FakeResp(400, {"error_description": "bad refresh"})):
        result = youtube.publish("id", "secret", "refresh", post)
    assert not result.ok and "bad refresh" in result.detail
