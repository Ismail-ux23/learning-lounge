# Private owner access notes — review stage

This document is repository documentation, never served through learner routes. A final PDF guide will be prepared only after approval.

## Project and backend

Project directory: `/Users/macbook/learning-lounge`.

Activate the local environment or run tools with `.venv/bin/`. The Flask application factory is `app.create_app`; `run.py` starts the local server on port 5066. `wsgi.py` exports the production application.

## Administrator access

Run `.venv/bin/flask --app run create-admin` from the project directory. It prompts privately for an email, full name, and password. No shared/default administrator credential exists. Sign in through the ordinary login form, then visit `/admin/`.

The admin interface manages courses, modules, topics, lessons, versioned questions, resources, categories, users, reports, certificate status, and lesson progress. Relationships use record IDs. Course rules and question content use JSON fields in this review implementation. Archive content used by historical attempts; there is no destructive delete control for referenced learning content.

## Database

Local SQLite database: `instance/lounge.db`. This contains private learner records. Do not place it in the static directory, share it publicly, or include it in the eventual source ZIP. Use a SQLite database browser locally or `.venv/bin/flask --app run shell` with `app.extensions.db` and the model classes.

Production uses the `DATABASE_URL` environment variable with PostgreSQL. Apply schema updates using `.venv/bin/flask --app run db upgrade`. Migration scripts are under `migrations/versions/`. `flask db check` detects model/schema drift against the current migration history.

## Configuration

Copy `.env.example` to the ignored `.env` file, then set private values there or in a deployment secret store. `SECRET_KEY` must be random and stable in production. `PLATFORM_NAME` controls branding, `PUBLIC_URL` controls verification/reset links, and `PRODUCTION=1` enables secure cookies and mandatory secret validation.

AI requires `AI_PROVIDER`, `AI_MODEL`, and the appropriate endpoint/key. Judge0 needs `JUDGE0_URL`, an optional token, and an operator-approved execution profile. Mail delivery is configured through the mail environment settings; the current implementation targets Mailpit or a trusted relay. See README.md for limitations and deployment instructions.

## Storage and backups

Certificates are streamed from private database snapshots through authorized routes. They are not stored as public files. Keep uploaded branding in `app/static/images`; private learner files must not go there.

Follow the backup/restore section of README.md. Back up the database and deployment configuration separately, with encryption and restricted access. Test restoration on a separate database before touching live data.
