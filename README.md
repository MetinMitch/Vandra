# vandrastudios.com

Static site for Vandra™ (PFS Enterprise LLC), hosted on GitHub Pages at vandrastudios.com.

- `*.html`, `style.css`, `main.js`, `images/`, `fonts/` — the published site (served from the repo root).
- `build.py` — generator. All copy and layout data live here; edit, then `python3 build.py` regenerates every page. Do not hand-edit the HTML.
- `scrape/computed/` — measured geometry of the original Squarespace site (desktop 1920 / mobile 375) that build.py reproduces.
- `verify.py` — Playwright check of the built pages against those measurements.
- Forms (contact, registration, community, newsletter) post to Formspree endpoint `xkjjrqvg` → info@vandrastudios.com.
- "Buy now" links go to Amazon (ASINs in build.py).
- `CNAME` binds the custom domain; keep it.
