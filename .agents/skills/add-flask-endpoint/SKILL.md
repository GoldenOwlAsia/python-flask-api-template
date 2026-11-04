---
name: add-flask-endpoint
description: Add an HTTP endpoint, page, API resource or whole new blueprint to this Flask template end to end - MethodView view, auto-registered routes.py, optional SQLAlchemy model and Alembic migration, Jinja template, unittest. Use when asked to add a route, endpoint, API, CRUD or feature under app/blueprints.
---
# Add an endpoint

Run every command from the repo root with the `.venv/bin/` paths.

1. Extend an existing blueprint or create `app/blueprints/<bp>/`. Every folder there is imported at boot, so it must contain `routes.py` with `blueprint = Blueprint("<bp>", __name__, url_prefix="/<bp>", template_folder="templates")`. No `__init__.py` is needed. Shared helpers go in `app/utils`, never as a bare folder in `app/blueprints`.
2. View: `views/<name>.py` with `class <name>(MethodView)` and `get`/`post` methods. Return `jsonify(...)` with an explicit status code. Register it in `routes.py`: `blueprint.add_url_rule("/path", view_func=<name>.as_view("<endpoint>"))`.
3. Model (optional): in `models/model.py`, `class FooModel(BaseModel)` creates table `foo`. Use `id_column()` and `int_fk_column("table.id")`, with explicit String lengths. Import it in `app/blueprints/models.py`, then follow the add-alembic-migration skill.
4. Template (optional): `templates/<bp>/<name>.jinja2`, extending `layouts/main.jinja2`. Template names are global across blueprints, hence the `<bp>/` prefix. No `|safe`.
5. Security: there is no `login_required`, so check `session.get("user_id")`. No state changes on GET (there are no CSRF tokens). Hash passwords with werkzeug. Return the same error for every auth failure.
6. Test: `tests/test_<bp>.py`, copying `setUp`/`tearDown` from `tests/test_authentication.py` (`create_app(test_config)` with a temporary SQLite file, `BaseModel.metadata.create_all`, `db_session.remove()`). Cover the happy path, 4xx responses and auth.
7. Verify: `.venv/bin/python -m unittest -v` and `FLASK_SECRET_KEY=dev .venv/bin/flask --app wsgi routes`, and check the new endpoints are listed.
