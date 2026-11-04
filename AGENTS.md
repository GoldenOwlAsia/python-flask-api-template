# Flask API template: agent guide

Stack: Python 3.12, Flask 3.1, SQLAlchemy 2.0 with a global scoped session, Alembic 1.13, Jinja2, Postgres 14, unittest. `requirements.txt` is exact-pinned; pin every new dependency.

## Agent shell rules
- Start agents from this repo's root, not from a parent folder or a subfolder. `.claude/settings.json` (permission rules and the guard hook) loads only from the folder the agent starts in.
- Agent shells do not stay activated. Call every tool by its venv path (`.venv/bin/python`, `.venv/bin/flask`, `.venv/bin/alembic`) and run everything from the repo root: `BLUEPRINTS_DIRECTORY` is a relative path, so the app only boots there.
- Never read, print, copy or edit `.env` (or `.env.<name>`), `instance/` or `alembic.ini`. They hold secrets and a human fills them in. If you need a value, ask. The `*.example` files are safe to read.
- Search code with `git grep -n <pattern>` (add `--untracked` for files you just created): it never reads gitignored files such as `.env`. Don't use `grep -r` on the repo.
- Never run `python configure.py`. It is interactive (it waits on prompts forever) and writes SECRET_KEY. Ask the human to run it.
- Claude Code reads this file only if there is no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in this folder or any folder above it, committed or not. Don't create one. For personal notes use `~/.claude/CLAUDE.md`, or start a `CLAUDE.local.md` with the line `@AGENTS.md`.

## Commands
- Setup: `uv venv --seed --python 3.12 --allow-existing .venv && .venv/bin/pip install -r requirements.txt`. Safe to re-run; run it again after changing requirements.txt. psycopg2 is the source build, not `-binary`, so `pg_config` must be on PATH (check with `command -v pg_config`): use Postgres.app with its bin folder on PATH, or `brew install libpq`, which is keg-only, so install with `PATH="$(brew --prefix libpq)/bin:$PATH" .venv/bin/pip install -r requirements.txt`.
- Test: `.venv/bin/python -m unittest -v`. It uses a temporary SQLite file and needs no database, `.env` or instance config. One test: `.venv/bin/python -m unittest tests.test_authentication.TestAuthentication.test_login_sets_session`
- Routes: `FLASK_SECRET_KEY=dev .venv/bin/flask --app wsgi routes`
- Dev database: first run `docker inspect -f '{{json .HostConfig.PortBindings}}' flask`. If it says `No such object`, create the container: `docker run --name flask -p 127.0.0.1:5435:5432 -e POSTGRES_PASSWORD=flask -e POSTGRES_USER=flask -e POSTGRES_DB=flask -d postgres:14`. If every HostIp is `127.0.0.1`, run `docker start flask`. If any HostIp is empty or `0.0.0.0`, the container comes from the old README and listens on every network interface: don't start or use it, and ask the human to recreate it (`docker rm -f flask` deletes its data, and you can't run `docker rm`).
- Run: `APP_CONFIG=development FLASK_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex())') FLASK_SQLALCHEMY_DATABASE_URI=postgresql://flask:flask@localhost:5435/flask .venv/bin/flask --app wsgi run --no-debugger --no-reload --port 5001`, then smoke-test at http://127.0.0.1:5001 (`--port` overrides FLASK_RUN_PORT from `.env`). Before any POST request, run `test -f instance/config.py && echo present || echo absent`. If it prints `present`, that file loads last and replaces both FLASK_ variables above (configure.py always writes SECRET_KEY and SQLALCHEMY_DATABASE_URI): an empty URI makes POST `/auth/login` and `/auth/register` return 500, and a real one receives your test accounts. Ask the human which database it names first. GET pages are safe either way.
- Migrations (Postgres only), with an `alembic.ini` a human created from `alembic.ini.example`: `.venv/bin/alembic current`, `.venv/bin/alembic upgrade head`. Without a database, use the example config: `.venv/bin/alembic -c alembic.ini.example heads`, `... history`, and `... upgrade <from>:<to> --sql` to preview SQL. Always pass `--sql` with `-c alembic.ini.example`: its URL is the docker dev database, so without `--sql` it migrates that database. Read `alembic/AGENTS.md` before touching migrations or models.
- Production: `uwsgi --ini webservice.ini` (uwsgi is not in requirements.txt).
- There is no linter, type checker, Dockerfile, compose file or CI yet.
- Agent hook tests: `python3 -m unittest discover -s .claude/hooks`

## Layout
- `app/app.py`: `create_app(test_config)`.
- `app/blueprints/<bp>/`: `routes.py` exports `blueprint`; `views/*.py` hold MethodView classes; `models/model.py`; `templates/`.
- `app/blueprints/models.py` imports every model so Alembic can see it.
- `app/ext/sqlalchemy/`: the global scoped `db_session`, `BaseModel`, `id_column()`, `int_fk_column()`. Also `app/ext/{sentry,cache}`, `app/jinja`, `app/errors`.
- `config/{default,development,production}.py`; `instance/config.py` (gitignored secrets); `alembic/`; `tests/`.
- Skills for repeatable tasks are in `.agents/skills/` (Claude Code reaches them through the `.claude/skills/` symlinks). If `.claude/skills/<name>` is a one-line text file rather than a folder (a Windows clone without symlinks), read `.agents/skills/<name>/SKILL.md` directly and tell the user to run `git config core.symlinks true` and `git checkout -- .claude/skills`.

## Config precedence (`init_configuration` in app/app.py)
`config.default`, then `FLASK_*` environment variables with the prefix stripped (FLASK_SECRET_KEY becomes SECRET_KEY), then `config.<APP_CONFIG>` (default `production`, which overrides the environment), then `instance/config.py` (skipped when `test_config` is passed). A missing SECRET_KEY raises RuntimeError. `.env` is loaded only by the flask CLI, never by unittest.

## Gotchas
- Every folder under `app/blueprints/` is imported as a blueprint and must have a `routes.py` defining `blueprint`. `BLUEPRINTS_BOILERPLATE` and simple-term-menu are leftovers: there is no generator.
- Without a database URI, POST `/auth/login` and POST `/auth/register` return 500 (UnboundExecutionError). The GET pages still render.
- The production config sets `SESSION_COOKIE_SECURE`, so the login cookie is dropped over plain http. Use `APP_CONFIG=development` locally.
- The 404 handler returns status 200 (`app/errors/__init__.py`).
- On macOS, AirPlay Receiver listens on port 5000. A 403 with `Server: AirTunes` means you reached AirPlay, not Flask, hence `--port 5001` above.
- Tests build tables with `metadata.create_all`, never migrations. Migrations don't run on SQLite.
- `BaseModel` has no naming convention, so autogenerate emits unnamed constraints. `downgrade` below d451affc417a cannot compile, so never run `alembic downgrade base`.
- The model says `username` is `String(255)` but the migrations created `VARCHAR(100)`, so autogenerate shows that diff and `alembic check` always fails on it. That failure is expected; don't add a revision for it unless the task is about it.

## Security invariants (keep tests/test_authentication.py green)
- Hash passwords only with werkzeug `generate_password_hash`/`check_password_hash`, never md5, sha or plain text. The legacy MD5 branch in `views/login.py` only rehashes old accounts; don't extend it.
- Return the same 401 for an unknown user and a wrong password. Call `session.clear()` before setting `session["user_id"]`.
- Autoescape is forced in `app/jinja/__init__.py`. Never use `|safe` or `Markup` on user data.
- There are no CSRF tokens (SameSite=Lax only), so never change state on GET.
- No secrets in `config/`, tests or committed files. DEBUG and the debug toolbar belong only in `config/development.py`. Sentry never sets `send_default_pii`. No f-string SQL.

## Code Review Rules
The invariants above, plus: each new model is imported in `app/blueprints/models.py` and has a migration with named constraints, and the test suite passes.

## Done means
`.venv/bin/python -m unittest -v` is green from the repo root, `FLASK_SECRET_KEY=dev .venv/bin/flask --app wsgi routes` lists the new endpoints, and the README is updated if a command changed.
