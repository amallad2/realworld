from flask import Blueprint, request, jsonify, g
from models.profiles import Profiles
from extensions import couchbase_db
import uuid
from datetime import datetime
from validation.profiles import FollowUnfollowRequest, FollowUnfollowResponse
from validation.common import ErrorResponse
from utils.handle_errors import with_error_handling

profiles_blueprint = Blueprint(
    "profiles_endpoints",
    __name__,
    url_prefix="/profiles",
)


def authenticate_request():
    from utils.auth import authenticate
    response = authenticate()
    if response:
        return response


profiles_blueprint.before_request(authenticate_request)


def _fetch_user_by_username(username):
    result = couchbase_db.query(f"SELECT * FROM users WHERE username = '{username}'")
    for row in result.rows():
        return row["users"]
    return None


def _fetch_profile(following_username, followed_username):
    query = f"SELECT * FROM profiles where following_username = '{following_username}' and followed_username = '{followed_username}'"
    result = couchbase_db.query(query)
    for row in result.rows():
        return row["profiles"]
    return None


def _handle_follow(current_user, followed_username, profile_id):
    existing_profile = _fetch_profile(current_user.username, followed_username)
    if existing_profile:
        return jsonify(ErrorResponse(**{"error": "already following the user"}).model_dump()), 400

    profile = Profiles(
        id=profile_id,
        following_username=current_user.username,
        followed_username=followed_username,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    couchbase_db.insert_document("profiles", profile_id, profile.to_dict())
    return jsonify(FollowUnfollowResponse(**{"message": "profile followed successfully!"}).model_dump()), 200


def _handle_unfollow(current_user, followed_username):
    existing_profile = _fetch_profile(current_user.username, followed_username)
    if not existing_profile:
        return jsonify(ErrorResponse(**{"error": "already not following the profile"}).model_dump()), 400

    couchbase_db.delete_document("profiles", existing_profile['id'])
    return jsonify(FollowUnfollowResponse(**{"message": "profile unfollowed successfully!"}).model_dump()), 200


@profiles_blueprint.route("/", methods=["POST"])
@with_error_handling()
def follow_unfollow():
    data = FollowUnfollowRequest(**request.json)
    current_user = g.current_user
    action = data.action
    followed_username = data.followed_username

    if action not in ("FOLLOW", "UNFOLLOW"):
        return jsonify(ErrorResponse(**{"error": "action doesn't exist"}).model_dump()), 400

    followed_user = _fetch_user_by_username(followed_username)
    if not followed_user:
        return jsonify(ErrorResponse(**{"error": "followed user doesn't exist"}).model_dump()), 400

    if current_user.username == followed_user['username']:
        return jsonify(ErrorResponse(**{"error": "following and followed user cannot be same"}).model_dump()), 400

    profile_id = str(uuid.uuid4())

    if action == "FOLLOW":
        return _handle_follow(current_user, followed_username, profile_id)
    else:
        return _handle_unfollow(current_user, followed_username)
