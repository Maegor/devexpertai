import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import PartnerDeal
from schemas.partner_deal import PartnerDealCreate, PartnerDealUpdate


async def get_all(db: AsyncSession) -> list[PartnerDeal]:
    result = await db.execute(select(PartnerDeal))
    return result.scalars().all()


async def get_by_id(db: AsyncSession, deal_id: uuid.UUID) -> PartnerDeal | None:
    result = await db.execute(select(PartnerDeal).where(PartnerDeal.id == deal_id))
    return result.scalar_one_or_none()


async def get_by_partner(db: AsyncSession, partner_id: uuid.UUID) -> list[PartnerDeal]:
    result = await db.execute(
        select(PartnerDeal).where(PartnerDeal.partner_id == partner_id)
    )
    return result.scalars().all()


async def create(db: AsyncSession, data: PartnerDealCreate) -> PartnerDeal:
    deal = PartnerDeal(**data.model_dump())
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


async def update(db: AsyncSession, deal: PartnerDeal, data: PartnerDealUpdate) -> PartnerDeal:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(deal, field, value)
    await db.commit()
    await db.refresh(deal)
    return deal


async def delete(db: AsyncSession, deal: PartnerDeal) -> None:
    await db.delete(deal)
    await db.commit()
