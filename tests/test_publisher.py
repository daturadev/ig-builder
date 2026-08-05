import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from lib import publisher  # noqa: E402


class FakeResp:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = str(self._payload)

    def json(self):
        return self._payload


def test_create_container_returns_id():
    with mock.patch("lib.publisher.requests.post", return_value=FakeResp(200, {"id": "123"})):
        cid = publisher.create_container("u", "t", "https://img", "cap", kind="photo")
    assert cid == "123"


def test_create_container_surfaces_graph_error():
    err = {"error": {"message": "Invalid image URL"}}
    with mock.patch("lib.publisher.requests.post", return_value=FakeResp(400, err)):
        with pytest.raises(publisher.PublishError) as e:
            publisher.create_container("u", "t", "https://img", "cap")
    assert "Invalid image URL" in str(e.value)


def test_publish_container_returns_media_id():
    with mock.patch("lib.publisher.requests.post", return_value=FakeResp(200, {"id": "media-9"})):
        mid = publisher.publish_container("u", "t", "123")
    assert mid == "media-9"


def test_video_uses_reels_media_type():
    captured = {}

    def fake_post(url, data=None, timeout=None):
        captured.update(data)
        return FakeResp(200, {"id": "1"})

    with mock.patch("lib.publisher.requests.post", side_effect=fake_post):
        publisher.create_container("u", "t", "https://v.mp4", "cap", kind="video")
    assert captured.get("media_type") == "REELS"
    assert captured.get("video_url") == "https://v.mp4"
