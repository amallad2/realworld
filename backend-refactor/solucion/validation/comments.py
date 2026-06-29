from pydantic import BaseModel
from validation.base import ValidatedModel


class CreateCommentRequest(ValidatedModel):
    body: str
    article_id: str


class Comment(BaseModel):
    comment_id: str
    article_id: str
    body: str
    created_at: str


class CreateCommentResponse(BaseModel):
    comment: Comment


class GetCommentsResponse(BaseModel):
    comments: list[Comment]


class DeleteCommentResponse(BaseModel):
    message: str
