
from fastapi import APIRouter, UploadFile
from fastapi.params import Depends

from app.schemas.audiofile import AudioFileSchema
from app.schemas.user import UserSchema
from app.services.audiofiles import AudioFileService, get_audiofile_service
from app.services.users import UserService

router = APIRouter(prefix="/audio")


@router.post("/upload", response_model=AudioFileSchema)
async def upload_audio(
        file: UploadFile,
        name: str,
        user: UserSchema = Depends(UserService.get_current_user),
        service: AudioFileService = Depends(get_audiofile_service)
):
    return await service.create_audio_file(file, name, user.id)


@router.get("/files", response_model=list[AudioFileSchema])
async def get_audio_files(
        user: UserSchema = Depends(UserService.get_current_user),
        service: AudioFileService = Depends(get_audiofile_service)
):
    return await service.get_audio_files(user.id)