import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models import PartnerCampaign
from schemas.partner_campaign import PartnerCampaignCreate, PartnerCampaignUpdate


async def get_all(db: AsyncSession) -> list[PartnerCampaign]:
    result = await db.execute(select(PartnerCampaign).options(selectinload(PartnerCampaign.campaign)))
    return result.scalars().all()


async def get_by_id(db: AsyncSession, pc_id: uuid.UUID) -> PartnerCampaign | None:
    result = await db.execute(
        select(PartnerCampaign)
        .options(selectinload(PartnerCampaign.campaign))
        .where(PartnerCampaign.id == pc_id)
    )
    return result.scalar_one_or_none()


async def get_by_partner(db: AsyncSession, partner_id: uuid.UUID) -> list[PartnerCampaign]:
    result = await db.execute(
        select(PartnerCampaign)
        .options(selectinload(PartnerCampaign.campaign))
        .where(PartnerCampaign.partner_id == partner_id)
    )
    return result.scalars().all()


async def get_by_campaign(db: AsyncSession, campaign_id: uuid.UUID) -> list[PartnerCampaign]:
    result = await db.execute(
        select(PartnerCampaign)
        .options(selectinload(PartnerCampaign.campaign))
        .where(PartnerCampaign.campaign_id == campaign_id)
    )
    return result.scalars().all()


async def create(db: AsyncSession, data: PartnerCampaignCreate) -> PartnerCampaign:
    pc = PartnerCampaign(**data.model_dump())
    db.add(pc)
    await db.commit()
    await db.refresh(pc)
    return pc


async def update(db: AsyncSession, pc: PartnerCampaign, data: PartnerCampaignUpdate) -> PartnerCampaign:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(pc, field, value)
    await db.commit()
    await db.refresh(pc)
    return pc


async def delete(db: AsyncSession, pc: PartnerCampaign) -> None:
    await db.delete(pc)
    await db.commit()
