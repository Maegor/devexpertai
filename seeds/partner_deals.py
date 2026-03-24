import asyncio
import random
import sys
import os
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, func
from database import SessionLocal, engine, Base
from models import Partner, PartnerDeal, PartnerDealStatus

CURRENCIES = ["EUR", "USD", "GBP"]

DESCRIPTIONS = [
    "Cloud Migration",
    "SaaS Integration",
    "API Development",
    "Security Audit",
    "Data Analytics Platform",
    "Mobile App Development",
    "DevOps Transformation",
    "AI/ML Consulting",
    "Infrastructure Optimization",
    "Compliance Assessment",
    "E-commerce Platform Build",
    "CRM Implementation",
    "Microservices Refactor",
    "Performance Tuning",
    "Disaster Recovery Setup",
    "Identity & Access Management",
    "CI/CD Pipeline Design",
    "Data Warehouse Migration",
    "Blockchain PoC",
    "IoT Gateway Integration",
]

STATUS_POOL = [
    PartnerDealStatus.Proposal,
    PartnerDealStatus.PendingClosure,
    PartnerDealStatus.Closed,
    PartnerDealStatus.Active, PartnerDealStatus.Active, PartnerDealStatus.Active,
    PartnerDealStatus.Completed, PartnerDealStatus.Completed,
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

        count_result = await session.execute(select(func.count()).select_from(PartnerDeal))
        existing_count = count_result.scalar()

        if existing_count and existing_count > 0:
            print(f"Ya existen {existing_count} partner_deals en la BD. No se duplican.")
            return

        print(f"Partners disponibles: {len(partners)}")

        created = 0
        for i in range(50):
            partner = random.choice(partners)
            description = random.choice(DESCRIPTIONS)
            currency = random.choice(CURRENCIES)
            status = random.choice(STATUS_POOL)

            start_year = random.randint(2023, 2025)
            start_month_num = random.randint(1, 12)
            start_month = date(start_year, start_month_num, 1)

            duration = random.randint(1, 12)
            end_month_num = start_month_num + duration
            end_year = start_year + (end_month_num - 1) // 12
            end_month_num = ((end_month_num - 1) % 12) + 1
            end_month = date(end_year, end_month_num, 1)

            total_cost = Decimal(str(round(random.uniform(5000, 150000), 2)))

            deal = PartnerDeal(
                partner_id=partner.id,
                description=description,
                currency=currency,
                status=status,
                start_month=start_month,
                end_month=end_month,
                total_cost=total_cost,
            )
            session.add(deal)
            print(f"  creado: {description} | {partner.name} | {status.value} | {currency} {total_cost}")
            created += 1

        await session.commit()

    print(f"\nSeed completado: {created} partner_deals creados.")


if __name__ == "__main__":
    asyncio.run(run())
