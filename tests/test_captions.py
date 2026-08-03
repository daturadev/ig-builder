import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import captions  # noqa: E402


def test_load_hashtags_normalizes_and_skips_comments(tmp_path):
    p = tmp_path / "tags.txt"
    p.write_text("# a comment\nphotography\n#alreadyhashed\n\n  spaced  \n")
    tags = captions.load_hashtags(str(p))
    assert tags == ["#photography", "#alreadyhashed", "#spaced"]


def test_load_hashtags_missing_file_returns_empty():
    assert captions.load_hashtags("/does/not/exist.txt") == []


def test_pick_hashtags_is_capped_and_distinct():
    tags = [f"#t{i}" for i in range(50)]
    picked = captions.pick_hashtags(tags, count=100, rng=random.Random(1))
    assert len(picked) == captions.MAX_HASHTAGS
    assert len(set(picked)) == len(picked)


def test_pick_hashtags_handles_fewer_than_requested():
    tags = ["#a", "#b"]
    picked = captions.pick_hashtags(tags, count=10, rng=random.Random(0))
    assert sorted(picked) == ["#a", "#b"]


def test_compose_includes_body_attribution_and_hashtags(tmp_path):
    p = tmp_path / "tags.txt"
    p.write_text("photography\ntravel\n")
    cap = captions.compose(
        body="My own words.",
        keyword="sunrise",
        attribution="Photo by Jane on Pexels",
        hashtags_path=str(p),
        rng=random.Random(3),
    )
    rendered = cap.render()
    assert "My own words." in rendered
    assert "Photo by Jane on Pexels" in rendered
    assert "#photography" in rendered or "#travel" in rendered
