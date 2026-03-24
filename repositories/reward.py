import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Reward
from schemas.reward import RewardCreate, RewardUpdate


async def get_all(db: AsyncSession) -> list[Reward]:
    result = await db.execute(select(Reward))
    return result.scalars().all()


async def get_by_id(db: AsyncSession, reward_id: uuid.UUID) -> Reward | None:
    result = await db.execute(select(Reward).where(Reward.id == reward_id))
    return result.scalar_one_or_none()


async def get_by_invoice(db: AsyncSession, invoice_id: uuid.UUID) -> list[Reward]:
    result = await db.execute(
        select(Reward).where(Reward.invoice_id == invoice_id)
    )
    return result.scalars().all()


async def get_by_partner(db: AsyncSession, partner_id: uuid.UUID) -> list[Reward]:
    result = await db.execute(
        select(Reward).where(Reward.partner_id == partner_id)
    )
    return result.scalars().all()


async def create(db: AsyncSession, data: RewardCreate) -> Reward:
    reward = Reward(**data.model_dump())
    db.add(reward)
    await db.commit()
    await db.refresh(reward)
    return reward


async def update(db: AsyncSession, reward: Reward, data: RewardUpdate) -> Reward:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(reward, field, value)
    await db.commit()
    await db.refresh(reward)
    return reward


async def delete(db: AsyncSession, reward: Reward) -> None:
    await db.delete(reward)
    await db.commit()
