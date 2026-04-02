import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Campaign
from schemas.campaign import CampaignCreate, CampaignUpdate


async def get_all(db: AsyncSession) -> list[Campaign]:
    result = await db.execute(select(Campaign))
    return result.scalars().all()


async def get_by_id(db: AsyncSession, campaign_id: uuid.UUID) -> Campaign | None:
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, data: CampaignCreate) -> Campaign:
    campaign = Campaign(**data.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def update(db: AsyncSession, campaign: Campaign, data: CampaignUpdate) -> Campaign:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def delete(db: AsyncSession, campaign: Campaign) -> None:
    await db.delete(campaign)
    await db.commit()
