from flask.views import MethodView
from flask import jsonify, request
from flask import make_response, render_template
from werkzeug.security import generate_password_hash
from app.ext.sqlalchemy.database import db_session
from app.blueprints.authentication.models.model import FlaskUser

class register(MethodView):

    def get(self):
        return make_response(
            render_template(
                "register.jinja2",
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
        if user:
            return jsonify({
                "message": "User does exist"
            }) 
        
        user_create = FlaskUser(
            username=username,
            password=generate_password_hash(password)
        )

        db_session.add(user_create)
        db_session.commit()
        
        return jsonify({
            "created": True
        })
