import uuid
from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel

from models import InvoiceType, InvoiceStatus


class InvoiceCreate(BaseModel):
    partner_id: uuid.UUID
    billing_entity_id: uuid.UUID | None = None
    invoice_type: InvoiceType
    invoice_reference: str
    period_from: date
    period_to: date
    currency: str
    net_amount: Decimal
    vat_amount: Decimal | None = None
    gross_total: Decimal
    tax_rate: str | None = None
    pdf_path: str
    status: InvoiceStatus = InvoiceStatus.Sent
    rejection_reason: str | None = None
    scheduled_payment_date: date | None = None


class InvoiceUpdate(BaseModel):
    billing_entity_id: uuid.UUID | None = None
    invoice_type: InvoiceType | None = None
    invoice_reference: str | None = None
    period_from: date | None = None
    period_to: date | None = None
    currency: str | None = None
    net_amount: Decimal | None = None
    vat_amount: Decimal | None = None
    gross_total: Decimal | None = None
    tax_rate: str | None = None
    pdf_path: str | None = None
    status: InvoiceStatus | None = None
    rejection_reason: str | None = None
    scheduled_payment_date: date | None = None


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    partner_id: uuid.UUID
    billing_entity_id: uuid.UUID | None
    invoice_type: InvoiceType
    invoice_reference: str
    period_from: date
    period_to: date
    currency: str
    net_amount: Decimal
    vat_amount: Decimal | None
    gross_total: Decimal
    tax_rate: str | None
    pdf_path: str
    status: InvoiceStatus
    rejection_reason: str | None
    scheduled_payment_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
