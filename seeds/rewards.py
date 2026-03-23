import asyncio
import random
import sys
import os
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, func
from database import SessionLocal, engine, Base
from models import Partner, Reward

CURRENCIES = ["EUR", "USD", "GBP"]
REWARD_TYPES = ["Cashback", "Discount", "Bonus", "Referral"]
PRODUCT_CODES = [f"PROD-{i:03d}" for i in range(1, 21)]


async def run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        partners_result = await session.execute(select(Partner))
        partners = partners_result.scalars().all()

        if not partners:
            print("ERROR: No hay partners. Ejecuta primero: .venv/bin/python seeds/partners.py")
            return

        # Verificar si ya existen rewards
        count_result = await session.execute(select(func.count()).select_from(Reward))
        existing_count = count_result.scalar()

        if existing_count and existing_count > 0:
            print(f"Ya existen {existing_count} rewards en la BD. No se duplican.")
            return

        print(f"Partners disponibles: {len(partners)}")

        created = 0
        for i in range(100):
            partner = random.choice(partners)
            year = random.randint(2023, 2025)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            transaction_date = datetime(year, month, day)

            product_code = random.choice(PRODUCT_CODES)
            customer_email = f"customer{random.randint(1, 500)}@example.com"
            amount = Decimal(str(round(random.uniform(10, 500), 2)))
            currency = random.choice(CURRENCIES)
            reward_type = random.choice(REWARD_TYPES)

            reward = Reward(
                partner_id=partner.id,
                transaction_date=transaction_date,
                product_code=product_code,
                customer_email=customer_email,
                amount=amount,
                currency=currency,
                reward_type=reward_type,
            )
            session.add(reward)
            print(f"  creado: {product_code} | {partner.name} | {reward_type} | {currency} {amount}")
            created += 1

        await session.commit()

    print(f"\nSeed completado: {created} rewards creados.")


if __name__ == "__main__":
    asyncio.run(run())
