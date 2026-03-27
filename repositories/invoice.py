import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Invoice
from schemas.invoice import InvoiceCreate, InvoiceUpdate


async def get_all(db: AsyncSession) -> list[Invoice]:
    result = await db.execute(select(Invoice))
    return result.scalars().all()


async def get_by_id(db: AsyncSession, invoice_id: uuid.UUID) -> Invoice | None:
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    return result.scalar_one_or_none()


async def get_by_partner(db: AsyncSession, partner_id: uuid.UUID) -> list[Invoice]:
    result = await db.execute(
        select(Invoice).where(Invoice.partner_id == partner_id)
    )
    return result.scalars().all()


async def get_by_partners(db: AsyncSession, partner_ids: list[uuid.UUID]) -> list[Invoice]:
    if not partner_ids:
        return []
    result = await db.execute(
        select(Invoice).where(Invoice.partner_id.in_(partner_ids))
    )
    return result.scalars().all()


async def create(db: AsyncSession, data: InvoiceCreate) -> Invoice:
    invoice = Invoice(**data.model_dump())
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def update(db: AsyncSession, invoice: Invoice, data: InvoiceUpdate) -> Invoice:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(invoice, field, value)
    await db.commit()
    await db.refresh(invoice)
    return invoice


async def delete(db: AsyncSession, invoice: Invoice) -> None:
    await db.delete(invoice)
    await db.commit()
