# 🎓 Learning Lounge

**Learning Lounge** is a full-stack learning and assessment platform built with Python and Flask. It provides structured courses, interactive lessons, practice sessions, timed assessments, progress tracking, AI-assisted learning features, and administrative course management.

The platform is designed with a modular architecture so additional courses, programming languages, frameworks, and learning categories can be added in the future.

## Try the project

Start with the [local installation](#-local-installation) below, then follow
[the demo walkthrough](docs/DEMO.md). The basic learner flow uses SQLite
and does not require paid AI credentials, Redis, or a code runner.

| Available locally | Needs an additional service |
| --- | --- |
| Registration, enrollment, 29 lessons, saved progress | Gemini or Ollama for AI generation and analysis |
| Objective practice and assessments from approved questions | A trusted Judge0 service for executing coding answers |
| Learner dashboard and admin content management | SMTP for password-reset email delivery |
| Certificate verification and assessment history | Redis and Celery for background jobs and periodic processing |

Assessment availability depends on approved questions covering the chosen
topics and categories. The seed contains introductory examples, not a
complete final-assessment question bank for all 29 lessons.

## ✨ Key Features

- User registration and secure authentication
- Learner profiles and course enrollment
- 29 introductory learning lessons
- Interactive practice sessions
- Timed assessments
- Automatic answer saving
- Objective question scoring
- Coding-question support through Judge0
- AI integration with Gemini and Ollama
- Structured AI-generated responses
- Mistake tracking
- Personalized learning roadmap
- Assessment result tracking
- PDF achievement certificates
- Certificate verification and revocation
- Admin content management
- Course and learning-resource management
- Light and dark themes
- Lesson continuation
- Daily learning sessions
- Progress and streak tracking
- Database migrations
- Automated integration/security tests

## 🤖 AI-Powered Learning

Learning Lounge includes an AI provider architecture supporting:

- Google Gemini
- Ollama

AI can assist with structured question generation and result analysis while keeping assessment scoring controlled by the application.

Generated questions require review before becoming part of the approved assessment bank.

## 💻 Coding Assessments

Programming exercises can be evaluated through a configured Judge0 execution environment.

The platform supports:

- Coding questions
- Hidden test cases
- Automated grading
- Partial-credit scoring
- Pending grading states
- Safe handling of runner failures

## 🧠 Assessment System

The assessment engine supports:

- Timed assessments
- Question snapshots
- Autosave
- Objective scoring
- Coding evaluation
- Deadline handling
- Repeat-submission protection
- Late-answer rejection
- Result history

Question snapshots preserve historical assessment results even when learning content changes later.

## 📊 Learning Experience

Learners can:

1. Create an account
2. Enroll in a course
3. Study lessons
4. Complete practice sessions
5. Take assessments
6. Review mistakes
7. Track learning progress
8. Receive roadmap recommendations
9. Earn assessment certificates

## 🛠️ Tech Stack

### Backend
- Python
- Flask
- SQLAlchemy
- Alembic / Flask-Migrate
- Celery

### Database & Infrastructure
- SQLite for local development
- PostgreSQL deployment support
- Redis
- Docker
- Docker Compose

### Frontend
- HTML
- CSS
- JavaScript
- Bootstrap
- CodeMirror
- Chart.js

### AI & Code Execution
- Google Gemini
- Ollama
- Judge0

### Testing
- Pytest

## 📁 Project Structure

    learning-lounge/
    │
    ├── app/
    │   ├── models/
    │   ├── routes/
    │   ├── services/
    │   ├── ai/
    │   ├── tasks/
    │   └── static/
    │
    ├── data/
    ├── deploy/
    ├── migrations/
    ├── scripts/
    ├── tests/
    │
    ├── config.py
    ├── run.py
    ├── wsgi.py
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── Dockerfile
    └── compose.yaml

## 🚀 Local Installation

Clone the repository:

    git clone https://github.com/Ismail-ux23/learning-lounge.git
    cd learning-lounge

Create a virtual environment:

    # Python 3.12 or 3.14 (tested in CI)
    python3 -m venv .venv

Activate it:

### macOS / Linux

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Create your environment configuration:

    cp .env.local.example .env

This local preset uses SQLite and process-local rate limits. With an empty
`SECRET_KEY`, the application creates a persistent private development key
in `instance/session.key`. Keep `instance/` and `.env` out of version control.
For deployment, use `.env.example` as a starting point and set a random
`SECRET_KEY`, a real Redis URL, and the other services you intend to use.

If you already have `.env`, update its values rather than overwriting it.

Run database migrations:

    flask --app run db upgrade

Seed the initial learning content:

    flask --app run seed

Create an administrator (optional for the learner demo):

    flask --app run create-admin

Start the application:

    python run.py

Then open:

    http://localhost:5066

For Windows PowerShell, replace `source .venv/bin/activate` with
`.venv\Scripts\Activate.ps1` and use `Copy-Item .env.local.example .env`.

Troubleshooting:

- **Redis connection refused:** use `REDIS_URL=memory://` for this local
  preset, or start the Redis service for the full stack. Process-local
  limits do not provide shared limits across multiple workers.
- **No such table:** run `flask --app run db upgrade` before opening the app.
- **No courses:** run `flask --app run seed`.
- **Insufficient assessment coverage:** use a topic with approved questions,
  or review and approve more questions through the admin workflow.
- **AI or coding unavailable:** configure the corresponding service; these
  features are not required to browse lessons and save progress.

## 🔐 Environment Variables

Sensitive configuration should be stored in `.env`.

Example:

    SECRET_KEY=your-secret-key
    GEMINI_API_KEY=your-api-key
    AI_PROVIDER=gemini
    AI_MODEL=gemini-3.1-flash-lite

Never commit your real `.env` file or API keys to GitHub.

## 🧪 Testing

Run the automated tests with:

    python -m pytest -q

Tests cover important platform behavior including authentication, enrollment, lesson persistence, assessments, autosave, deadlines, scoring, certificates, CSRF protection, AI response validation, and grading failures.

Final assessments include every syllabus topic and each selected question category. If the requested count cannot cover both, the application asks for more questions instead of silently leaving gaps.

The `Tests` GitHub Actions workflow runs the regression suite and a fresh-database migration/seed smoke check on Python 3.12 and 3.14 for pushes and pull requests. AI calls are mocked in tests; live Gemini/Ollama, Judge0, PostgreSQL, and Redis integrations require separate verification.

## Contributing

Install `requirements-dev.txt` and run `python -m pytest -q` before opening a pull request. For a bug report, include the steps to reproduce, expected and actual behavior, and your Python version. Remove passwords, API keys, and personal data from logs.

Keep pull requests focused on a specific fix or feature. Add a regression test when changing assessment selection, grading, deadlines, authorization, or certificate behavior. New question-bank material should include an explanation and be reviewed before approval.

## 🐳 Docker Support

The project includes:

- Dockerfile
- Docker Compose configuration
- PostgreSQL
- Redis
- Celery worker
- Celery beat

This provides a foundation for running the platform in a production-style environment.

## 🔮 Future Development

The architecture is designed to support continued expansion, including:

- Additional programming languages
- More frameworks and technologies
- Advanced learning paths
- Larger question banks
- Adaptive question selection
- Advanced learner analytics
- Expanded AI learning assistance
- More comprehensive course content
- Improved asynchronous processing
- Production deployment hardening

## 👨‍💻 Developer

**Ismail Manzoor**

Python Developer & Web Developer

GitHub: @Ismail-ux23

---

⭐ If you find Learning Lounge useful, consider starring the repository.
