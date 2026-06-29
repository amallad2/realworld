from flask import Blueprint, request, jsonify, g
from models.articles import Author
from models.comments import Comment
from extensions import couchbase_db
import uuid
from datetime import datetime
from couchbase.exceptions import DocumentNotFoundException, CouchbaseException
from validation.common import ErrorResponse
from validation.comments import CreateCommentRequest, CreateCommentResponse, GetCommentsResponse, DeleteCommentResponse
from utils.handle_errors import with_error_handling

comments_blueprint = Blueprint(
    "comments_endpoints",
    __name__,
    url_prefix="/comments",
)


def authenticate_request():
    auth_required_routes = [
        "comments_endpoints.create_comment",
        "comments_endpoints.get_comments",
        "comments_endpoints.delete_comment"
    ]
    if request.endpoint in auth_required_routes:
        from utils.auth import authenticate
        response = authenticate()
        if response:
            return response


comments_blueprint.before_request(authenticate_request)


@comments_blueprint.route("/", methods=["POST"])
@with_error_handling()
def create_comment():
    data = CreateCommentRequest(**request.json)
    user = g.current_user
    comment_id = str(uuid.uuid4())

    author = Author(username=user.username)

    try:
        couchbase_db.get_document("articles", data.article_id)
    except DocumentNotFoundException:
        return jsonify(ErrorResponse(**{"message": "Article not found"}).model_dump()), 404
    except CouchbaseException:
        return jsonify(ErrorResponse(**{"message": "internal server error"}).model_dump()), 500

    comment = Comment(
        comment_id=comment_id,
        article_id=data.article_id,
        body=data.body,
        created_at=datetime.utcnow(),
        author=author
    )

    couchbase_db.insert_document("comments", comment_id, comment.to_dict())
    return jsonify(CreateCommentResponse(**{"comment": comment.to_dict()}).model_dump()), 201


@comments_blueprint.route("/<article_id>", methods=["GET"])
@with_error_handling()
def get_comments(article_id):
    skip = request.args.get("skip", default=0, type=int)
    limit = request.args.get("limit", default=10, type=int)

    result = couchbase_db.query(f"""
        SELECT * FROM comments
        WHERE article_id = "{article_id}"
        LIMIT {limit} OFFSET {skip}
    """)

    comments_data = [row['comments'] for row in result.rows()]

    return jsonify(GetCommentsResponse(**{"comments": comments_data}).model_dump()), 200


@comments_blueprint.route("/<comment_id>", methods=["DELETE"])
@with_error_handling()
def delete_comment(comment_id):
    try:
        comment_doc = couchbase_db.get_document("comments", comment_id)
        comment = comment_doc.value
        user = g.current_user

        if comment["author"]["username"] != user.username:
            return jsonify(ErrorResponse(**{"error": "You don't have permission to delete this comment"}).model_dump()), 403

        couchbase_db.delete_document("comments", comment_id)
        return jsonify(DeleteCommentResponse(**{"message": "Comment deleted successfully"}).model_dump()), 200

    except DocumentNotFoundException:
        return jsonify(ErrorResponse(**{"message": "Comment not found"}).model_dump()), 404
