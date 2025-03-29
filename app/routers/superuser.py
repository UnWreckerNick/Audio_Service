from typing import Any

from fastapi import APIRouter, HTTPException, Body
from fastapi.params import Depends

from app.schemas.user import UserSchema, UserUpdateSchema
from app.services.users import UserService, get_user_service, get_superuser_dependency

router = APIRouter(prefix="/superuser", tags=["Superuser"], dependencies=[Depends(get_superuser_dependency)])


# Superuser endpoints
@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
        user_id: int,
        service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
        user_id: int,
        user_data: UserUpdateSchema,
        service: UserService = Depends(get_user_service)
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
    return await service.update_user(user_id, update_data)


@router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        service: UserService = Depends(get_user_service)
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await service.delete_user(user.id)
    return {"message": "User deleted"}