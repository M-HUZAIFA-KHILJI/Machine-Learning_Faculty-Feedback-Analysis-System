# Machine Learning Faculty Feedback Analysis System

## Introduction

This repository contains a web application that collects, stores, and analyzes textual feedback for faculty members using modern machine learning and web technologies. The application extracts sentiment and basic statistics from free-text feedback, visualizes trends and distributions, and provides an accessible UI for submitting and browsing feedback.

The system was built as a practical example of applying natural language processing (NLP) and data visualization to feedback analysis problems. Although the domain in this project is faculty/course feedback, the architecture and techniques are intentionally general so they can be adapted to other industries and feedback types.

## Project Scope

- Collect free-text feedback and associate it with entities (e.g. faculty, product, store, representative).
- Automatically extract sentiment scores and labels from textual feedback.
- Aggregate metrics (counts, averages, trends) and surface them through an interactive dashboard.
- Provide a lightweight UI for submitting feedback and viewing details for a single entity.
- Enable re-use and adaptation of the analysis pipeline across different domains (education, customer support, retail, HR, product reviews, etc.).

The intent is to provide a reusable reference implementation that demonstrates a complete flow from data collection through model-driven scoring to end-user visualizations and export-ready summaries.

## Headings / Techniques Implemented

The codebase implements and demonstrates the following techniques and components:

- Data model and storage
  - Django models for entities (Professor) and feedback (Comment)
  - SQLite used for development (excluded from repository history by default)

- Natural Language Processing & Sentiment
  - Text preprocessing and token handling
  - Sentiment scoring (numeric score + categorical label)
  - Simple word-frequency extraction for word clouds and keyword summaries

- Aggregation & Analytics
  - Queryset annotations (Count, Avg) to avoid N+1 queries and compute aggregates server-side
  - Trend extraction (time-series aggregation by day/week)
  - Histogram and distribution calculations for score ranges

- Frontend Visualization
  - Bootstrap 5 responsive UI for pages and forms
  - Chart.js for pie/line/bar/histogram visualizations
  - A lightweight word-cloud visualization for keyword exploration

- DevOps / CI
  - Basic GitHub Actions workflow for CI checks (Python lint/test skeleton)
  - `.gitignore` configured to exclude virtual environments and local DB files

- Code organization & best-practices
  - Django app separation (`feedback` app) and `templates` / `static` structure
  - Template inheritance via `base.html` for consistent layout
  - Reusable template tags (e.g., name initials helper)

## Structure (important files)

- `feedback/` — Django app containing models, views, templates, static assets, and utilities
- `feedback/templates/feedback/` — core HTML templates (`base.html`, `home.html`, `dashboard.html`, `submit_feedback.html`, `professor_detail.html`)
- `feedback/static/feedback/css/app.css` — shared stylesheet for updated UI
- `feedback/utils/sentiment_analyzer.py` — sentiment analysis helper used to score comments
- `manage.py` — Django management entrypoint
- `README.md` — this file

## Installation (development, Windows PowerShell)

1. Create (or activate) your Python virtualenv. If you already have the included `sentiment_env`, activate it:

```powershell
# If using included virtualenv (PowerShell)
D:\uni\S7\PSA\Sentiment_feedback\sentiment_env\Scripts\Activate.ps1

# Or create a new venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies (if a `requirements.txt` is present) or your project's requirements:

```powershell
pip install -r requirements.txt
```

3. Run Django migrations and start the server:

```powershell
# from repository root
cd D:\uni\S7\PSA\Sentiment_feedback
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

4. Open the app in your browser: `http://127.0.0.1:8000/`

## Usage

- Submit feedback via the web form (Submit Faculty Feedback).
- Visit the dashboard to inspect sentiment distributions, time trends, and word clouds.
- Use the admin interface (`/admin/`) to manage professors and comments if needed.

## Security & Privacy Notes

- The repository excludes `db.sqlite3` and local virtual environments via `.gitignore`. If you need to remove the DB from the repository history, use `git filter-repo` or BFG and coordinate a force-push (I can assist if desired).
- Do not commit credentials or environment files (`local_settings.py`, `.env`) to the repo.

## Next Improvements (suggestions)

- Replace the simple sentiment model with a fine-tuned transformer for domain-specific accuracy.
- Add authentication & role-based access (submitter vs admin vs analyst).
- Add export endpoints (CSV/JSON) for aggregated reports.
- Add automated end-to-end tests and visual regression tests for the frontend.
- Add pagination and search for large feedback collections.


---

 `README.md`.
