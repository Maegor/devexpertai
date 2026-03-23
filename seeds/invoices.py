import asyncio
import calendar
import random
import sys
import os
from collections import defaultdict
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from database import SessionLocal, engine, Base
from models import Partner, BillingEntity, Invoice, InvoiceType, InvoiceStatus

CURRENCIES = ["EUR", "USD", "GBP", "CHF", "CAD"]

STATUS_POOL = [
    InvoiceStatus.Sent, InvoiceStatus.Sent,
    InvoiceStatus.Approved,
    InvoiceStatus.Paid, InvoiceStatus.Paid, InvoiceStatus.Paid,
    InvoiceStatus.UnderReview,
    InvoiceStatus.PendingPayment,
    InvoiceStatus.Rejected,
    InvoiceStatus.Cancelled,
]

REJECTION_REASONS = [
    "Missing supporting documentation",
    "Incorrect VAT rate applied",
    "Invoice amount does not match contract",
    "Duplicate invoice detected",
    "Unauthorized billing entity",
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

        be_result = await session.execute(select(BillingEntity))
        billing_entities = be_result.scalars().all()

        be_by_partner = defaultdict(list)
        for be in billing_entities:
            be_by_partner[be.partner_id].append(be)

        # Cargar referencias existentes para deduplicar
        existing_refs_result = await session.execute(select(Invoice.invoice_reference))
        existing_refs = set(existing_refs_result.scalars().all())

        print(f"Partners: {len(partners)}, BillingEntities: {len(billing_entities)}")
        print(f"Referencias existentes: {len(existing_refs)}")

        counter = 1
        created = 0
        skipped = 0

        for year in [2023, 2024, 2025]:
            for month in range(1, 13):
                if created >= 200:
                    break
                partner = random.choice(partners)
                be_list = be_by_partner.get(partner.id, [])
                billing_entity_id = random.choice(be_list).id if be_list else None

                invoice_reference = f"INV-{year}-{counter:04d}"
                counter += 1

                if invoice_reference in existing_refs:
                    print(f"  omitido (ya existe): {invoice_reference}")
                    skipped += 1
                    continue

                net_amount = Decimal(str(round(random.uniform(500, 50000), 2)))
                vat_pct = random.choice([0.0, 0.10, 0.21, 0.23])
                vat_amount = (net_amount * Decimal(str(vat_pct))).quantize(Decimal("0.01"))
                gross_total = net_amount + vat_amount
                tax_rate = f"{int(vat_pct * 100)}%" if vat_pct > 0 else "VAT Exempt"

                invoice_type = random.choice(list(InvoiceType))
                status = random.choice(STATUS_POOL)
                period_from = date(year, month, 1)
                period_to   = date(year, month, calendar.monthrange(year, month)[1])
                currency = random.choice(CURRENCIES)
                pdf_path = f"invoices/{year}/{invoice_reference}.pdf"

                rejection_reason = None
                scheduled_payment_date = None

                if status == InvoiceStatus.Rejected:
                    rejection_reason = random.choice(REJECTION_REASONS)
                elif status in (InvoiceStatus.PendingPayment, InvoiceStatus.Paid):
                    scheduled_payment_date = date(year, month, random.randint(1, 28))

                invoice = Invoice(
                    partner_id=partner.id,
                    billing_entity_id=billing_entity_id,
                    invoice_type=invoice_type,
                    invoice_reference=invoice_reference,
                    period_from=period_from,
                    period_to=period_to,
                    currency=currency,
                    net_amount=net_amount,
                    vat_amount=vat_amount,
                    gross_total=gross_total,
                    tax_rate=tax_rate,
                    pdf_path=pdf_path,
                    status=status,
                    rejection_reason=rejection_reason,
                    scheduled_payment_date=scheduled_payment_date,
                )
                session.add(invoice)
                existing_refs.add(invoice_reference)
                print(f"  creado: {invoice_reference} | {partner.name} | {status.value} | {currency} {gross_total}")
                created += 1

            if created >= 200:
                break

        # Completar hasta 200 si los ciclos año/mes no alcanzaron
        while created < 200:
            year = random.randint(2023, 2025)
            month = random.randint(1, 12)
            partner = random.choice(partners)
            be_list = be_by_partner.get(partner.id, [])
            billing_entity_id = random.choice(be_list).id if be_list else None

            invoice_reference = f"INV-{year}-{counter:04d}"
            counter += 1

            if invoice_reference in existing_refs:
                skipped += 1
                continue

            net_amount = Decimal(str(round(random.uniform(500, 50000), 2)))
            vat_pct = random.choice([0.0, 0.10, 0.21, 0.23])
            vat_amount = (net_amount * Decimal(str(vat_pct))).quantize(Decimal("0.01"))
            gross_total = net_amount + vat_amount
            tax_rate = f"{int(vat_pct * 100)}%" if vat_pct > 0 else "VAT Exempt"

            invoice_type = random.choice(list(InvoiceType))
            status = random.choice(STATUS_POOL)
            period_from = date(year, month, 1)
            period_to   = date(year, month, calendar.monthrange(year, month)[1])
            currency = random.choice(CURRENCIES)
            pdf_path = f"invoices/{year}/{invoice_reference}.pdf"

            rejection_reason = None
            scheduled_payment_date = None

            if status == InvoiceStatus.Rejected:
                rejection_reason = random.choice(REJECTION_REASONS)
            elif status in (InvoiceStatus.PendingPayment, InvoiceStatus.Paid):
                scheduled_payment_date = date(year, month, random.randint(1, 28))

            invoice = Invoice(
                partner_id=partner.id,
                billing_entity_id=billing_entity_id,
                invoice_type=invoice_type,
                invoice_reference=invoice_reference,
                period_from=period_from,
                period_to=period_to,
                currency=currency,
                net_amount=net_amount,
                vat_amount=vat_amount,
                gross_total=gross_total,
                tax_rate=tax_rate,
                pdf_path=pdf_path,
                status=status,
                rejection_reason=rejection_reason,
                scheduled_payment_date=scheduled_payment_date,
            )
            session.add(invoice)
            existing_refs.add(invoice_reference)
            print(f"  creado: {invoice_reference} | {partner.name} | {status.value} | {currency} {gross_total}")
            created += 1

        await session.commit()

    print(f"\nSeed completado: {created} creados, {skipped} omitidos.")


if __name__ == "__main__":
    asyncio.run(run())
