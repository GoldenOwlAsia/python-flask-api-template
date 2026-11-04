---
name: add-alembic-migration
description: Create, check and apply an Alembic migration for this repo's Postgres database after a SQLAlchemy model change in app/blueprints/*/models. Use when a table, column, index or constraint changes, when asked to add or fix a migration, or when alembic heads or upgrade fails.
---
# Add a migration

Preconditions: run from the repo root; the local Postgres is up on 5435 (`docker start flask`). If `alembic.ini` is missing, ask the human to run `cp alembic.ini.example alembic.ini`. Never write database credentials yourself, and never target a database that isn't local. Read `alembic/AGENTS.md` first.

1. Confirm the model is imported in `app/blueprints/models.py`.
2. `.venv/bin/alembic -c alembic.ini.example heads` must show exactly one head. If there are two, stop and ask about a merge revision.
3. `.venv/bin/alembic current`. If it is behind, `.venv/bin/alembic upgrade head`.
4. `.venv/bin/alembic revision --autogenerate -m "<imperative summary>"`.
5. Edit the new file: give every constraint, index and foreign key an explicit name (never `None`); remove unrelated diffs such as `flask_user.username` VARCHAR(100) to 255, or move them to their own revision; make `downgrade()` mirror `upgrade()`; split NOT NULL additions into add nullable, backfill with `op.execute(sa.text(...))` using `.bindparams()` for any values (see `alembic/AGENTS.md`), then alter.
6. Offline check of both directions: `.venv/bin/alembic -c alembic.ini.example upgrade <prev>:<new> --sql` and `.venv/bin/alembic -c alembic.ini.example downgrade <new>:<prev> --sql`.
7. Local round trip: `.venv/bin/alembic upgrade head && .venv/bin/alembic downgrade -1 && .venv/bin/alembic upgrade head`.
8. `.venv/bin/python -m unittest -v`, then report the revision id, whether it is reversible, and any data-loss risk.
