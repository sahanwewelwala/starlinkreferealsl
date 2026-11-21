# Starlink Referral Sri Lanka – static website

A small, fast, SEO- and AI-search-optimised site in **English, Sinhala and Tamil**
that sends visitors to your Starlink referral link (Rs. 15,000 for both of you).

The ready-to-upload website is the **`docs/`** folder (GitHub Pages serves it directly).

## Change the link, reward or domain

Edit `config.json`:

| Key | What it is |
|---|---|
| `site_url` | Your real domain, e.g. `https://example.lk` (needed for Google, sitemap, share previews) |
| `referral_url` | Your Starlink referral link |
| `reward` | The reward text per language (update if Starlink changes the offer) |

Texts are in `content/en.json`, `content/si.json`, `content/ta.json`.

Then rebuild:

```bash
python3 build.py
```

If you changed the reward, also refresh the share images (needs Node + Playwright):

```bash
node tools/make_images.mjs && python3 build.py
```

## Put it online (free)

Any static host works. Easiest options:

- **Netlify Drop** – drag the `docs` folder onto app.netlify.com/drop.
- **Cloudflare Pages** – create a project, upload `docs`.
- **GitHub Pages** (used now) – Settings → Pages → Deploy from branch → `main` / `/docs`.
  Live at https://sahanwewelwala.github.io/starlinkreferealsl/

To use your own domain later: add it in the host's settings, set `site_url`, rebuild and push.

## Get found by Google and AI assistants

1. **Google Search Console** – add your domain, submit `https://YOUR-DOMAIN/sitemap.xml`.
2. **Bing Webmaster Tools** – add the site and submit the same sitemap. Bing's index
   feeds ChatGPT search, Microsoft Copilot and DuckDuckGo.
3. Share the page (not the raw link) on your own social profiles – real visits and
   links help ranking.

## What's built in

- One page per language (`/`, `/si/`, `/ta/`) with `hreflang` alternates and `x-default`.
- Titles/descriptions targeting "Starlink referral link/code Sri Lanka" in all three languages.
- Structured data: WebSite, WebPage (Sri Lanka coverage, referral link), FAQPage, HowTo.
- `llms.txt` – a plain-text summary with the link and key facts for AI assistants.
- `robots.txt` that explicitly welcomes AI search crawlers (GPTBot, OAI-SearchBot, ClaudeBot,
  PerplexityBot, Google-Extended, Bingbot and others).
- A "Quick answer" block and FAQ answers containing the link as visible text, so search engines
  and AI tools can quote it directly.
- Open Graph / Twitter share images per language, favicon and app icons.
- Referral links marked `rel="sponsored"` (Google's rule for referral/affiliate links) and a
  clear referral disclosure + "not affiliated with Starlink" notice.
- No frameworks, no tracking, CSS inlined: ~50–65 KB per page, loads fast on mobile data.
- Language hint banner for visitors whose phone is set to Sinhala or Tamil (no forced redirects).
- Sticky "Order" button on phones.

## Good to know

- Starlink's referral terms forbid spamming referral links – don't paste the link in
  comment sections or groups you don't own. Starlink can change the reward at any time;
  keep `reward` in `config.json` up to date.
- Don't use Starlink's logo, and avoid "starlink" in your domain name (trademark).
