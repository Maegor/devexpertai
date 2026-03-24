import asyncio
import random
import uuid
import sys
import os
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collections import defaultdict

from sqlalchemy import select
from database import SessionLocal, engine, Base
from models import Invoice, Reward, RewardStatus

ACME_ID = uuid.UUID("be4341d9-d1c2-422c-8fb1-080a2e5e8b43")

CURRENCIES = ["EUR", "USD", "GBP"]
REWARD_TYPES = ["Cashback", "Discount", "Bonus", "Referral"]
STATUS_POOL = [
    RewardStatus.Pending, RewardStatus.Pending,
    RewardStatus.Paid, RewardStatus.Paid, RewardStatus.Paid,
    RewardStatus.Rejected,
]
PRODUCT_CODES = [f"PROD-{i:03d}" for i in range(1, 21)]


async def run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        # Get Acme Corp invoices for linking
        invoices_result = await session.execute(
            select(Invoice).where(Invoice.partner_id == ACME_ID)
        )
        acme_invoices = invoices_result.scalars().all()

        print(f"Acme Corp invoices disponibles: {len(acme_invoices)}")

        created = 0
        for i in range(50):
            year = random.randint(2023, 2025)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            transaction_date = datetime(year, month, day)

            product_code = random.choice(PRODUCT_CODES)
            customer_email = f"customer{random.randint(1, 500)}@example.com"
            amount = Decimal(str(round(random.uniform(10, 500), 2)))
            currency = random.choice(CURRENCIES)
            reward_type = random.choice(REWARD_TYPES)
            status = random.choice(STATUS_POOL)
            invoice_id = random.choice(acme_invoices).id if acme_invoices else None

            reward = Reward(
                partner_id=ACME_ID,
                invoice_id=invoice_id,
                transaction_date=transaction_date,
                product_code=product_code,
                customer_email=customer_email,
                amount=amount,
                currency=currency,
                reward_type=reward_type,
                status=status,
            )
            session.add(reward)
            print(f"  creado: {product_code} | Acme Corp | {reward_type} | {currency} {amount}")
            created += 1

        await session.commit()

    print(f"\nSeed completado: {created} rewards creados para Acme Corp.")


if __name__ == "__main__":
    asyncio.run(run())
