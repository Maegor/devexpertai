import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Partner
from schemas.partner import PartnerCreate, PartnerUpdate


async def get_all(db: AsyncSession) -> list[Partner]:
    result = await db.execute(select(Partner))
    return result.scalars().all()


async def get_by_sales_rep(db: AsyncSession, sales_rep_id: uuid.UUID) -> list[Partner]:
    result = await db.execute(
        select(Partner).where(Partner.assigned_sales_rep_id == sales_rep_id)
    )
    return result.scalars().all()


async def get_by_id(db: AsyncSession, partner_id: uuid.UUID) -> Partner | None:
    result = await db.execute(select(Partner).where(Partner.id == partner_id))
    return result.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> Partner | None:
    result = await db.execute(select(Partner).where(Partner.email == email))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, data: PartnerCreate) -> Partner:
    partner = Partner(**data.model_dump())
    db.add(partner)
    await db.commit()
    await db.refresh(partner)
    return partner


async def update(db: AsyncSession, partner: Partner, data: PartnerUpdate) -> Partner:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(partner, field, value)
    await db.commit()
    await db.refresh(partner)
    return partner


async def delete(db: AsyncSession, partner: Partner) -> None:
    await db.delete(partner)
    await db.commit()
