import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import crosspost, threads, tiktok  # noqa: E402
from lib.config import Config  # noqa: E402
from lib.models import PostRequest  # noqa: E402


class FakeResp:
    def __init__(self, status_code=200, payload=None, headers=None, content=b"x"):
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = headers or {}
        self.text = str(self._payload)
        self.content = content

    def json(self):
        return self._payload


def _cfg(**over):
    base = dict(
        pexels_api_key="k",
        ig_user_id=None,
        ig_access_token=None,
        threads_user_id=None,
        threads_access_token=None,
        youtube_client_id=None,
        youtube_client_secret=None,
        youtube_refresh_token=None,
        tiktok_access_token=None,
    )
    base.update(over)
    return Config(**base)


def test_threads_text_post_flow():
    post = PostRequest(body="hello world", media_kind="none")
    responses = [FakeResp(200, {"id": "container-1"}), FakeResp(200, {"id": "thread-9"})]
    with mock.patch("lib.threads.requests.post", side_effect=responses):
        result = threads.publish("u", "t", post)
    assert result.ok and result.detail == "thread-9"


def test_threads_surfaces_error():
    post = PostRequest(body="hi", media_kind="none")
    with mock.patch("lib.threads.requests.post", return_value=FakeResp(400, {"error": {"message": "bad"}})):
        result = threads.publish("u", "t", post)
    assert not result.ok and "bad" in result.detail


def test_tiktok_photo_is_skipped():
    result = tiktok.publish("t", PostRequest(body="x", media_kind="photo", media_url="u"))
    assert result.skipped and not result.ok


def test_tiktok_inbox_default_flow():
    post = PostRequest(body="clip", media_kind="video", media_url="https://v/x.mp4")
    with mock.patch("lib.tiktok.requests.post", return_value=FakeResp(200, {"data": {"publish_id": "p1"}, "error": {"code": "ok"}})):
        result = tiktok.publish("t", post, direct_post=False)
    assert result.ok and "inbox" in result.detail and "p1" in result.detail


def test_crosspost_skips_platforms_without_credentials():
    post = PostRequest(body="hey", media_kind="none")
    report = crosspost.crosspost(_cfg(), post, platforms=("threads", "tiktok"))
    # No creds -> both skipped, nothing "failed".
    assert not report.any_failed
    assert all(r.skipped for r in report.results)
    assert {r.platform for r in report.results} == {"threads", "tiktok"}


def test_crosspost_runs_configured_platform():
    post = PostRequest(body="hey", media_kind="none")
    cfg = _cfg(threads_user_id="u", threads_access_token="t")
    responses = [FakeResp(200, {"id": "c"}), FakeResp(200, {"id": "posted"})]
    with mock.patch("lib.threads.requests.post", side_effect=responses):
        report = crosspost.crosspost(cfg, post, platforms=("threads",))
    assert not report.any_failed
    assert report.results[0].ok and report.results[0].detail == "posted"
