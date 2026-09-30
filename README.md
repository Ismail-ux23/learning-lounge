# 🎓 Learning Lounge

**Learning Lounge** is a full-stack learning and assessment platform built with Python and Flask. It provides structured courses, interactive lessons, practice sessions, timed assessments, progress tracking, AI-assisted learning features, and administrative course management.

The platform is designed with a modular architecture so additional courses, programming languages, frameworks, and learning categories can be added in the future.

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

    python3 -m venv .venv

Activate it:

### macOS / Linux

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Create your environment configuration:

    cp .env.example .env

Set a secure `SECRET_KEY` inside `.env`.

Run database migrations:

    flask --app run db upgrade

Seed the initial learning content:

    flask --app run seed

Create an administrator:

    flask --app run create-admin

Start the application:

    python run.py

Then open:

    http://localhost:5066

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