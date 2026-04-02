import asyncio
import random
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, func
from database import SessionLocal, engine, Base
from models import Partner, Campaign, PartnerCampaign, CampaignStatus, PartnerCampaignStatus

CAMPAIGN_DATA = [
    ("Black Friday 2024",      "Exclusive Black Friday promotion",       "BF2024",    CampaignStatus.finished),
    ("New Year Boost",         "New Year trading incentive campaign",    "NY2025",    CampaignStatus.finished),
    ("Spring Launch",          "Spring season partner activation",       "SPRING25",  CampaignStatus.active),
    ("Summer Referral",        "Summer referral bonus programme",        "SUMREF25",  CampaignStatus.active),
    ("Q2 Growth Drive",        "Q2 partner growth incentive",            "Q2GROW25",  CampaignStatus.active),
    ("Elite Partner Club",     "Exclusive programme for top partners",   "ELITE25",   CampaignStatus.active),
    ("Crypto Launch",          "Crypto product launch promotion",        "CRYPTO25",  CampaignStatus.pending),
    ("Autumn Activation",      "Autumn season partner campaign",         "AUTUMN25",  CampaignStatus.pending),
    ("Year-End Celebration",   "Year-end rewards for active partners",   "YEAREND25", CampaignStatus.cancelled),
    ("Global Expansion",       "International market expansion drive",   "GLOBAL25",  CampaignStatus.pending),
]

STATUS_POOL = [
    PartnerCampaignStatus.active, PartnerCampaignStatus.active, PartnerCampaignStatus.active,
    PartnerCampaignStatus.pending, PartnerCampaignStatus.pending,
    PartnerCampaignStatus.finished,
    PartnerCampaignStatus.cancelled,
]


async def run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        partners_result = await session.execute(select(Partner))
        partners = partners_result.scalars().all()

        if not partners:
            print("ERROR: No hay partners. Ejecuta primero: .venv/bin/python seeds/partners.py")
            return

        count_result = await session.execute(select(func.count()).select_from(Campaign))
        existing_count = count_result.scalar()

        if existing_count and existing_count > 0:
            print(f"Ya existen {existing_count} campaigns en la BD. No se duplican.")
            return

        print(f"Partners disponibles: {len(partners)}")

        campaigns = []
        for name, description, coupon, status in CAMPAIGN_DATA:
            year = 2025
            start_month = random.randint(1, 6)
            end_month = start_month + random.randint(1, 4)
            end_year = year + (end_month - 1) // 12
            end_month = ((end_month - 1) % 12) + 1

            campaign = Campaign(
                name=name,
                description=description,
                coupon=coupon,
                status=status,
                start_date=datetime(year, start_month, 1),
                end_date=datetime(end_year, end_month, 1),
            )
            session.add(campaign)
            campaigns.append(campaign)
            print(f"  campaña: {name} | {status.value} | {coupon}")

        await session.flush()

        pc_created = 0
        for campaign in campaigns:
            num_partners = random.randint(1, min(3, len(partners)))
            selected = random.sample(partners, num_partners)
            for partner in selected:
                status = random.choice(STATUS_POOL)
                coupon = f"{campaign.coupon}-{partner.name[:4].upper()}" if random.random() > 0.5 else None
                pc = PartnerCampaign(
                    partner_id=partner.id,
                    campaign_id=campaign.id,
                    coupon=coupon,
                    status=status,
                    start_date=campaign.start_date,
                    end_date=campaign.end_date,
                )
                session.add(pc)
                print(f"    partner-campaign: {partner.name} → {campaign.name} | {status.value}")
                pc_created += 1

        await session.commit()

    print(f"\nSeed completado: {len(campaigns)} campaigns y {pc_created} partner_campaigns creados.")


if __name__ == "__main__":
    asyncio.run(run())
