# VibeCodeIdeaGenerator

## Scope

All work must be scoped to this directory (`/Users/simonmurray/Desktop/VibeCodeIdeaGenerator/`). Do not read, modify, or reference files outside of this project folder.

## Project Overview

A FastAPI web app that suggests vibe coding app ideas using the Claude Haiku 4.5 API. Two users (Euty and Simon) enter their work experience, the app generates 3 tailored app suggestions, users can save ideas to SQLite, and clicking a saved idea opens a detail page for deep-dive analysis (build requirements, route to market, adoption strategy).

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
models.py           # Idea ORM model (single table: ideas)
claude_client.py    # AsyncAnthropic wrapper: generate_ideas(), generate_deep_dive()
templates/
  base.html         # Layout: Google Fonts, Pico CSS, Lucide icons CDN, sticky nav, footer, Lucide init
  home.html         # Gradient hero, input section card, experience form, idea cards with save buttons
  saved.html        # Page header with count, idea cards grid with analysis badges, empty state
  detail.html       # Gradient accent header, collapsible experience, deep-dive display (marked.js), CTA
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
| GET    | `/saved`                 | List all saved ideas                           |
| GET    | `/idea/{id}`             | Idea detail page with deep-dive content        |
| POST   | `/idea/{id}/deep-dive`   | Generate deep-dive via Claude, redirect back   |
| POST   | `/idea/{id}/delete`      | Delete idea, redirect to /saved                |

## Database Schema

Single table `ideas`: id (PK), title, summary, euty_experience, simon_experience, deep_dive (nullable), created_at.

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
- **Loading UX**: JavaScript disables submit buttons and shows spinner during API calls
- **Default experiences**: Euty and Simon have pre-filled default experience text in the home page form
- **Session persistence**: Generated ideas persist on home page via sessionStorage until new ones are generated
- **Lucide icons**: Initialized via `lucide.createIcons()` on DOMContentLoaded; must be re-called after dynamic HTML injection (e.g., sessionStorage restore)

## UI Design System

- **Colors**: Indigo/violet gradient primary (`#4f46e5` → `#7c3aed`), amber accent (`#f59e0b`), slate text scale
- **Font**: Inter (400, 500, 600, 700) from Google Fonts
- **Cards**: White surface on slate-50 background, subtle borders, soft shadows, hover lift with staggered slide-up animations
- **Nav**: Sticky with backdrop blur and bottom border
- **CDN resources**: Pico CSS v2, Google Fonts (Inter), Lucide icons, marked.js
