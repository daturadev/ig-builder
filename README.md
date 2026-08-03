# InstaForm

**A content-drafting toolkit for creators who run their own Instagram account.**

InstaForm helps you post consistently without cutting corners. It sources
royalty-free media, arranges *your* caption with a curated hashtag set, and
saves a reviewable draft. When you're happy with it, you can publish through
Instagram's official Graph API — for an account **you own and operate**.

### What it does

- 🖼️ **Sources media** from [Pexels](https://www.pexels.com/api/) (royalty-free, with creator attribution baked in).
- ✍️ **Composes captions** from your own words plus hashtags you curate.
- 📝 **Saves drafts** to `drafts/` so a human reviews every post before it goes out.
- 🚀 **Publishes (opt-in)** via the official Instagram Graph Content Publishing API.

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

Draft **and** publish (requires publishing credentials, see below):

```bash
python3 main.py --keyword sunrise --body "First light." --publish
```

Secrets are read from your environment / `.env` — never passed as CLI flags,
so they don't leak into shell history or process lists.

## Configuration

| Variable | Required for | How to get it |
| --- | --- | --- |
| `PEXELS_API_KEY` | drafting | Free at <https://www.pexels.com/api/> |
| `IG_USER_ID` | publishing | Your Instagram Business/Creator account ID |
| `IG_ACCESS_TOKEN` | publishing | Long-lived Graph API token for a Page you own |
| `GRAPH_API_VERSION` | optional | Defaults to `v20.0` |

### Publishing setup

Publishing uses Meta's official [Content Publishing API](https://developers.facebook.com/docs/instagram-api/guides/content-publishing).
You need an Instagram **Business or Creator** account connected to a Facebook
Page, and a long-lived access token with the right permissions. Curate your
own tag lists in `lib/hashtags.txt`.

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
