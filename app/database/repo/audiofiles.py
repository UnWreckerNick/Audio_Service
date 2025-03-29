from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audiofiles import AudioFile
from app.database.repo.base import BaseRepo


class AudioFileRepo(BaseRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AudioFile)

    async def create_audio_file(self, name: str, file_path: str,  user_id: int):
        new_file = AudioFile(name=name, file_path=file_path, user_id=user_id)
        self.session.add(new_file)
        await self.session.commit()
        await self.session.refresh(new_file)
        return new_file

    async def get_audio_files(self, user_id: int):
        stmt = select(AudioFile).filter(AudioFile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()