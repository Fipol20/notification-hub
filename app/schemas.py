import datetime as dt

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class NotificationCreate(BaseModel):
    message: str


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    message: str
    status: str
    created_at: dt.datetime
