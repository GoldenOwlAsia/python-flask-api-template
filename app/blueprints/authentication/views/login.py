# https://flask.palletsprojects.com/en/2.1.x/views/#method-based-dispatching

from flask.views import MethodView
from flask import jsonify, request, session
from flask import make_response, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from app.ext.sqlalchemy.database import db_session
from app.blueprints.authentication.models.model import FlaskUser
import hashlib
import hmac


def is_legacy_md5_match(stored_password: str, password: str) -> bool:
    # Accounts registered before the switch from unsalted MD5 hashes
    legacy_hash = hashlib.md5(password.encode()).hexdigest()
    return len(stored_password) == 32 and hmac.compare_digest(stored_password, legacy_hash)


class login(MethodView):

    def get(self):
        return make_response(
            render_template(
                "login.jinja2",
            )
        )

    def post(self):
        username = request.form["email"]
        password = request.form["password"]

        user = db_session.query(
            FlaskUser
        ).filter_by(
            username=username
        ).first()
        stored_password = (user.password or "") if user else ""

        if user and is_legacy_md5_match(stored_password, password):
            user.password = generate_password_hash(password)
            db_session.commit()
        elif not user or not check_password_hash(stored_password, password):
            # Same answer for unknown users and wrong passwords
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        session.clear()
        session["user_id"] = user.id

        return jsonify({
            "message": "login successfully"
        })
