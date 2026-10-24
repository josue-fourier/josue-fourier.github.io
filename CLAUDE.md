# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Layout

Django 6 portfolio site (single app `portfolio`, project package `djangoPortfolio/djangoPortfolio`). Everything Django lives in `djangoPortfolio/` (where `manage.py` is); repo root holds Docker/nginx/Tailwind tooling. `.agents/` is gitignored scratch from prior agent runs — ignore it.

## Commands

Run Django commands from `djangoPortfolio/` (a `venv/` exists at repo root).

```bash
python manage.py runserver
python manage.py test                                   # all tests
python manage.py test portfolio.test_telemetry          # one module
python manage.py test portfolio.tests.SomeClass.test_x  # one test
python manage.py run_task [hackerrank|ntfy|all]         # run background tasks on demand
python manage.py run_huey                               # Huey worker (separate process in prod)
```

CSS: Tailwind v4 + daisyUI. Source is `app.css` at repo root; compiled output `djangoPortfolio/static/portfolio/main.css` is committed. Rebuild with `npm run dev` (watch mode). Hand-written styles/JS live in `static/portfolio/css/` and `static/portfolio/js/` (e.g. `hero-network.js` is the hero animation).

Social card: `python scripts/generate_og_card.py` (needs Chrome/Chromium; see its docstring), then `collectstatic`.

Deploy: `docker compose up -d --build` — services `db` (Postgres 15), `web` (gunicorn), `huey` (worker, same image), `nginx`, `cloudflared`. `nginx/default.conf` serves static/media and a custom bilingual error page (via SSI) for 5xx/404 even when Django is down. Config comes from `.env` (see `.env.example`) via `python-decouple`.

## Architecture notes

- **Database is Postgres only** (no SQLite fallback for the app). `settings._resolve_db_host()` probes `127.0.0.1:5432` and, if closed, tries `docker inspect` on the compose db container to find its IP — so local dev works against the compose DB without exposing the port.
- **i18n**: `django-modeltranslation` (see `portfolio/translation.py`) adds per-language columns to models; `LocaleMiddleware` + `i18n_patterns` in `urls.py` give `/<lang>/` routes for the root and project pages, while `api/`, `health`, `sitemap.xml`, `robots.txt`, `_track/` are unprefixed. Message catalogs are in `djangoPortfolio/locale`. Many routes are duplicated with/without trailing slash intentionally.
- **Background work** is Huey (`SqliteHuey`, file from `HUEY_FILENAME`). `portfolio/tasks.py` defines `db_periodic_task`s: HackerRank badge scrape (daily 08:00) and an ntfy status poller (every minute). In dev, Huey runs `immediate` unless `HUEY_IMMEDIATE=False`; the `run_huey` consumer forces it off. `run_task` management command is the manual entry point.
- **Telemetry**: edge nodes (Raspberry Pis) POST to `/api/telemetry/heartbeat` with `TELEMETRY_TOKEN`, stored as `NodeHeartbeat`; ntfy messages become `Status`; `context_processors.global_telemetry` injects both into every template.
- **Images**: `Image` model with generic upload path (`get_image_upload_path`) and `pre/post_delete`/`pre_save` signals in `models.py` that delete files on delete or replacement — keep that in mind when touching image fields or tests (tests use temp media dirs).
- Frontend is server-rendered: `templates/portfolio/base.html`, `index.html`, `project.html`, plus `_log*.html` partials fetched via `api/logs/...`.

## Tests

`portfolio/tests.py` (images/admin/views, large), `test_hackerrank.py`, `test_telemetry.py`. Network calls (HackerRank, ntfy) are mocked with `unittest.mock`.
