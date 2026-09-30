# Learning Lounge by ismail

A runnable modular Flask learning platform with a Python 3.14 introductory curriculum. The platform name is configurable through `PLATFORM_NAME`.

## Review stage

The UI now includes remembered light/dark themes, simplified learning navigation, owner-managed resources and categories, lesson continuation, a code reset action, and the owner-supplied Gwen character. See `REVIEW_NOTES.md` for validation limits and `OWNER_ACCESS.md` for private owner setup. The final ZIP and owner PDF are deferred until approval.

## Delivery status

This is a working first implementation, **not full completion of the attached production specification**. It includes registration/login, learner profiles, enrollment, 29 introductory lessons, administrative content editing, version-snapshotted timed assessments, autosave, objective scoring, Judge0 grading adapter, Gemini/Ollama structured-output adapters, results, a basic mistake notebook and roadmap, PDF assessment achievement certificates, revocation, migrations, and critical integration tests.

The local preview is http://localhost:5066 . Create your own learner account; no default administrator/password is installed.

### Still incomplete

- The reviewed starter bank contains 12 non-coding questions and one coding draft. It does not cover every lesson, level, or specialist subject. Final assessments deliberately refuse to start without full topic coverage. Lessons are introductory, not a comprehensive specialist course in each listed field.
- Practice supports an optional timer, tracked hints, and immediate answer feedback. Detailed retry history and adaptive question selection remain to be implemented.
- Daily sessions are reused per learner/course/local calendar date, with date-seeded selection. Different setup filters can still produce different questions for different learners. Streaks use completed assessment dates in the profile timezone. Placement uses category-balanced question selection, not a calibrated placement model.
- The roadmap recommends existing lessons from missed topics; prerequisite-aware adaptive ordering and persistent roadmap records remain incomplete.
- Admin CRUD uses basic field forms, including JSON editors for question tests and scoring rules. Batch generation, provider-setting UI, aggregate analytics, near-duplicate detection, and auditable invalidation/regrading with certificate replacement remain incomplete. Revocation works; the replaced status is only a status marker and does not create a replacement certificate.
- Certificates currently represent passing exam achievement only; course-completion criteria and separate result/completion credential types remain incomplete. The built-in PDF font has limited Unicode coverage.
- Models store options, tests, and snapshots as JSON. This preserves historical results but does not fully implement the normalized schema requested in the brief. Lists have bounded limits rather than page controls.
- AI question generation and result analysis are bounded synchronous operations. Grading retry/deadline sweeps use Celery, but initial grading can still run in the submission request. Full asynchronous jobs, scalable per-test scheduling, and fine-grained worker leases remain work for production.
- SMTP support is intended for a local Mailpit or trusted internal relay. Authenticated/TLS SMTP configuration and session invalidation after password reset are not yet implemented.
- No live Gemini, Ollama, Judge0, PostgreSQL, Redis/Celery, reverse-proxy, or Docker deployment was exercised. Their absence is not represented as successful integration. Production hardening, load/concurrency tests, and live sandbox escape/resource tests remain required.

## Local setup

Python 3.14 recommended. Dependencies are pinned from the installed, tested environment.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# Set a random SECRET_KEY in .env.
.venv/bin/flask --app run db upgrade
.venv/bin/flask --app run seed
.venv/bin/flask --app run create-admin
.venv/bin/python run.py
```

Open http://localhost:5066 . The seed command is idempotent. Use `create-admin` interactively; passwords are hashed and there are no default credentials. In local development without SECRET_KEY, a private persistent key is generated under the ignored `instance/` directory. Production requires an explicit secret.

### Deadlines while the browser is closed

Run Redis plus both workers:

```sh
.venv/bin/celery -A app.tasks.celery worker --loglevel=INFO
.venv/bin/celery -A app.tasks.celery beat --loglevel=INFO --schedule=/tmp/lounge-celerybeat
```

The periodic sweep checks every 15 seconds, catches overdue attempts after restarts, and retries pending grading. A manual `.venv/bin/flask --app run sweep` is also available. With no worker, visiting an expired attempt still finalizes it, but unattended deadlines will not be processed. Interrupted evaluation claims recover after a conservative four-hour lease. Run only one beat scheduler.

### AI setup

The local app is set to Gemini. Create an API key in [Google AI Studio](https://aistudio.google.com/apikey), open the private `.env` file, and fill in `GEMINI_API_KEY`. Do not put keys in chat, browser JavaScript, or source control. Restart the app after saving. The selected model is `gemini-3.1-flash-lite`; change `AI_MODEL` if your account requires another model. This lightweight model offers free-tier access subject to Google account eligibility and quota. Keep the Google project on the Free tier for free usage; selecting a model does not change project billing. No fallback to a different model is configured. An empty key leaves AI unavailable; a configured status does not verify a live connection.

For Ollama instead, set `AI_PROVIDER=ollama`, `AI_MODEL` to an installed model, and `AI_ENDPOINT` to your Ollama service. Both adapters validate Pydantic schemas, enforce output limits/timeouts, and retry at most three times. Generated questions remain outside the approved exam bank until human review. AI cannot alter marks.

### Mail

For development, use Mailpit (Compose profile `dev-mail`), set `MAIL_HOST=localhost`, `MAIL_PORT=1025`, and read the inbox at http://localhost:8025 . Within Compose use `MAIL_HOST=mailpit`. Password resets expire after 30 minutes and use hashed, single-use tokens. Unconfigured delivery is shown on the reset page.

### Code execution

Follow [deploy/RUNNER.md](deploy/RUNNER.md). Code categories stay unavailable without a configured operator-approved runtime. The coding seed is deliberately a draft until its reference solution is validated against a real runner. Hidden tests never leave the server except for the configured isolated grader. Infrastructure failures preserve code and remain pending, never false zeroes.

## Tests and migrations

```sh
.venv/bin/python -m pytest -q
.venv/bin/flask --app run db upgrade
```

Tests cover registration/enrollment, lesson persistence, adding a new course through administration, immutable question snapshots, deadlines surviving refresh, autosave, closed-browser sweep, late answer rejection, ownership, active-answer secrecy, repeat submissions, PDF verification/revocation, invalid AI structures, CSRF, and pending runner failures/weighted partial credit. Runner responses are test doubles; these tests do not establish real sandbox isolation.

## Deployment

Use the included Dockerfile and Compose services for web, PostgreSQL, Redis, worker, and beat. Add `POSTGRES_PASSWORD` to `.env`, configure a stable random `SECRET_KEY`, set `PUBLIC_URL` to the HTTPS domain, and set `PRODUCTION=1`. Keep `.env` private. Configure Caddy or another HTTPS reverse proxy using the example in `deploy/Caddyfile`.

```sh
docker compose up -d db redis
docker compose run --rm web flask --app run db upgrade
docker compose run --rm web flask --app run seed
docker compose run --rm web flask --app run create-admin
docker compose up -d web worker beat
```

Do not expose Redis, PostgreSQL, or Judge0 to the internet. Use a Redis-backed limiter in production. Configure trusted proxy handling only after defining the proxy boundary; the application currently uses the directly connected IP. `/health` verifies database connectivity, not external AI or runner health.

Certificates are generated on demand from private database snapshots through authorized download routes; no PDFs are stored in public static directories. Public verification exposes only the issued credential details and current status, never email or answer history.

### Backup and restore

Back up PostgreSQL with `pg_dump -Fc` using your deployment's private credential mechanism. Restore into a separate database with `pg_restore`, then verify migrations, accounts, attempts, and certificate records before changing the live connection. For SQLite, stop writers and use Python sqlite3's backup API (or the sqlite3 `.backup` command) instead of copying an actively written file. Store backups encrypted and test restoration regularly. Preserve the session secret separately in your secret manager.

## Structure

- `app/models`: SQLAlchemy entities and immutable assessment snapshots.
- `app/routes`: authentication, learner pages, versioned API, administrator forms.
- `app/services`: assembly, scoring, deadline recovery, isolated runner, certificate rendering, seeding.
- `app/ai`: provider abstraction, current google-genai SDK adapter, Ollama HTTP adapter, schemas.
- `app/tasks`: Celery periodic deadline/grading sweep.
- `data/curriculum.py`: 29 versioned introductory lessons with examples and exercises.
- `migrations`: Alembic schema history.
- `tests`: behavior and security regression tests.
- `app/static/vendor`: locally served Bootstrap 5.3.8, CodeMirror 5.65.20, Chart.js 4.5.1 (upstream license headers retained).

## Documentation checked during implementation

- Flask installation and support: https://flask.palletsprojects.com/en/stable/installation/
- Python 3.14 reference and tutorial: https://docs.python.org/3.14/tutorial/
- Gemini structured responses: https://ai.google.dev/gemini-api/docs/structured-output
- Judge0 request limits and submission API: https://ce.judge0.com/
- Ollama structured outputs: https://docs.ollama.com/capabilities/structured-outputs

No external accreditation or cheating-detection claims are made.
