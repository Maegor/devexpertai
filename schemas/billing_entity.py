import uuid
from datetime import datetime, date

from pydantic import BaseModel


class BillingEntityCreate(BaseModel):
    partner_id: uuid.UUID
    entity_name: str
    country: str
    tax_identification_number: str | None = None
    vat_registered: bool = False
    address: str | None = None
    banking_details: str | None = None
    effective_from: date
    effective_until: date | None = None


class BillingEntityUpdate(BaseModel):
    entity_name: str | None = None
    country: str | None = None
    tax_identification_number: str | None = None
    vat_registered: bool | None = None
    address: str | None = None
    banking_details: str | None = None
    effective_from: date | None = None
    effective_until: date | None = None


class BillingEntityResponse(BaseModel):
    id: uuid.UUID
    partner_id: uuid.UUID
    entity_name: str
    country: str
    tax_identification_number: str | None
    vat_registered: bool
    address: str | None
    banking_details: str | None
    effective_from: date
    effective_until: date | None
    created_at: datetime

    model_config = {"from_attributes": True}
