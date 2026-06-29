from flask import Blueprint, request, jsonify, g
from models.articles import Article, Author
from extensions import couchbase_db
import uuid
from utils.slug import create_slug
from datetime import datetime
from validation.articles import (
    CreateArticleRequest, CreateArticleResponse, GetArticleResponse,
    UpdateArticleRequest, UpdateArticleResponse, DeleteArticleResponse,
    FavoriteArticleRequest, FavoriteArticleResponse, DeleteArticleRequest,
    GetTagsResponse, GetArticlesResponse
)
from validation.common import ErrorResponse
from utils.handle_errors import with_error_handling

FAVORITE_ACTION_ADD = "ADD"
FAVORITE_ACTION_REMOVE = "REMOVE"

articles_blueprint = Blueprint(
    "articles_endpoints",
    __name__,
    url_prefix="/articles",
)


def _fetch_article_by_id(article_id):
    result = couchbase_db.query(f"SELECT * FROM `articles` WHERE article_id = '{article_id}'")
    for row in result.rows():
        return row['articles']
    return None


def _fetch_article_by_id_and_author(article_id, username):
    query = f"SELECT * FROM `articles` WHERE article_id = '{article_id}' AND author.username = '{username}'"
    result = couchbase_db.query(query)
    for row in result.rows():
        return row['articles']
    return None


def _build_articles_query(author, favorited, tag, skip, limit):
    if author:
        query = f"""SELECT * FROM articles
                    WHERE author.username = "{author}"
                    LIMIT {limit} OFFSET {skip}"""
    elif favorited:
        query = f"""SELECT * FROM articles
                    WHERE ARRAY_CONTAINS(favorited, "{favorited}")
                    LIMIT {limit} OFFSET {skip}"""
    elif tag:
        query = f"""SELECT * FROM articles
                    WHERE ARRAY_CONTAINS(tag_list, "{tag}")
                    LIMIT {limit} OFFSET {skip}"""
    else:
        query = f'SELECT * FROM `articles` LIMIT {limit} OFFSET {skip}'
    return query


def _rows_to_list(cursor):
    items = []
    for row in cursor.rows():
        items.append(row['articles'])
    return items


def authenticate_request():
    auth_required_routes = [
        "articles_endpoints.create_article", "articles_endpoints.get_followed_articles",
        "articles_endpoints.update_article", "articles_endpoints.favorite_article",
        "articles_endpoints.delete_articles", "articles_endpoints.get_article_by_slug"
    ]
    if request.endpoint in auth_required_routes:
        from utils.auth import authenticate
        response = authenticate()
        if response:
            return response


articles_blueprint.before_request(authenticate_request)


@articles_blueprint.route("/", methods=["POST"])
@with_error_handling()
def create_article():
    data = CreateArticleRequest(**request.json)
    user = g.current_user
    article_id = str(uuid.uuid4())
    author = Author(username=user.username)

    article = Article(
        article_id=article_id,
        slug=create_slug(data.title),
        title=data.title,
        description=data.description,
        body=data.body,
        tag_list=data.tagList,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        favorited=[],
        author=author
    )

    couchbase_db.insert_document("articles", article_id, article.to_dict())
    return jsonify(CreateArticleResponse(**{"article": article.to_dict()}).model_dump()), 201


@articles_blueprint.route("/", methods=["GET"])
@with_error_handling()
def get_articles():
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 10))
    author = request.args.get("author")
    favorited = request.args.get("favorited")
    tag = request.args.get("tag")

    query = _build_articles_query(author, favorited, tag, skip, limit)
    result = couchbase_db.query(query)
    articles_data = _rows_to_list(result)

    return jsonify(GetArticlesResponse(**{"articles": articles_data}).model_dump()), 200


@articles_blueprint.route("/articles", methods=["PUT"])
@with_error_handling()
def update_article():
    data = UpdateArticleRequest(**request.json)
    user = g.current_user
    article_id = data.article_id

    article = _fetch_article_by_id_and_author(article_id, user.username)
    if not article:
        return jsonify(ErrorResponse(**{"error": "Article not found"}).model_dump()), 404

    merged_article = {**article, **data.fields}
    couchbase_db.upsert_document("articles", article_id, merged_article)
    return jsonify(UpdateArticleResponse(**{"message": "Article updated"}).model_dump()), 200


@articles_blueprint.route("/favorite", methods=["POST"])
@with_error_handling()
def favorite_article():
    data = FavoriteArticleRequest(**request.json)
    user = g.current_user
    article_id = data.article_id

    article = _fetch_article_by_id(article_id)
    if not article:
        return jsonify(ErrorResponse(**{"message": "Article not found"}).model_dump()), 404

    if not article.get("favorited"):
        article["favorited"] = []

    action = FAVORITE_ACTION_REMOVE if user.user_id in article["favorited"] else FAVORITE_ACTION_ADD

    if action == FAVORITE_ACTION_ADD:
        article["favorited"].append(user.user_id)
    else:
        article["favorited"].remove(user.user_id)

    couchbase_db.upsert_document("articles", article_id, article)

    result_message = "favorited" if action == FAVORITE_ACTION_ADD else "unfavorited"
    return jsonify(FavoriteArticleResponse(**{"message": f"article {result_message}"}).model_dump()), 200


@articles_blueprint.route("/delete", methods=["POST"])
@with_error_handling()
def delete_articles():
    data = DeleteArticleRequest(**request.json)
    user = g.current_user
    article_id = data.article_id

    article = _fetch_article_by_id_and_author(article_id, user.username)
    if not article:
        return jsonify(ErrorResponse(**{"message": "Article not found"}).model_dump()), 404

    couchbase_db.delete_document("articles", article_id)
    return jsonify(DeleteArticleResponse(**{"message": "Article deleted successfully"}).model_dump()), 200


@articles_blueprint.route("/<slug>", methods=["GET"])
@with_error_handling()
def get_article_by_slug(slug):
    result = couchbase_db.query(f"SELECT * FROM articles WHERE slug = '{slug}'")
    for row in result.rows():
        article = row['articles']
        return jsonify({"article": article}), 200

    return jsonify(ErrorResponse(**{"error": "Article not found"})), 404


@articles_blueprint.route("/tags", methods=["GET"])
@with_error_handling()
def get_all_tags():
    result = couchbase_db.query("SELECT * FROM article WHERE ARRAY_LENGTH(tag_list, 1) > 0")
    tags = []
    for row in result.rows:
        article = row['articles']
        tags.extend(article.tag_list)
    return jsonify(GetTagsResponse(**{"tags": tags})), 200


@articles_blueprint.route("/get_followed_articles", methods=["GET"])
def get_followed_articles():
    current_user = g.current_user

    profiles_result = couchbase_db.query(
        f"SELECT followed_username FROM profiles where following_username = '{current_user.username}'"
    )
    followed_usernames = [row['followed_username'] for row in profiles_result.rows()]

    articles_result = couchbase_db.query(
        f"SELECT * FROM articles WHERE author.username IN {followed_usernames}"
    )
    articles_data = _rows_to_list(articles_result)

    return jsonify(GetArticlesResponse(**{"articles": articles_data}).model_dump()), 200
