# AI Agent Certification Lab

A full-stack Flask web application for learning and getting certified on
building AI agents. Users register/log in, work through three hands-on
modules (lesson + code exercise + auto-graded quiz), then sit a final
certification exam. Passing the exam (80%+) issues a downloadable PDF
certificate with a unique certificate ID.

## Features

- **Authentication** — email/password registration and login using
  Flask-Login, with hashed passwords (Werkzeug `generate_password_hash`),
  session-based auth, "remember me," and route protection via
  `@login_required`.
- **Three learning modules**:
  1. Agent Foundations (observe-think-act loop)
  2. Tool Use & Function Calling
  3. Multi-Agent Orchestration & Safety
- **Auto-graded quizzes** — server-side grading, per-module pass threshold,
  progress persisted per user in SQLite.
- **Final certification exam** — unlocked only after all modules are
  complete; requires 80%+ to pass.
- **PDF certificate generation** — a formatted certificate (name, score,
  certificate ID, issue date) generated with ReportLab and available for
  download.
- **Custom styling** — a navy/gold "credential" design system (no CSS
  framework dependency), responsive down to mobile, with visible focus
  states and reduced-motion support.

## Project structure

```
ai_agent_cert_lab/
├── app.py                 # Flask app: routes, models, auth, exam logic
├── lab_content.py          # Module lessons, exercises, quizzes, final exam
├── certificate.py          # PDF certificate generator (ReportLab)
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── module.html
│   ├── exam.html
│   ├── certificate.html
│   └── 404.html
├── static/
│   └── css/style.css
├── certificates/           # generated PDF certificates land here
└── instance/                # SQLite database (created on first run)
```

## Setup

1. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set a secret key (recommended for anything beyond local testing)**
   ```bash
   export SECRET_KEY="replace-with-a-long-random-string"   # Windows: set SECRET_KEY=...
   ```
   If not set, the app falls back to a development-only default — do not
   use that default in production.

4. **Run the app**
   ```bash
   python app.py
   ```
   The database and certificates folder are created automatically on first
   run. Open **http://127.0.0.1:5000** in your browser.

## How it works

1. Register an account (name, email, password — min. 8 characters).
2. From the dashboard, open each module: read the lesson, review the code
   exercise (a reference solution is available under "Show reference
   solution"), then answer the quiz. You can retry a module's quiz as many
   times as needed; your best score is kept.
3. Once all three modules are marked complete, the **Certification Exam**
   unlocks on the dashboard.
4. Score 80% or higher on the exam to receive your certificate. It's stored
   against your account, viewable at `/certificate`, and downloadable as a
   PDF at any time.

## Extending this project

- **Swap SQLite for Postgres**: change `SQLALCHEMY_DATABASE_URI` in
  `app.py` (e.g. to a `postgresql://...` URL) — the SQLAlchemy models need
  no changes.
- **Add more modules**: append entries to the `MODULES` list in
  `lab_content.py` following the existing dict shape; the dashboard and
  module routes are fully data-driven.
- **Email verification / password reset**: hook in Flask-Mail and add
  token-based confirmation routes alongside the existing auth routes.
- **Real code grading**: the exercise "solution" is currently shown for
  self-checking. For automated grading, you could run submitted code in a
  sandboxed subprocess against unit tests before marking it correct.

## Security notes

- Passwords are hashed with Werkzeug's `generate_password_hash` (PBKDF2)
  and never stored in plain text.
- Sessions are managed by Flask-Login with a signed session cookie tied to
  `SECRET_KEY` — always set a strong, unique `SECRET_KEY` outside of local
  development.
- All module/exam/certificate routes are protected by `@login_required`.
- Certificate PDFs are served only to the authenticated owner via
  `send_from_directory`, not from a public static folder.
