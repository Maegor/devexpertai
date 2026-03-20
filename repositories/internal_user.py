import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import InternalUser
from schemas.internal_user import InternalUserCreate, InternalUserUpdate


async def get_all(db: AsyncSession) -> list[InternalUser]:
    result = await db.execute(select(InternalUser))
    return result.scalars().all()


async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> InternalUser | None:
    result = await db.execute(select(InternalUser).where(InternalUser.id == user_id))
    return result.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> InternalUser | None:
    result = await db.execute(select(InternalUser).where(InternalUser.email == email))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, data: InternalUserCreate) -> InternalUser:
    user = InternalUser(**data.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update(
    db: AsyncSession, user: InternalUser, data: InternalUserUpdate
) -> InternalUser:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user: InternalUser) -> None:
    await db.delete(user)
    await db.commit()
