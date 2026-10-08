# Class 9 ICSE Online Test Platform

Streamlit app for Class 9 ICSE students to take subject-wise tests, with an admin dashboard,
OTP-verified registration, PDF result export and performance analytics.

## Run locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Set `USE_POSTGRES=true` plus `POSTGRES_HOST`, `POSTGRES_DATABASE`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_PORT` (env vars or `.env`) to use PostgreSQL; otherwise SQLite is used.
In production the same values come from Streamlit secrets (see `.streamlit/secrets.toml.template`).

## Layout
| Path | Purpose |
|---|---|
| `streamlit_app.py`, `auth.py`, `generate_test_engine.py`, `db_connection.py` | The application |
| `schema_postgres.sql` | PostgreSQL schema |
| `scripts/db/` | One-off migration / data-fix scripts |
| `scripts/checks/` | Ad-hoc DB checks |
| `tools/` | OCR and question-data tooling (dev only) |
| `ChatBot/` | Separate AI tutor (not imported by the main app) |
| `pdfs/`, `ocr_output/` | Source textbooks and OCR text |
| `docs/` | Guides: setup, deployment, OTP, admin features |

## Running the helper scripts
Run from the repository root so `db_connection` is importable, and never hardcode credentials:
```bash
python -m scripts.db.create_admin
```
