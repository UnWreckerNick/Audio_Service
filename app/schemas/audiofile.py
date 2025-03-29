from pydantic import BaseModel


class AudioFileBaseSchema(BaseModel):
    name: str

class AudioFileSchema(AudioFileBaseSchema):
    id: int
    file_path: str
    user_id: int

class TokenSchema(BaseModel):
    access_token: str
    token_type: str