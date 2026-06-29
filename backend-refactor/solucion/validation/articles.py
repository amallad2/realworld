from pydantic import BaseModel
from validation.base import ValidatedModel


class CreateArticleRequest(ValidatedModel):
    title: str
    description: str
    body: str
    tagList: list[str]


class Article(BaseModel):
    title: str
    description: str
    body: str
    tag_list: list[str]
    created_at: str
    updated_at: str
    favorited: list[str]
    article_id: str
    slug: str
    author: object


class CreateArticleResponse(BaseModel):
    article: Article


class GetArticlesResponse(BaseModel):
    articles: list[Article]


class GetArticleResponse(BaseModel):
    article: Article


class UpdateArticleRequest(ValidatedModel):
    article_id: str
    fields: dict


class UpdateArticleResponse(BaseModel):
    message: str


class DeleteArticleRequest(ValidatedModel):
    article_id: str


class DeleteArticleResponse(BaseModel):
    message: str


class FavoriteArticleRequest(ValidatedModel):
    article_id: str


class FavoriteArticleResponse(BaseModel):
    message: str


class GetTagsResponse(BaseModel):
    tags: list[str]
