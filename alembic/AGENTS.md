# Alembic migrations

- Run from the repo root. The config is `alembic.ini` (gitignored, created by a human from `alembic.ini.example`), or `alembic.ini.example` itself for offline `--sql` previews.
- Postgres only. Never run migrations against SQLite or any database that isn't local.
- Keep one linear chain; the current head is 028b3e3f0958. Check `.venv/bin/alembic -c alembic.ini.example heads` before and after.
- New models must be imported in `app/blueprints/models.py`, or autogenerate misses them (`env.py` builds `target_metadata` from it).
- Name every constraint, index and foreign key explicitly (`uq_<table>_<col>`, `fk_<table>_<col>_<ref>`, `ix_<table>_<col>`), never `None`. `d451affc417a` used `None`, and its downgrade can't compile.
- `downgrade()` must exactly reverse `upgrade()`. Prove both directions compile: `.venv/bin/alembic -c alembic.ini.example upgrade <prev>:<new> --sql` and `.venv/bin/alembic -c alembic.ini.example downgrade <new>:<prev> --sql`.
- Never edit or delete an existing revision; fix forward.
- Drop the unrelated `flask_user.username` VARCHAR(100) to 255 diff from autogenerate output, unless the change is about it. Because of it, `alembic check` fails even at head; that is expected.
- No app or ORM imports in revisions. Data fixes use `op.execute(sa.text("UPDATE t SET c = :v WHERE id = :id").bindparams(v=..., id=...))`. `op.execute` takes no parameters dict (a second argument raises TypeError), and `op.get_bind().execute(..., params)` renders every parameter as NULL in `--sql` previews.
- Postgres locking: ALTER COLUMN TYPE takes an ACCESS EXCLUSIVE lock and rewrites the table for most type changes (widening VARCHAR(n), or VARCHAR to TEXT, is metadata-only). Add NOT NULL columns as nullable, backfill, then alter.
- Never `downgrade base` (broken below d451affc417a) and never `stamp`.
