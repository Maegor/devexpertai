import asyncio
import random
import uuid
import sys
import os
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import SessionLocal, engine, Base
from models import PartnerDeal, PartnerDealStatus

ACME_ID = uuid.UUID("be4341d9-d1c2-422c-8fb1-080a2e5e8b43")

DEALS = [
    ("Cloud Migration", "EUR", PartnerDealStatus.Active, date(2025, 1, 1), date(2025, 9, 1), Decimal("85000.00")),
    ("API Development", "USD", PartnerDealStatus.Completed, date(2024, 3, 1), date(2024, 12, 1), Decimal("42500.50")),
    ("Security Audit", "GBP", PartnerDealStatus.Proposal, date(2026, 4, 1), date(2026, 10, 1), Decimal("31200.00")),
    ("Data Analytics Platform", "EUR", PartnerDealStatus.PendingClosure, date(2025, 6, 1), date(2026, 2, 1), Decimal("120000.00")),
    ("DevOps Transformation", "USD", PartnerDealStatus.Closed, date(2025, 2, 1), date(2025, 8, 1), Decimal("67800.75")),
]


async def run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        created = 0
        for desc, currency, status, start, end, cost in DEALS:
            deal = PartnerDeal(
                partner_id=ACME_ID,
                description=desc,
                currency=currency,
                status=status,
                start_month=start,
                end_month=end,
                total_cost=cost,
            )
            session.add(deal)
            print(f"  creado: {desc} | {status.value} | {currency} {cost}")
            created += 1

        await session.commit()

    print(f"\nSeed completado: {created} partner_deals creados para Acme Corp.")


if __name__ == "__main__":
    asyncio.run(run())
