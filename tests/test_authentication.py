import hashlib
import os
import tempfile
from unittest import TestCase

from flask import render_template
from jinja2 import ChoiceLoader, DictLoader
from werkzeug.security import check_password_hash

from app.app import create_app
from app.ext.sqlalchemy.database import db_session
from app.ext.sqlalchemy.model import BaseModel
from app.blueprints.authentication.models.model import FlaskUser


class TestAuthentication(TestCase):

    def setUp(self):
        db_dir = tempfile.mkdtemp()
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{os.path.join(db_dir, 'test.db')}",
            "DEBUG_TB_ENABLED": False,
        })
        BaseModel.metadata.create_all(db_session.get_bind())
        self.client = self.app.test_client()

    def tearDown(self):
        db_session.remove()

    def register(self, email="user@example.com", password="pw-123456"):
        return self.client.post("/auth/register", data={"email": email, "password": password})

    def login(self, email="user@example.com", password="pw-123456"):
        return self.client.post("/auth/login", data={"email": email, "password": password})

    def test_register_stores_salted_hash(self):
        self.register()

        stored = db_session.query(FlaskUser).one().password
        self.assertNotEqual(stored, hashlib.md5(b"pw-123456").hexdigest())
        self.assertTrue(check_password_hash(stored, "pw-123456"))

    def test_login_sets_session(self):
        self.register()

        response = self.login()

        self.assertEqual(response.status_code, 200)
        self.assertIn("session=", response.headers.get("Set-Cookie", ""))

    def test_login_failures_look_the_same(self):
        self.register()

        unknown_user = self.login(email="nobody@example.com")
        wrong_password = self.login(password="wrong")

        self.assertEqual(unknown_user.status_code, 401)
        self.assertEqual(wrong_password.status_code, 401)
        self.assertEqual(unknown_user.get_json(), wrong_password.get_json())
        self.assertNotIn("Set-Cookie", wrong_password.headers)

    def test_legacy_md5_password_is_rehashed_on_login(self):
        db_session.add(FlaskUser(username="old@example.com", password=hashlib.md5(b"old-pass").hexdigest()))
        db_session.commit()

        response = self.login(email="old@example.com", password="old-pass")

        self.assertEqual(response.status_code, 200)
        stored = db_session.query(FlaskUser).filter_by(username="old@example.com").one().password
        self.assertTrue(check_password_hash(stored, "old-pass"))

    def test_trailing_slash_is_not_an_open_redirect(self):
        for path in ["/\\evil.example/", "/\t/evil.example/", "//evil.example/"]:
            # Set PATH_INFO directly: the test client would read "//host" as a host
            response = self.client.get("/", environ_overrides={"PATH_INFO": path})

            self.assertNotIn("Location", response.headers, path)

        self.assertEqual(self.client.get("/auth/login/").status_code, 200)

    def test_jinja2_templates_autoescape(self):
        # A named .jinja2 template: Flask only autoescapes .html/.xml/... by default
        self.app.jinja_env.loader = ChoiceLoader([
            DictLoader({"probe.jinja2": "{{ value }}"}),
            self.app.jinja_env.loader,
        ])

        with self.app.test_request_context():
            rendered = render_template("probe.jinja2", value="<script>")

        self.assertEqual(rendered, "&lt;script&gt;")
