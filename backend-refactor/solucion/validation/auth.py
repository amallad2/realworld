from pydantic import BaseModel
from validation.base import ValidatedModel


class RegisterRequest(ValidatedModel):
    username: str
    password: str
    email: str


class NestedRegisterResponse(BaseModel):
    username: str
    email: str
    token: str


class RegisterResponse(BaseModel):
    user: NestedRegisterResponse


class NestedCurrentResponse(BaseModel):
    user_id: str
    username: str
    email: str


class CurrentResponse(BaseModel):
    user: NestedCurrentResponse


class LoginRequest(ValidatedModel):
    email: str
    password: str


class CurrentUserRequest(ValidatedModel):
    email: str
    password: str
