from datetime import datetime
from models.articles import Author


class Comment:
    def __init__(self, comment_id: int, article_id: int, body: str,
                 created_at: datetime, author: Author):
        self.comment_id = comment_id
        self.article_id = article_id
        self.body = body
        self.created_at = created_at
        self.author = author

    def to_dict(self):
        return {
            "comment_id": self.comment_id,
            "article_id": self.article_id,
            "body": self.body,
            "created_at": self.created_at.isoformat(),
            "author": self.author.to_dict()
        }
