import os
import typing as t

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from app.ext.sqlalchemy.database import init_database

from app import blueprints

from app.jinja import register_jinja_mapping
from app.errors import register_error_handlers

from app.ext.sentry import init_sentry
from app.ext.cache import cache


def init_configuration(app: Flask, test_config: t.Optional[dict] = None) -> None:

    # Load the default configuration
    app.config.from_object('config.default')

    # load configuration from .env
    app.config.from_prefixed_env()

    # Variables defined here will override those in the default configuration
    app.config.from_object(f"config.{os.environ.get('APP_CONFIG', 'production')}")

    if test_config is None:
        # Load the configuration from the instance folder (created by configure.py)
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is not set. Run `python configure.py` to create instance/config.py, "
            "or set FLASK_SECRET_KEY."
        )


def create_app(test_config: t.Optional[dict] = None) -> Flask:
    app: Flask = Flask(__name__, instance_relative_config=True)

    # first, init configurations
    init_configuration(app, test_config)

    init_sentry(app)

    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        init_database(app)

    cache.init_app(app)
    register_jinja_mapping(app)

    # automatically enabled when DEBUG_TB_ENABLED=True
    # https://github.com/flask-debugtoolbar/
    DebugToolbarExtension(app)

    # With strict slashes off, example.com/url/ serves the same view as example.com/url
    app.url_map.strict_slashes = app.config.get("FLASK_STRICT_SLASHES")

    register_error_handlers(app)
    blueprints.register_blueprints(app)

    return app
