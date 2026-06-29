from pydantic import BaseModel


class FollowUnfollowRequest(BaseModel):
    action: str
    followed_username: str


class FollowUnfollowResponse(BaseModel):
    message: str
