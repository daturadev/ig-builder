"""Shared types for cross-platform publishing."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PostRequest:
    """One piece of content to fan out to one or more platforms.

    `media_url` must be a public, hostable URL (the platforms fetch it
    server-side). `media_kind` is "photo", "video", or "none" (text-only).
    """

    body: str
    media_url: str | None = None
    media_kind: str = "none"  # "photo" | "video" | "none"
    title: str | None = None  # used by YouTube; ignored elsewhere

    @property
    def has_video(self) -> bool:
        return self.media_kind == "video" and bool(self.media_url)

    @property
    def has_photo(self) -> bool:
        return self.media_kind == "photo" and bool(self.media_url)


@dataclass(frozen=True)
class PublishResult:
    """Outcome of a single platform publish attempt."""

    platform: str
    ok: bool
    detail: str  # media id / post id on success, or the error message
    skipped: bool = False


@dataclass
class PublishReport:
    """Aggregate of a fan-out across platforms."""

    results: list[PublishResult] = field(default_factory=list)

    def add(self, result: PublishResult) -> None:
        self.results.append(result)

    @property
    def any_failed(self) -> bool:
        return any((not r.ok and not r.skipped) for r in self.results)

    def render(self) -> str:
        lines = []
        for r in self.results:
            mark = "-" if r.skipped else ("+" if r.ok else "!")
            lines.append(f"  [{mark}] {r.platform}: {r.detail}")
        return "\n".join(lines)
