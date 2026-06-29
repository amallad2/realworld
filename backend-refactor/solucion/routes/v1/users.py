from flask import Blueprint, request, jsonify, g
from extensions import couchbase_db
from models.users import User
from utils.jwt import generate_token
from validation.auth import RegisterRequest, RegisterResponse, LoginRequest, CurrentResponse
from validation.common import ErrorResponse
from utils.handle_errors import with_error_handling
import bcrypt
import uuid

users_blueprint = Blueprint(
    "users_endpoints",
    __name__,
    url_prefix="/users",
)


def authenticate_request():
    auth_required_routes = ["users_endpoints.get_current_user"]
    if request.endpoint in auth_required_routes:
        from utils.auth import authenticate
        response = authenticate()
        if response:
            return response


users_blueprint.before_request(authenticate_request)


def _build_user_response(user, token):
    return {
        "username": user.username,
        "email": user.email,
        "token": token
    }


@users_blueprint.route("/", methods=["POST"])
@with_error_handling()
def create_user():
    data = RegisterRequest(**request.json)
    existing_user = User.get_by_username(data.username)
    existing_user_email = User.get_by_email(data.email)

    if existing_user:
        return jsonify(ErrorResponse(**{"error": "Username already exists"}).model_dump()), 400
    if existing_user_email:
        return jsonify(ErrorResponse(**{"error": "Email already exists"}).model_dump()), 400

    user_id = str(uuid.uuid4())
    user = User(user_id, data.username, data.email, data.password)
    user.save()

    token = generate_token(user_id)
    response_data = RegisterResponse(**{"user": _build_user_response(user, token)})
    return jsonify(response_data.model_dump()), 201


@users_blueprint.route("/login", methods=["POST"])
@with_error_handling()
def login_user():
    data = LoginRequest(**request.json)
    user = User.get_by_email(data.email)

    if not user:
        return jsonify(ErrorResponse(**{"error": "email or password is incorrect"}).model_dump()), 400

    if not bcrypt.checkpw(data.password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify(ErrorResponse(**{"error": "Invalid password"}).model_dump()), 401

    token = generate_token(user.user_id)
    response_data = RegisterResponse(**{"user": _build_user_response(user, token)})
    return jsonify(response_data.model_dump()), 200


@users_blueprint.route("/get-current-user", methods=["GET"])
@with_error_handling()
def get_current_user():
    user = g.current_user
    if not user:
        return jsonify(ErrorResponse(**{"error": "Not logged in"}).model_dump()), 401

    return jsonify(
        CurrentResponse(**{
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email
            }
        }).model_dump()
    ), 200


def get_all_users():
    return {"users": []}
