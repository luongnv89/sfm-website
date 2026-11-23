<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="site/assets/logo/logo-white.svg">
    <img src="site/assets/logo/logo-full.svg" alt="sfm" width="220">
  </picture>
</p>

# sfm website

The source of [sfm.luongnv.com](https://sfm.luongnv.com), the landing page of sfm (SSH Fleet Monitor): every Mac and Linux machine you own, on one screen.

This repository holds the website only. sfm itself is proprietary software and its source is not public.

## What is here

| Path | What it holds |
|---|---|
| `site/` | The published site: `index.html`, `docs.html`, `changelog.html`, `privacy.html`, `404.html` and their assets. Plain HTML and CSS, no JavaScript and no build step |
| `site/assets/shots/` | Dashboard screenshots. They show an invented demo fleet |
| `site/assets/fonts/` | JetBrains Mono (SIL Open Font License 1.1, see `OFL.txt` there) |
| `scripts/check-site.py` | Checks that every local link resolves and that no page loads anything from another site |
| `.github/workflows/deploy.yml` | Publishes `site/` to GitHub Pages on every push to `main` |

## Work on it

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
python3 scripts/check-site.py site
```

Open `http://127.0.0.1:8000/`. Edit the HTML and CSS in `site/` directly. A push to `main` runs the check and deploys.

Every page sets a Content-Security-Policy that allows only its own files, so there is no inline style, no script and nothing from a CDN. The check fails the deploy if a page breaks that rule, because the privacy policy states it.

## Contact

Early access requests and questions: sfm@luongnv.com
