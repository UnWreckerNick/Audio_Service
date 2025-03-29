from pydantic import BaseModel


class UserBaseSchema(BaseModel):
    email: str

class UserCreateSchema(UserBaseSchema):
    yandex_id: str

class UserSchema(UserBaseSchema):
    id: int
    is_superuser: bool
