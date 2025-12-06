# AI-Powered RFP Management System

A full-stack RFP/procurement tool with a Flask backend and static HTML/CSS/JS frontend.

## Project Structure
- backend/ – Flask app, APIs, database models, email + AI services
- frontend/ – static pages, CSS, and JS
- .env.example – environment variable template

## Prerequisites
- Python 3.13+
- Node is *not* required (static frontend)

## Setup
1) Clone the repo and navigate to proejcts/.
2) Copy .env.example to .env and fill values (see Environment below).
3) Install backend deps:
   bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   
4) Initialize DB (SQLite by default):
   bash
   python app.py  # first run creates rfpsystem.db
   

## Running
bash
cd backend
python app.py

- Backend: http://127.0.0.1:5000
- Frontend served by Flask from frontend/

## Environment
Key variables (see .env.example):
- SECRET_KEY
- DATABASE_URL (default sqlite:///rfp_system.db)
- Mail: MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER
- AI (Groq): GROQ_API_KEY, GROQ_MODEL

## Notable APIs (prefixed with /api)
- RFPs: POST /rfp/create, GET /rfp/list, PUT /rfp/<id>/update, POST /rfp/<id>/send, GET /rfp/<id>/proposals
- Vendors: POST /vendor/add, GET /vendor/list, PUT /vendor/<id>, DELETE /vendor/<id>, GET /vendor/search
- Proposals: GET /proposal/list, POST /proposal/parse, POST /proposal/compare

## Email Sending
The Flask-Mail instance is injected into email_service; ensure mail env vars are valid. Sending RFP emails requires a working SMTP configuration.

## Frontend Notes
- Entry: frontend/index.html
- Styles: frontend/css/style.css
- Scripts: frontend/js/main.js

## Troubleshooting
- Missing styles: ensure Flask app uses static_url_path='' (already set) and hard-refresh the browser.
- Date parse fallback: deadline defaults to 30 days out if parsing fails.
- AI calls: require valid GROQ_API_KEY.

## Future Improvements
- Add loading skeletons and improved empty states
- Add tests for API endpoints
- Optional: migrate to a component framework (e.g., React) if needed
