# Credential setup — automated posting to accounts you own

Automated posting requires you to authorize a developer app on each platform,
one time. Nobody can generate these tokens for you — they're tied to your
logins. Once a platform's values are in `.env`, `--publish --platforms <name>`
posts to it. Set up whichever platforms you want; the rest are skipped.

Your handle is **@_dedrop / @dedrop** — make sure you're logged into that
account (and its linked Page, for Meta) when creating each app.

---

## 1. Instagram + Threads (both live in one Meta app)

Instagram publishing needs a **Business or Creator** account linked to a
**Facebook Page**. Threads uses the same Meta developer app with a separate
token.

**A. Convert the account (if needed)**
1. In the Instagram app: Settings → *Account type and tools* → switch to
   **Business** or **Creator**.
2. Link it to a Facebook Page you control (Meta will prompt you).

**B. Create the Meta app**
1. Go to <https://developers.facebook.com/apps> → *Create App* → type
   **Business**.
2. Add the **Instagram Graph API** product (and the **Threads API** use case).

**C. Get the Instagram values**
1. Use the Graph API Explorer (<https://developers.facebook.com/tools/explorer/>)
   with permissions: `instagram_basic`, `instagram_content_publish`,
   `pages_show_list`, `pages_read_engagement`.
2. `IG_USER_ID`: query `me/accounts` → your Page → `instagram_business_account`.
3. `IG_ACCESS_TOKEN`: generate a token, then exchange it for a **long-lived**
   token (60 days) via the `oauth/access_token` endpoint. Refresh before it
   expires.

**D. Get the Threads values**
1. In the Threads API use case, add scopes `threads_basic` and
   `threads_content_publish`.
2. `THREADS_USER_ID`: call `GET https://graph.threads.net/v1.0/me?fields=id`.
3. `THREADS_ACCESS_TOKEN`: the long-lived Threads token from the OAuth flow.

Docs: [Instagram publishing](https://developers.facebook.com/docs/instagram-api/guides/content-publishing) ·
[Threads posts](https://developers.facebook.com/docs/threads/posts)

---

## 2. YouTube (Data API v3)

1. <https://console.cloud.google.com> → create a project.
2. *APIs & Services* → **Enable** the **YouTube Data API v3**.
3. *OAuth consent screen* → set it up (External is fine; add yourself as a
   test user so you don't need Google verification for personal use).
4. *Credentials* → *Create credentials* → **OAuth client ID** → type
   **Desktop app**. Save the `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET`.
5. Get a **refresh token** for scope
   `https://www.googleapis.com/auth/youtube.upload`. Easiest path: the
   [OAuth 2.0 Playground](https://developers.google.com/oauthplayground) —
   gear icon → *Use your own OAuth credentials* → paste client id/secret →
   authorize the YouTube upload scope → exchange for tokens → copy the
   **refresh token** into `YOUTUBE_REFRESH_TOKEN`.

**Heads-up:** default upload quota is 10,000 units/day and each upload costs
~1,600, so ~6 uploads/day out of the box. New projects may have uploads forced
to *private* until the channel is verified — that's YouTube's rule, not this
tool. Request a quota increase / verify the channel when you're ready to scale.

---

## 3. TikTok (Content Posting API)

TikTok gates public auto-posting behind an app audit. You can start
immediately in **inbox mode** (the video lands in your TikTok inbox as a
draft; you tap *Post*), then switch to direct posting once audited.

1. <https://developers.tiktok.com> → register → *Manage apps* → create an app.
2. Add the **Content Posting API** product.
3. Add scopes: `video.upload` (inbox mode) and, once audited, `video.publish`
   (direct post).
4. Complete **URL ownership verification** for the domain your media is served
   from — `PULL_FROM_URL` rejects unverified domains. If you can't verify the
   media host, serve videos from your own verified domain/bucket.
5. Get a user `TIKTOK_ACCESS_TOKEN` via TikTok Login Kit (OAuth) for the
   @_dedrop account.
6. Leave `TIKTOK_DIRECT_POST` empty until your app passes audit. Set it to `1`
   only after — before audit, direct posts are forced private anyway.

Docs: [Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started)

---

## Once configured

```bash
# Draft only (always safe — nothing posts):
python3 main.py --keyword surf --body "Dawn patrol." --media video

# Fan out to everything you've set up:
python3 main.py --keyword surf --body "Dawn patrol." --media video \
    --publish --platforms instagram,threads,youtube,tiktok
```

Platforms missing credentials are skipped with a note, never a hard failure —
so you can wire them up one at a time and re-run.
