from pydantic import BaseModel


class UserBaseSchema(BaseModel):
    email: str

class UserCreateSchema(UserBaseSchema):
    yandex_id: str

class UserSchema(UserBaseSchema):
    id: int
    is_superuser: bool

class UserUpdateSchema(BaseModel):
    email: str | None = None
    is_superuser: bool | None = None

    class Config:
        extra = "forbid"