import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.internal_user import InternalUserCreate, InternalUserUpdate, InternalUserResponse
import repositories.internal_user as repo

router = APIRouter(prefix="/internal-users", tags=["internal-users"])


@router.get("/", response_model=list[InternalUserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    return await repo.get_all(db)


@router.get("/{user_id}", response_model=InternalUserResponse)
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("/", response_model=InternalUserResponse, status_code=201)
async def create_user(data: InternalUserCreate, db: AsyncSession = Depends(get_db)):
    existing = await repo.get_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    return await repo.create(db, data)


@router.patch("/{user_id}", response_model=InternalUserResponse)
async def update_user(
    user_id: uuid.UUID, data: InternalUserUpdate, db: AsyncSession = Depends(get_db)
):
    user = await repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await repo.update(db, user, data)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    user = await repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await repo.delete(db, user)
