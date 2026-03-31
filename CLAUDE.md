# VibeCodeIdeaGenerator

## Scope

All work must be scoped to this directory (`/Users/simonmurray/Desktop/VibeCodeIdeaGenerator/`). Do not read, modify, or reference files outside of this project folder.

## Project Overview

A FastAPI web app that suggests vibe coding app ideas using the Claude Haiku 4.5 API. Two users (Euty and Simon) enter their experience and current interests, the app generates 3 practical, tailored app suggestions (with a "why it's exciting" hook), users can save ideas to SQLite, and clicking a saved idea opens a detail page for deep-dive analysis (build requirements, first weekend sprint, route to market, growth playbook).

## Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **Templates**: Jinja2 (server-side rendered)
- **Database**: SQLite via SQLAlchemy ORM
- **AI**: Anthropic Python SDK — model `claude-haiku-4-5-20251001` (async client)
- **Styling**: Pico CSS (CDN) + custom CSS design system, Inter font (Google Fonts), Lucide icons (CDN), marked.js (CDN) for markdown rendering
- **Environment**: python-dotenv for `.env` config

## Project Structure

```
app.py              # FastAPI app, all routes, entry point
database.py         # SQLAlchemy engine, SessionLocal, Base, init_db(), get_db()
models.py           # ORM models: Idea table + UserProfile table (one per user)
claude_client.py    # AsyncAnthropic wrapper: generate_ideas(), generate_deep_dive()
templates/
  base.html         # Layout: Google Fonts, Pico CSS, Lucide icons CDN, sticky nav, footer, Lucide init
  home.html         # Gradient hero, experience form with per-user save buttons, idea cards with why_exciting
  saved.html        # Page header with count, ideas table with delete buttons, empty state
  detail.html       # Gradient accent header, collapsible experience, deep-dive display (icons, checklists, callouts, progress bar), CTA
static/
  style.css         # Design system: CSS custom properties, component styles, animations, responsive
.env                # ANTHROPIC_API_KEY (not committed)
.env.example        # Template for .env
requirements.txt    # Python dependencies
```

## Routes

| Method | Path                     | Description                                    |
|--------|--------------------------|------------------------------------------------|
| GET    | `/`                      | Home page with experience form                 |
| POST   | `/generate`              | Call Claude API, render 3 idea cards            |
| POST   | `/save`                  | Save idea to DB, redirect to /saved (PRG)      |
| GET    | `/saved`                 | List all saved ideas with delete buttons        |
| GET    | `/idea/{id}`             | Idea detail page with deep-dive content        |
| POST   | `/idea/{id}/deep-dive`   | Generate deep-dive via Claude, redirect back   |
| POST   | `/idea/{id}/delete`      | Delete idea, redirect to /saved                |
| POST   | `/api/profile`           | Save/update user experience (JSON, upsert)     |

## Database Schema

Two tables:
- `ideas`: id (PK), title, summary, euty_experience, simon_experience, deep_dive (nullable), created_at
- `user_profiles`: id (PK), name ("Euty" or "Simon"), experience (text), created_at — one row per user, upserted on save

## Development Commands

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then add ANTHROPIC_API_KEY

# Run
python app.py  # starts uvicorn on http://localhost:8000 with reload

# Alternative
uvicorn app:app --reload --port 8000
```

## Key Patterns

- **PRG (Post-Redirect-Get)**: `/save` and `/delete` routes redirect after mutation to prevent duplicate submissions
- **Hidden form fields**: carry idea data from generate → save without extra DB round trips
- **Async routes**: all route handlers are async; Claude API calls use AsyncAnthropic
- **Synchronous SQLAlchemy**: SQLite latency is negligible, no async DB driver needed
- **JSON parsing**: Claude responses are stripped of markdown code fences before `json.loads()`
- **Markdown rendering**: Deep-dive content stored as raw markdown, rendered client-side with marked.js
- **Loading UX**: JavaScript disables submit buttons and shows spinner during API calls; deep-dive generation shows animated progress bar with stage labels and elapsed timer
- **Per-user profile save**: Each user has an independent Save button; experience is upserted (one saved version per user) via `/api/profile` endpoint
- **Saved experiences**: Home page pre-fills textareas from saved profiles; changes are not persisted unless Save is clicked
- **Creative prompts**: Idea generation uses rotating creative constraints, temperature 0.8, and returns a `why_exciting` field; deep-dive uses a co-founder persona with 4 sections (build, weekend sprint, market, growth)
- **Session persistence**: Generated ideas persist on home page via sessionStorage until new ones are generated
- **Lucide icons**: Initialized via `lucide.createIcons()` on DOMContentLoaded; must be re-called after dynamic HTML injection (e.g., sessionStorage restore)

## UI Design System

- **Colors**: Indigo/violet gradient primary (`#4f46e5` → `#7c3aed`), amber accent (`#f59e0b`), slate text scale
- **Font**: Inter (400, 500, 600, 700) from Google Fonts
- **Cards**: White surface on slate-50 background, subtle borders, soft shadows, hover lift with staggered slide-up animations
- **Nav**: Sticky with backdrop blur and bottom border
- **CDN resources**: Pico CSS v2, Google Fonts (Inter), Lucide icons, marked.js
