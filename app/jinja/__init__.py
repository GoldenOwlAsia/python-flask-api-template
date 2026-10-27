from flask import Flask

from app.jinja.filters import register_filters
from app.jinja.context_processor import register_context_processor


def register_jinja_mapping(app: Flask) -> None:
    # Flask only autoescapes .html/.htm/.xml/.xhtml/.svg, and our templates are .jinja2
    app.jinja_env.autoescape = True

    register_filters(app)
    register_context_processor(app)
