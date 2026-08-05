# InstaForm

**A content-drafting toolkit for creators who run their own social accounts.**

InstaForm helps you post consistently without cutting corners. It sources
royalty-free media, arranges *your* caption with a curated hashtag set, and
saves a reviewable draft. When you're happy with it, you can fan the post out
through the platforms' **official APIs** — for accounts **you own and operate**.

### What it does

- 🖼️ **Sources media** from [Pexels](https://www.pexels.com/api/) (royalty-free, with creator attribution baked in).
- ✍️ **Composes captions** from your own words plus hashtags you curate.
- 📝 **Saves drafts** to `drafts/` so a human reviews every post before it goes out.
- 🚀 **Publishes (opt-in)** across **Instagram, Threads, YouTube, and TikTok** via each platform's official API.

### Supported platforms

| Platform | API | Notes |
| --- | --- | --- |
| Instagram | Graph Content Publishing | Business/Creator account + Facebook Page |
| Threads | Threads API | Same Meta app as Instagram |
| YouTube | Data API v3 | Video uploads; ~6/day on default quota |
| TikTok | Content Posting API | Inbox-draft mode until your app is audited |

Setting these up is a one-time job per platform — see
[`docs/SETUP_APIS.md`](docs/SETUP_APIS.md). Platforms you haven't configured are
simply skipped, so you can add them one at a time.

### What it does *not* do

InstaForm is built to be sustainable, which means staying inside Instagram's
Terms. It does **not** mass-create or sell accounts, does **not** trade in
account credentials, does **not** fake engagement, and does **not** try to
evade platform detection. One real account, real content, real audience.

## Installation

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env   # then fill in your keys
```

## Usage

Draft a post (nothing is published — you get a file to review):

```bash
python3 main.py --keyword sunrise --body "Chasing first light this morning."
```

Draft a reel instead of a photo:

```bash
python3 main.py --keyword coffee --body "Slow mornings." --media video
```

Draft **and** publish to one or more platforms (requires credentials, see below):

```bash
# Publish to Instagram only (the default target)
python3 main.py --keyword sunrise --body "First light." --publish

# Fan a video out to every platform you've configured
python3 main.py --keyword surf --body "Dawn patrol." --media video \
    --publish --platforms instagram,threads,youtube,tiktok
```

Platforms without credentials are skipped with a note (not a failure), so you
can wire them up one at a time. Secrets are read from your environment /
`.env` — never passed as CLI flags, so they don't leak into shell history or
process lists.

## Configuration

Set up whichever platforms you want — full walkthrough in
[`docs/SETUP_APIS.md`](docs/SETUP_APIS.md).

| Variable | Required for | How to get it |
| --- | --- | --- |
| `PEXELS_API_KEY` | drafting | Free at <https://www.pexels.com/api/> |
| `IG_USER_ID`, `IG_ACCESS_TOKEN` | Instagram | Business/Creator account + Page |
| `THREADS_USER_ID`, `THREADS_ACCESS_TOKEN` | Threads | Same Meta app as Instagram |
| `YOUTUBE_CLIENT_ID/SECRET/REFRESH_TOKEN` | YouTube | Google Cloud OAuth client |
| `TIKTOK_ACCESS_TOKEN` | TikTok | TikTok developer app |
| `GRAPH_API_VERSION` | optional | Defaults to `v20.0` |

Curate your own hashtag lists in `lib/hashtags.txt`.

## Curate your hashtags

Edit `lib/hashtags.txt` — one tag per line, `#` optional, `# ` for comments.
Generic tags rarely help reach; tags specific to your niche do.

## Development

```bash
python3 -m pytest -q
```

## Making it pay

Growing a genuine audience is the asset; see [`MONETIZATION.md`](MONETIZATION.md)
for legitimate ways to turn it into income.

## License

See [LICENSE](LICENSE).
