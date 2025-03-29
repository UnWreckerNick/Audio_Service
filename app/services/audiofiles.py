import aiofiles
from fastapi import UploadFile, Depends

from app.database.database import get_database_repo
from app.database.requests import RequestsRepo


class AudioFileService:
    def __init__(self, repo: RequestsRepo):
        self.repo = repo

    async def create_audio_file(self, file: UploadFile, name: str, user_id: int):
        file_path = f"uploads/{user_id}_{file.filename}"
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        new_file = await self.repo.audio_files.create_audio_file(name, file_path, user_id)
        return new_file

    async def get_audio_files(self, user_id):
        return await self.repo.audio_files.get_audio_files(user_id)

def get_audiofile_service(
        repo: RequestsRepo = Depends(get_database_repo)
) -> AudioFileService:
    return AudioFileService(repo=repo)