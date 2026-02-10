"""Minimal user registration API for demo purposes."""

from datetime import datetime
import os
import re

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

db = SQLAlchemy(app)


class User(db.Model):
    """User model for registration demo."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.String(30), nullable=False, default="user")


def generate_confirmation_token(user_id):
    """Generate a confirmation token for a user id."""
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return serializer.dumps({"user_id": user_id})


def send_confirmation_email(email, token):
    """Placeholder for sending confirmation emails."""
    app.logger.info("Confirmation email to %s with token %s", email, token)


@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.get_json(silent=True) or {}

    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'error': 'Missing required field',
                'message': f'{field} is required'
            }), 400

    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'error': 'Username taken',
            'message': 'Username is already in use'
        }), 409

    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'error': 'Email exists',
            'message': 'An account with this email already exists'
        }), 409

    # Validate email format
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", data['email']):
        return jsonify({
            'error': 'Invalid email',
            'message': 'Please provide a valid email address'
        }), 400

    # Validate password strength
    if len(data['password']) < 8:
        return jsonify({
            'error': 'Weak password',
            'message': 'Password must be at least 8 characters long'
        }), 400

    # Create new user
    try:
        # Hash password
        password_hash = generate_password_hash(data['password'])

        # Create user object
        new_user = User(
            username=data['username'],
            email=data['email'].lower(),
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            role='user'
        )

        # Add user to database
        db.session.add(new_user)
        db.session.commit()

        # Generate confirmation token
        confirmation_token = generate_confirmation_token(new_user.id)

        # Send confirmation email
        try:
            send_confirmation_email(new_user.email, confirmation_token)
        except Exception as e:
            # Log email error but continue
            app.logger.error(f"Failed to send confirmation email: {str(e)}")

        # Create response without password
        user_data = {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'created_at': new_user.created_at.isoformat(),
            'role': new_user.role
        }

        return jsonify({
            'message': 'User registered successfully',
            'user': user_data
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error registering user: {str(e)}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to register user'
        }), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)