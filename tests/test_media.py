import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from lib import media  # noqa: E402


class FakeResp:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = str(self._payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_search_photo_builds_asset_with_attribution():
    payload = {
        "photos": [
            {
                "src": {"large2x": "https://img/large.jpg", "medium": "https://img/med.jpg"},
                "photographer": "Jane Doe",
                "url": "https://pexels.com/photo/1",
            }
        ]
    }
    with mock.patch("lib.media.requests.get", return_value=FakeResp(200, payload)):
        asset = media.search_photo("sunrise", "key")
    assert asset.kind == "photo"
    assert asset.url == "https://img/large.jpg"
    assert "Jane Doe" in asset.attribution()


def test_search_photo_no_results_raises():
    with mock.patch("lib.media.requests.get", return_value=FakeResp(200, {"photos": []})):
        with pytest.raises(media.MediaError):
            media.search_photo("nothing", "key")


def test_bad_key_raises_media_error():
    with mock.patch("lib.media.requests.get", return_value=FakeResp(401, {})):
        with pytest.raises(media.MediaError):
            media.search_photo("x", "bad")


def test_search_video_picks_highest_resolution():
    payload = {
        "videos": [
            {
                "image": "https://img/thumb.jpg",
                "user": {"name": "Sam"},
                "url": "https://pexels.com/video/1",
                "video_files": [
                    {"width": 640, "link": "https://v/small.mp4"},
                    {"width": 1920, "link": "https://v/big.mp4"},
                ],
            }
        ]
    }
    with mock.patch("lib.media.requests.get", return_value=FakeResp(200, payload)):
        asset = media.search_video("coffee", "key")
    assert asset.url == "https://v/big.mp4"
    assert asset.kind == "video"
