from flask import g, request, jsonify
from models.users import User
import jwt
import os


def authenticate():
    SECRET_KEY = os.getenv("SECRET_KEY")
    token = request.headers.get('Authorization')
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            g.current_user = User.get_user_by_id(user_id)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    else:
        return jsonify({"error": "Authorization token required"}), 401
