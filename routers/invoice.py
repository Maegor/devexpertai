import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories import invoice as invoice_repo
from schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/", response_model=list[InvoiceResponse])
async def list_invoices(db: AsyncSession = Depends(get_db)):
    return await invoice_repo.get_all(db)


@router.get("/partner/{partner_id}", response_model=list[InvoiceResponse])
async def list_by_partner(partner_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await invoice_repo.get_by_partner(db, partner_id)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    invoice = await invoice_repo.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return invoice


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(data: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    return await invoice_repo.create(db, data)


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(invoice_id: uuid.UUID, data: InvoiceUpdate, db: AsyncSession = Depends(get_db)):
    invoice = await invoice_repo.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return await invoice_repo.update(db, invoice, data)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(invoice_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    invoice = await invoice_repo.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    await invoice_repo.delete(db, invoice)
