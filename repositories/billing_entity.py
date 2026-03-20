import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import BillingEntity
from schemas.billing_entity import BillingEntityCreate, BillingEntityUpdate


async def get_all(db: AsyncSession) -> list[BillingEntity]:
    result = await db.execute(select(BillingEntity))
    return result.scalars().all()


async def get_by_id(db: AsyncSession, entity_id: uuid.UUID) -> BillingEntity | None:
    result = await db.execute(select(BillingEntity).where(BillingEntity.id == entity_id))
    return result.scalar_one_or_none()


async def get_by_partner(db: AsyncSession, partner_id: uuid.UUID) -> list[BillingEntity]:
    result = await db.execute(
        select(BillingEntity).where(BillingEntity.partner_id == partner_id)
    )
    return result.scalars().all()


async def create(db: AsyncSession, data: BillingEntityCreate) -> BillingEntity:
    entity = BillingEntity(**data.model_dump())
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


async def update(db: AsyncSession, entity: BillingEntity, data: BillingEntityUpdate) -> BillingEntity:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    await db.commit()
    await db.refresh(entity)
    return entity


async def delete(db: AsyncSession, entity: BillingEntity) -> None:
    await db.delete(entity)
    await db.commit()
